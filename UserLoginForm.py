from wtforms import StringField, SubmitField, EmailField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm

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

    login = SubmitField("Log in")

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
