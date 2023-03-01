import os
import secrets
import uuid

from flask import Flask,flash,request,redirect,render_template, url_for
from flask_mail import Mail, Message
from database import db
from forms import RegistrerForm
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
bcrypt = Bcrypt(app)

app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_DEFAULT_SENDER'] = "kpe144@uit.no"

app.secret_key = secrets.token_urlsafe(16)

@app.route("/")
def home():
    return render_template("mainPage.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@ app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrerForm(request.form)
    database = db()
    if form.validate_on_submit and database.attemptedUser(form.email.data):
        flash("Email is already registered. Please use another email address", "danger")
        return render_template('register.html', form=form)
    if form.validate_on_submit() and database.attemptedUser(form.email.data) == False:
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password1.data)
        verificationId = str(uuid.uuid4())

        new_user = (firstname, lastname, username, email, password, verificationId)
        database.newUser(new_user)
        mail = Mail(app)
        msg = Message("Verify account",
                      sender='kpe144@uit.no', recipients=[email])
        msg.body = "Welcome as a user to our website. Please verify your account to get access to all services on our website."
        msg.html = f'<b> Confirm email </b> <a href="http://127.0.0.1:5000/verified/{verificationId}"> CONFIRM </a>'
        with app.app_context():
            mail.send(msg)
        return render_template('register_landing_page.html')
    return render_template('register.html', form=form)


@ app.route('/register-landing-page', methods=["GET", "POST"])
def register_landing_page():
    return render_template('register_landing_page')


@ app.route('/verified/<code>')
def verify(code):
    database = db()
    if database.verify(code) == True:
        flash(f"Success! You are verified, please log in", "success")
        return redirect(url_for("login"))
    else:
        flash(f'Verification failed...', "danger")
        return render_template('mainPage.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))