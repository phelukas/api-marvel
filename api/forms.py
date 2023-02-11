from wtforms import Form, StringField, TextAreaField, BooleanField, validators
from wtforms_sqlalchemy.fields import QuerySelectMultipleField


class FormTeamAdd(Form):
    name = StringField('Nome do Time', validators=[validators.DataRequired()])
    
