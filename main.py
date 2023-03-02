import os
import secrets
import uuid

from flask import Flask,flash,request,redirect,render_template, url_for, session
from flask_mail import Mail, Message
from database import db
from forms import RegistrerForm
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from UserLogin import UserLogin
from UserLoginForm import LoginForm, forgetPasswordForm, UpdatePasswordForm, UpdateUserForm

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
bcrypt = Bcrypt(app)

app.config['MAIL_SERVER'] = 'smtpserver.uit.no'
app.config['MAIL_PORT'] = 587

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
                      sender='csk044@uit.no', recipients=[email])
        msg.body = "Welcome as a user to our website. Please verify your account to get access to all services on our website."
        msg.html = f'<b> Confirm email </b> <a href="http://127.0.0.1:5000/verified/{verificationId}"> CONFIRM </a>'
        with app.app_context():
            mail.send(msg)
            flash(f"Success! You are verified, please log in", "success")
        return render_template('register_landing_page.html')
    return render_template('register.html', form=form)


@ app.route('/register-landing-page', methods=["GET", "POST"])
def register_landing_page():
    return render_template('register_landing_page.html')


@ app.route('/verified/<code>')
def verify(code):
    database = db()
    if database.verify(code) == True:
        flash(f"Success! You are verified, please log in", "success")
        return render_template('mainPage.html')
    else:
        flash(f'Verification failed...', "danger")
        return render_template('mainPage.html')
    
@app.route('/login', methods=["GET", "POST"])
def login() -> 'html':
    form = LoginForm()

    if form.validate_on_submit():
        print()
        session["email"] = form.email.data
        email = session["email"]
        userlogin = UserLogin()

        if not userlogin.isUser(email):
            return render_template('login.html', title='Log in',
                                   message="There is no user registered with the email {}, please try again or register".format(
                                       email), form=form)

        emailconfirmed = userlogin.emailConfirmed(email)
        emailconfirmed=0

        if not emailconfirmed:
            return render_template('confirmemail.html')

        if userlogin.canLogIn(email, form.password.data):
            print("login!")

            session["logged in"] = True
            user = userlogin.getUser(email)

            session["username"] = user.username
            session["idUser"] = user.user_id
            session["role"] = user.role
            return render_template('login_landing_page.html', user=user)

        else:

            return render_template('login.html', title='Log in',
                                   message="The email or password you wrote was wrong. Try again", form=form)

    else:
        return render_template('login.html', title='Log in', form=form)


@app.route('/forgetpassword', methods=["GET", "POST"])
def forgetpassword() -> 'html':
    form = forgetPasswordForm()

    if request.method == "GET":
        return render_template('forgetpassword.html', form=form)

    else:
        try:
            with UserLogin() as db:
                email: object = form.email.data
                usr = db.getUser(email)

        except AttributeError:
            message = "There was a problem with the database connection. Please try again later."
            return render_template('forgetpassword.html', form=form, message=message)

        if usr:
            if request.method == "POST" and form.validate():
                password1 = form.password1.data
                password2 = form.password1.data

                if password1 == password2:
                    password1 = form.password1.data
                    password_hash = generate_password_hash(password1)
                    usr.updateUserPassword(email, password_hash)
                    return redirect(url_for('login.html'))

                else:
                    message = "The two new passwords you wrote do not match. Try again"
                    return render_template('forgetpassword.html', form=form, message=message, email=form.email.data)

        else:
            message = "You are not a user yet. Please sign up!"
            render_template('sign_up.html', title="Sign up", form=form, message=message)



@app.route('/updatepassword', methods=["GET", "POST"])    
def updatepassword() -> 'html':
    userUpdatePW = UserLogin()
    email = session["email"]
    user = userUpdatePW.getUser(email)   
    form = UpdatePasswordForm()
    message=""

    if form.validate_on_submit():
        oldpassword = form.oldpassword.data
        if userUpdatePW.canLogIn(email, oldpassword):
            password1=form.password1.data
            password2=form.password2.data
            if password1==password2:
                #password_hash = generate_password_hash(password1)--------------------------------------------to be changed to hash password!!!!
                password_hash = password1
                userUpdatePW.updateUserPassword(email,password_hash)
                message += "Password updated!"
                return render_template('info_updated_landing_page.html', message=message)
            else:
                message += "The two new passwords you wrote do not match. Try again"
        else:
            message += "Your old password was not correct. Please try again"

        return render_template('updatepassword.html',user=user, title="Update password",message=message, form=form)

    return render_template('updatepassword.html', title="Update password", form=form, message=message)

@app.route('/viewuser', methods=["GET", "POST"])    
def viewuser() -> 'html':
    userView = UserLogin()
    email = session["email"]
    user = userView.getUser(email)   
    return render_template('viewuser.html',user=user, title="User details")

@app.route('/updateuser', methods=["GET", "POST"])    
def updateuser() -> 'html':
    userUpdate = UserLogin()
    email = session["email"]
    user = userUpdate.getUser(email)   
    firstname=user.firstname
    lastname=user.lastname
    username = user.username
    form = UpdateUserForm(firstname=firstname,lastname=lastname,username=username)
    message=""

    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        email = session["email"]
        userUpdate.updateUser(firstname,lastname,username, email)
        user = userUpdate.getUser(email)   
        session["username"] = username
        message = "User info updated!"
        print(user.firstname)
        return render_template('info_updated_landing_page.html', title="Update user details", message=message)

    return render_template('updateuser.html',firstname=firstname, lastname=lastname, title="User details", form=form, message=message)



@app.route('/logout', methods=["GET", "POST"])
def logout() -> 'html':
    session.pop("email", None)
    session.pop("logged in", None)
    session.pop("username", None)
    session.pop("access", None)
    session.pop("idUser", None)
    session.pop("role", None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))