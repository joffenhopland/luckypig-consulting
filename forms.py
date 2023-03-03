from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, HiddenField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError
from flask import flash
import re


class RegistrerForm(FlaskForm):

    def validate_password (form, field):
        password = field.data

        if len(password) < 8:
            flash(f"Passordet må inneholde minst 8 tegn.", "danger")
        elif not re.search(r'[A-Z]', password):
            flash( "Passordet må inneholde minst en stor bokstav", "danger")
        elif not re.search(r'[a-z]', password):
            flash("Passordet må inneholde minst en liten bokstav", "danger")
        elif not re.search(r'[0-9]', password):
            flash("Passordet må inneholde minst et tall", "danger")
        elif not re.search(r'[@$!%*?&.]', password):
            flash("Passordet må inneholde minst et spesialtegn", "danger")


    firstname = StringField(label="Fornavn:", validators=[
                          Length(min=2, max=50), DataRequired()])
    lastname = StringField(label="Etternavn:", validators=[
                            Length(min=2, max=50), DataRequired()])
    username = StringField(label="Brukernavn:", validators=[
                            Length(min=6, max=50), DataRequired()])
    email = StringField(label="Epost:", validators=[Email(), DataRequired()])
    password1 = PasswordField(label="Passord:", validators=[
                              DataRequired(), validate_password])
    password2 = PasswordField(label="Gjenta passord:", validators=[EqualTo(
        "password1", message="Begge passordene må være identiske."), DataRequired()])
    submit = SubmitField(label="Registrere en bruker")

"""
class UpdatePasswordForm(FlaskForm):
    oldpassword = PasswordField("Old password", validators=[DataRequired()])
    password1 = PasswordField("New password", validators=[DataRequired()])
    password2 = PasswordField("Repeat new password", validators=[DataRequired()])

    update = SubmitField("Change password")
"""

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])

    login = SubmitField(label="Logge inn")

class forgetPasswordForm(FlaskForm):
    email = EmailField("Epost", validators=[DataRequired(), Email()])
    submit = SubmitField("Send")

class resetPasswordForm(FlaskForm):
    verificationId = HiddenField(validators=[DataRequired()])
    password1 = PasswordField("Nytt passord", validators=[DataRequired()])
    password2 = PasswordField("Bekrefte nytt passord", validators=[DataRequired()])

    submit = SubmitField("Endre passord")


class UpdateUserForm(FlaskForm):
    firstname = StringField("Fornavn", validators=[DataRequired()])
    lastname = StringField("Etternavn", validators=[DataRequired()])
    username = StringField("Brukernavn", validators=[DataRequired()])

    update = SubmitField("Oppdater")

class UpdatePasswordForm(FlaskForm):
    oldpassword = PasswordField("Gammelt passord", validators=[DataRequired()])
    password1 = PasswordField("Nytt passord", validators=[DataRequired()])
    password2 = PasswordField("Gjenta nytt passord", validators=[DataRequired()])

    update = SubmitField("Endre passord")


