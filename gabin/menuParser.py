import re
from typing import List

from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import logging


class MenuParser:

    ERRORSTRINGS = ["Kein Speisenplan vorhanden",
                    "kein Speisenplan vorhanden",
                    "Es liegt aktuell kein Plan",
                    "Brückentag ",
                    "Geschlossen",
                    "-- kein Eintrag --"]

    def __init__(self, url):
        self.url = url
        self.lastUpdate = "NEVER"
        self.menu = []
        self.open = True
        self.lastCheck = "NEVER"
        self.t = 0

    def getMenu(self) -> list:
        return self.menu

    def updateMenu(self, nowDate: str):
        if self.lastUpdate != nowDate:
            try:
                menuDataRaw = self._updateMenu()
                self.menu = MenuParser.getValidMenu(menuDataRaw)
                if len(self.menu) < len(menuDataRaw):
                    logging.warning("Menu not parsable (%s): %s"%(type(self), str(menuDataRaw)))
                else:
                    self.lastUpdate = nowDate
            except Exception as e:
                logging.warning(e)


    def _updateMenu(self) -> List[str]:
        return ["-"]

    @staticmethod
    def getValidMenu(menu: List[str]) -> list:
        return [item for item in menu if len(item.strip()) >= 7 and not MenuParser.isErrorString(item)]

    @staticmethod
    def isErrorString(item: str) -> bool:
        for errorString in MenuParser.ERRORSTRINGS:
            if item.startswith(errorString):
                return True
        return False


class MenuFrauenhoferParser(MenuParser):

    def _updateMenu(self) -> list:
        request = requests.get(self.url)
        soup = BeautifulSoup(request.content, "html.parser")
        result1 = soup.find(class_=self.constructClass(1))
        result2 = soup.find(class_=self.constructClass(2))
        return [r.text for r in [result1,result2] if r is not None]

    def constructClass(self, no):
        d = date.today().strftime("%d.%m.%Y")
        d = d.replace(".","_")
        d = d+"-menu"+str(no)
        return d


class MenuStudentenwerkParser(MenuParser):

    days=["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

    def _updateMenu(self) -> list:
        request = requests.get(self.url)
        content = request.text.replace("<br/>", " <br/> ").replace("<br>", ", ")
        soup = BeautifulSoup(content, "html.parser")
        result = soup.find("h3", text=self.constructHeading())
        parent = result.parent
        menuItems = parent.findAll(class_="menu-info")
        menu = []
        for item in menuItems:
            menu.append(item.text.split("Kennz")[0].split("enthält Allergene:")[0].replace("<br>", "  ").strip())
        return menu

    def constructHeading(self):
        wd = datetime.today().weekday()
        dayName = MenuStudentenwerkParser.days[wd]
        d = date.today().strftime("%d.%m.")
        return dayName + " " + d

class FoodTruckParser(MenuParser):

    def _updateMenu(self) -> list:
        now = datetime.now()
        if now.hour < 2:
            raise Exception("Too early to read food trucks.")
        self.open = False
        request = requests.get(self.url)
        soup = BeautifulSoup(request.content, "html.parser")
        dateItems = [r.parent for r in soup.findAll(class_="date", text=re.compile(r'^Heute.*'))]
        tfResults = []
        for dateItem in dateItems:
            tfResults.extend([r.parent.parent for r in #todo: class_="location",
                              dateItem.findAll(text=re.compile(r'^Technische Fakultät.*'))])
            tfResults.extend([r.parent.parent for r in #todo: class_="location",
                              dateItem.findAll(text=re.compile(r'^LUNCHTIME @Techn. Fakultät Fr.*'))])
        trucks = []
        for tfResult in tfResults:
            temp = tfResult.find(class_="truck")
            if temp != None:
                trucks.append(temp.text)
                trucks.append(temp.text)
                self.open = True
        return trucks

class NullParser(MenuParser):

    def getMenu(self) -> list:
        return []

    def updateMenu(self, nowDate: str):
        pass