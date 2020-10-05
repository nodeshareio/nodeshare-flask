from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, SelectField, validators, ValidationError, HiddenField, DecimalField
from wtforms.fields.html5 import DateField


class NodeForm(FlaskForm):
    title = StringField('Node Title: ', [validators.DataRequired(), validators.Length(min=1, max=120)])
    description = StringField('Description: ', [validators.DataRequired(), validators.Length(min=1, max=250)])
    data = TextAreaField('Data: ', [validators.DataRequired(), validators.Length(min=1, max=1000)])
    submit = SubmitField('Submit')


