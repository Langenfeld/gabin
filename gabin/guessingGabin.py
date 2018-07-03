from datetime import date
from difflib import SequenceMatcher
from sqlite3 import connect
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)

class GuessingGabin:

    databasePath = "default.db"
    lastRequest = None
    historyCache = []

    """
    c.execute("CREATE TABLE votes (menu, date, no, may, yes)")
    c.execute("CREATE TABLE userVotes (menu, session, date, no, may, yes))
    """
    def __init__(self):
        self.databasePath = GuessingGabin.databasePath
        self.connection = connect(self.databasePath)
        self.cursor = self.connection.cursor()

    def logFinalResult(self, choices: list, nowDate: str):
        try:
            for item in choices:
                for menu in item.getMenu():
                    if len(self.cursor.execute("""SELECT * FROM votes WHERE menu=? AND date=?""",
                                      (menu, nowDate)).fetchall()) > 0:
                        self.cursor.execute(
                            """UPDATE votes SET no=?, may=?, yes=? WHERE menu=? AND date=?""",
                            (item.no, item.maybe, item.yes, menu ,nowDate)
                        )
                    else:
                        self.cursor.execute(
                            """INSERT INTO votes VALUES (?,?,?,?,?)""",
                            (menu , nowDate, item.no, item.maybe, item.yes)
                        )
        except Exception as e:
            logging.error(e)

    def getHistoricVotes(self, choices: list) -> list:
        nowDate = date.today()
        results = []
        if nowDate != GuessingGabin.lastRequest:
            logging.info("Requesting database for old choices...")
            GuessingGabin.lastRequest = nowDate
            try:
                dateString = nowDate.strftime("%d.%m.%Y")
                result = self.cursor.execute("""SELECT * FROM votes WHERE date!=(?) ORDER BY date(date)""", (dateString,))
                rows = result.fetchall()
                for item in choices:
                    for menu in item.getMenu():
                        for row in rows:
                            diff = SequenceMatcher(None, menu, row[0])
                            if diff.ratio() > 0.9:
                                results.append(row)
                            if len(results) >= 10:
                                GuessingGabin.historyCache = results
                                return results
            except Exception as e:
                logging.error(e)
        else:
            return GuessingGabin.historyCache
        logging.info("Old Choices loaded...")
        GuessingGabin.historyCache = results
        return results

    def commit(self):
        try:
            self.connection.commit()
        except Exception as e:
            logging.error(e)