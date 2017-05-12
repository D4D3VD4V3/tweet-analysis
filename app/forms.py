from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class HashtagForm(FlaskForm):
    hashtag = StringField("Enter a hashtag", [DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Go!")
