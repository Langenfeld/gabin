from typing import List

from flask import render_template, request, session
from wtforms import Form, validators, RadioField
from datetime import date
from choice import Choice
from guessingGabin import GuessingGabin


class VoteFormGenerator:

    def __init__(self, version: str, choices: List[Choice]):
        self.choices = choices
        self.version = version
        self.votesDate = "INIT"
        self.individualVotes = {}


    def getVoteForm(self):
        # values
        nowDate = date.today().strftime("%d.%m.%Y")
        self.resetVotes(nowDate)
        guessingG = GuessingGabin()
        # prepare
        if "choice" in session and session["date"] == nowDate:
            form = self.generateVoteForm(session["choice"])
        else:
            form = self.generateVoteForm({})
        # form.choice.choices = [choice.getAsTupleWithMenu(nowDate) for choice in CHOICES if choice.enabled]
        # save choice
        choiceMade = False
        if request.method == 'POST' and form.validate():
            choices = {choice.ident: getattr(form, choice.ident).data for choice in self.choices}
            session["choice"] = choices
            session["date"] = nowDate
            choiceMade = True
            self.individualVotes[session.sid] = choices
            guessingG.logFinalResult(self.choices, nowDate)
            guessingG.commit()
            self.updateVoteCount()
        values = {"votingOpen": True, "version": self.version, "theDay": nowDate, "choiceMade": choiceMade}
        # prepare Webpage
        menu = {choice.ident: choice.getMenu(nowDate) for choice in self.choices if choice.getHasOpened()}
        menuEntries = [(choice.ident, choice.menuParser.url) for choice in self.choices if choice.getHasOpened()]
        history = guessingG.getHistoricVotes(self.choices)
        return render_template('form.html', form=form, values=values, menu=menu, menuEntries=menuEntries,
                               history=history)

    def generateVoteForm(self, selected: dict):
        class VoteForm(Form):
            pass

        for choice in self.choices:
            setattr(VoteForm, choice.ident,
                    RadioField(choice.name,
                               choices=[("0", "no"), ("1", "may"), ("2", "want")],
                               validators=[validators.required()],
                               default=selected[choice.ident] if choice.ident in selected else "1",
                               )
                    )

        return VoteForm(request.form)

    def getBarChart(self):
        values = {"choices": self.choices}
        return render_template('bar.html', values=values)

    def updateVoteCount(self):
        for choice in self.choices:
            choice.countVotes(self.individualVotes)

    def resetVotes(self, nowDate):
        if self.votesDate != nowDate:
            self.individualVotes = {}
            self.updateVoteCount()
            self.votesDate = nowDate