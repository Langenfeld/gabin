from flask import Flask
from flask_session import Session
from choice import Choice
import os
from guessingGabin import GuessingGabin
from menuParser import *
import logging
from voteFormGenerator import VoteFormGenerator
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, "config.ini"), encoding='utf-8')

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(
    #DEBUG = True,
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=True,
    SESSION_FILE_DIR="./sessions"
)
Session(app)

VERSION = "0.7.6"
PARSER = {"MenuStudentenwerkParser": MenuStudentenwerkParser,
          "MenuFrauenhoferParser": MenuFrauenhoferParser,
          "MenuSolarParser": MenuSolarParser,
          "FoodTruckParser": FoodTruckParser,
          "NullParser": NullParser}

choices = []
for ident, args in config.items("restaurants"):
    logging.info("Loading parser: %s (%s)"%(ident, args))
    argList = [item.strip() for item in args.split(",")]
    parserClass = PARSER[argList[1]]
    if parserClass is None:
        logging.error("No parser class found: %s"%argList[1])
        continue
    parser = parserClass(argList[2])
    choice = Choice(ident, argList[0], parser)
    choices.append(choice)


GuessingGabin.databasePath = os.path.join(BASE_DIR, config.get("misc","dbpath"))

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

voteFormGenerator = VoteFormGenerator(VERSION, choices)

@app.route('/', methods=['GET', 'POST'])
def showVoteForm():
    return voteFormGenerator.getVoteForm()

@app.route('/barchart')
def getBarChart():
    return voteFormGenerator.getBarChart()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(config.get("misc", "port")), threaded=True)
