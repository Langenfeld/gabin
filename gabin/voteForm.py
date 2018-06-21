from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, RadioField, SelectMultipleField, widgets

class VoteForm():

    def consumeVote(self, form):

    def generateVoteForm(selected: dict):
        class VoteForm(Form):
            pass

        for choice in CHOICES:
            setattr(VoteForm, choice.id,
                    RadioField(choice.name,
                               choices=[("0", "no"), ("1", "may"), ("2", "want")],
                               validators=[validators.required()],
                               default=selected[choice.id] if choice.id in selected else "1",
                               )
                    )

        return VoteForm(request.form)




