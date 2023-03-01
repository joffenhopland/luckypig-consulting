from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, DataRequired, Email


class RegistrerForm(FlaskForm):
    firstname = StringField(label="First name:", validators=[
                          Length(min=2, max=50), DataRequired()])
    lastname = StringField(label="Last name:", validators=[
                            Length(min=2, max=50), DataRequired()])
    username = StringField(label="Username:", validators=[
                            Length(min=6, max=50), DataRequired()])
    email = StringField(label="Email:", validators=[Email(), DataRequired()])
    password1 = PasswordField(label="Password:", validators=[
                             Length(min=8), DataRequired()])
    password2 = PasswordField(label="Repeat password:", validators=[EqualTo(
        "password1", message="Both passwords should be equal."), DataRequired()])
    submit = SubmitField(label="Register account")
