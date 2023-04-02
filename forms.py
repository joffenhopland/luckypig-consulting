from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, HiddenField, RadioField, SelectField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError, Optional
from flask import flash
import re


class RegistrerForm(FlaskForm):
    firstname = StringField(label="Fornavn:", validators=[
                          Length(min=2, max=50), DataRequired()])
    lastname = StringField(label="Etternavn:", validators=[
                            Length(min=2, max=50), DataRequired()])
    username = StringField(label="Brukernavn:", validators=[
                            Length(min=6, max=50), DataRequired()])
    email = StringField(label="Epost:", validators=[Email(), DataRequired()])
    password1 = PasswordField(label="Passord:", validators=[
                              DataRequired()])
    password2 = PasswordField(label="Gjenta passord:", validators=[EqualTo(
        "password1", message="Begge passordene må være identiske."), DataRequired()])
    submit = SubmitField(label="Registrere en bruker")

def validate_password (password):
        if len(password) < 8:
            flash(f"Passordet må inneholde minst 8 tegn.", "danger")
            return 0
        elif not re.search(r'[A-Z]', password):
            flash( "Passordet må inneholde minst en stor bokstav", "danger")
            return 0
        elif not re.search(r'[a-z]', password):
            flash("Passordet må inneholde minst en liten bokstav", "danger")
            return 0
        elif not re.search(r'[0-9]', password):
            flash("Passordet må inneholde minst et tall", "danger")
            return 0
        elif not re.search(r'[@$!%*?&.]', password):
            flash("Passordet må inneholde minst et spesialtegn", "danger")
            return 0
        else:
            return 1

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

class ReportForm(FlaskForm):
    report_type = RadioField('Rapporttype', choices=[('user_reports', 'Brukerrapporter'), ('difficult_tasks', 'Rapport over vanskelige oppgaver')], validators=[DataRequired()])
    user_reports_sort = RadioField('Sorter på', choices=[('global', 'Globalt'), ('group', 'Gruppe'), ('single_user', 'Enkeltbruker')], validators=[Optional()])
    user_reports_sort_teacher = RadioField('Sorter på', choices=[('group', 'Gruppe'), ('single_user', 'Enkeltbruker')],
                                   validators=[Optional()])
    difficult_tasks_sort = RadioField('Sorter på', choices=[('global', 'Globalt'), ('group', 'Gruppe')], validators=[Optional()])
    difficult_tasks_sort_teacher = RadioField('Sorter på', choices=[('group', 'Gruppe')],
                                      validators=[Optional()])
    global_sort = RadioField('Velg sortering', choices=[('theme', 'Tema'), ('level', 'Nivå'), ('all', 'Alle')], validators=[Optional()])
    group_sort = RadioField('Velg sortering', choices=[('level', 'Nivå'),('all', 'Alle')], validators=[Optional()])

    groupID = SelectField('GruppeID', coerce=int, validators=[Optional()])
    userID = SelectField('BrukerID', coerce=int, validators=[Optional()])
    theme = SelectField('Velg tema', choices=[(None, '-'), ('1', 'Kokk'), ('2', 'Bilmekaniker'), ('3', 'Finans')],validators=[Optional()])
    level = SelectField('Velg nivå', choices=[(None, '-'), ('1', 'Bronse'), ('2', 'Sølv'), ('3', 'Gull')],validators=[Optional()])
    submit = SubmitField('Generer rapport')
