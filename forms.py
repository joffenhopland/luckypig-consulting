from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, HiddenField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError
from flask import flash
import re


class RegistrerForm(FlaskForm):

    def validate_password (form, field):
        password = field.data

        if len(password) < 8:
            flash(f"The password must contain at least 8 characters", "danger")
        elif not re.search(r'[A-Z]', password):
            flash( "The password must contain at least one uppercase letter", "danger")
        elif not re.search(r'[a-z]', password):
            flash("The password must contain at least one lowercase letter", "danger")
        elif not re.search(r'[0-9]', password):
            flash("The password must contain at least one digit", "danger")
        elif not re.search(r'[@$!%*?&.]', password):
            flash("The password must contain at least one special character", "danger")


    firstname = StringField(label="First name:", validators=[
                          Length(min=2, max=50), DataRequired()])
    lastname = StringField(label="Last name:", validators=[
                            Length(min=2, max=50), DataRequired()])
    username = StringField(label="Username:", validators=[
                            Length(min=6, max=50), DataRequired()])
    email = StringField(label="Email:", validators=[Email(), DataRequired()])
    password1 = PasswordField(label="Password:", validators=[
                              DataRequired(), validate_password])
    password2 = PasswordField(label="Repeat password:", validators=[EqualTo(
        "password1", message="Both passwords should be equal."), DataRequired()])
    submit = SubmitField(label="Register account")

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

    login = SubmitField(label="Log in")

class forgetPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

class resetPasswordForm(FlaskForm):
    verificationId = HiddenField(validators=[DataRequired()])
    password1 = PasswordField("New password", validators=[DataRequired()])
    password2 = PasswordField("Confirm new password", validators=[DataRequired()])

    submit = SubmitField("RESET")


class UpdateUserForm(FlaskForm):
    firstname = StringField("First name", validators=[DataRequired()])
    lastname = StringField("Last name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])

    update = SubmitField("Update info")

class UpdatePasswordForm(FlaskForm):
    oldpassword = PasswordField("Old password", validators=[DataRequired()])
    password1 = PasswordField("New password", validators=[DataRequired()])
    password2 = PasswordField("Repeat new password", validators=[DataRequired()])

    update = SubmitField("Change password")


