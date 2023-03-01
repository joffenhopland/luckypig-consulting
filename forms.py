from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError
import re




class RegistrerForm(FlaskForm):

    def validate_password (form, field):
        password = field.data

        if len(password) < 8:
            raise ValidationError("The password must contain at least 8 characters")
        if not re.search(r'[A-Z]', password):
            raise ValidationError( "The password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError("The password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', password):
            raise ValidationError("The password must contain at least one digit")
        if not re.search(r'[@$!%*?&.]', password):
            raise ValidationError("The password must contain at least one special character")


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


