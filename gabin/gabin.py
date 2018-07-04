from flask import Flask
from flask.ext.session import Session
from choice import Choice
import os
from guessingGabin import GuessingGabin
from menuParser import NullParser, MenuFrauenhoferParser, MenuStudentenwerkParser, FoodTruckParser
import logging
from voteFormGenerator import VoteFormGenerator

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(
    # DEBUG = True,
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=True,
    SESSION_FILE_DIR="./sessions"
)
Session(app)

VERSION = "0.7.6"
CHOICES = [Choice("mensa", "Mensa",
                  MenuStudentenwerkParser("https://www.swfr.de/essen-trinken/speiseplaene/mensa-flugplatz/")),
           Choice("solar", "SolarCasino", MenuFrauenhoferParser("https://kantine.ise.fraunhofer.de/sic/menu-sic/")),
           Choice("ise", "ISE", MenuFrauenhoferParser("https://kantine.ise.fraunhofer.de/heidenhof/menu-heidenhof/")),
           Choice("foodtruck", "Food Truck", FoodTruckParser(
               "http://www.foodtrucks-deutschland.de/trucks/stadt/freiburg-liste-tour-daten-termine-aktuell")),
           Choice("baecker", "Bäcker", NullParser(""))]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GuessingGabin.databasePath = os.path.join(BASE_DIR, "gabinHistory.db.demo")

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

voteFormGenerator = VoteFormGenerator(VERSION, CHOICES)

@app.route('/', methods=['GET', 'POST'])
def showVoteForm():
    return voteFormGenerator.getVoteForm()

@app.route('/barchart')
def getBarChart():
    return voteFormGenerator.getBarChart()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
