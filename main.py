import os
import secrets
import uuid

from flask import Flask,flash,request,redirect,render_template, url_for,session
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

from database import db
from UserLogin import UserLogin
from forms import RegistrerForm, LoginForm, forgetPasswordForm, UpdatePasswordForm, UpdateUserForm, resetPasswordForm
from User import User

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
bcrypt = Bcrypt(app)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'luckypig2023@gmail.com',
    "MAIL_PASSWORD":'iskbnfrukwlvwjfk'
}

app.config.update(mail_settings)
mail = Mail(app)

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
                      sender=app.config.get("MAIL_USERNAME"), recipients=[email])
        msg.body = "Welcome as a user to our website. Please verify your account to get access to all services on our website."
        verification_link = url_for('verify', code=verificationId, token=app.secret_key, _external=True)
        msg.html = f'<b> Confirm email </b>' + '<a href="{}"> CONFIRM </a>'.format(verification_link)
        with app.app_context():
            mail.send(msg)
            flash(f"Success! Your account is verified. Please log in", "success")
        # return redirect(url_for('register_landing_page'))
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@ app.route('/register-landing-page', methods=["GET", "POST"])
def register_landing_page():
    message = "Thank you for registering! Please check your email to verify your account"
    return render_template('message_landing_page.html', message=message)


@ app.route('/verified/<code>')
def verify(code):
    database = db()
    if database.verify(code) == True:
        flash(f"Success! You are verified. Please log in", "success")
        return redirect(url_for('login'))
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
            flash(f'There is no user registered with the email {email}. Please try again or register', "danger")
            return render_template('login.html', title='Log in',
                                   message="There is no user registered with the email {}, please try again or register".format(
                                       email), form=form)

        emailconfirmed = userlogin.emailConfirmed(email)

        if not emailconfirmed:
            return render_template('confirmemail.html')

        if userlogin.canLogIn(email, form.password.data,bcrypt):
            session["logged in"] = True
            user = userlogin.getUser(email)

            session["username"] = user.username
            session["idUser"] = user.user_id
            session["role"] = user.role
            flash(f'You are logged in!', "success")
            return render_template('learn.html')

        else:
            flash(f'The email or password you wrote was wrong. Try again', "danger")
            return render_template('login.html', title='Log in',
                                   message="The email or password you wrote was wrong. Try again", form=form)

    else:
        flash(f'Login failed', "danger")
        return render_template('login.html', title='Log in', form=form, message="Login failed")


@app.route('/forgetpassword', methods=["GET", "POST"])
def forgetpassword() -> 'html':
    form = forgetPasswordForm()
    if request.method == "POST":
        email: object = form.email.data
        database = db()
        usr = database.getUser(email)

        if not usr:
            flash(f'We have no user registered with this email...', "danger")
            return render_template('mainPage.html')

        elif usr and form.validate_on_submit():
            verificationId = str(uuid.uuid4())
            database.updateUuid(email,verificationId)
            mail = Mail(app)
            verification_link = url_for('verifyResetPassword', code=verificationId, token=app.secret_key, _external=True)

            msg = Message("Verification code: ",
                          sender=app.config.get("MAIL_USERNAME"), recipients=[email])
            msg.body = "Welcome as a user to our website. Please clik the link to reset your password ."
            msg.html = f'<b> Reset password </b>' + '<a href="{}"> RESET </a>'.format(verification_link)
            with app.app_context():
                mail.send(msg)
                print(msg) #todo remove
                message = "Please follow the link we have just sent you to reset your password"
                return render_template('message_landing_page.html',message=message)
    if request.method == "GET":
        return render_template('forgetpassword.html', form=form)
    
@ app.route('/verifyResetPassword/<code>')
def verifyResetPassword(code):
    database = db()
    if database.verify(code) == True:
        form = resetPasswordForm()
        form.verificationId.data = code
        flash(f"Success!", "success")
        return render_template('resetpassword.html',form=form)
    else:
        flash(f'Verification failed...', "danger")
        return render_template('mainPage.html')   



@app.route('/resetpassword', methods=["GET", "POST"])
def resetpassword() -> 'html':
    form = resetPasswordForm()
    uuid = form.verificationId.data
    database = db()
    user = database.getUserByUUID(uuid)
    

    if not user:
        return render_template('message_landing_page.html', message="Invalid reset link")
    if request.method == "GET":
        message = "Please reset your password"
        return render_template('resetpassword.html', form=form, message=message)
    else:
        password1 = form.password1.data
        password2 = form.password2.data

        if form.validate_on_submit():
            if password1 == password2:
                userUpdatePW = db()
                password = form.password1.data
                password_hash = bcrypt.generate_password_hash(password)
                userUpdatePW.resetPassword(uuid, password_hash)
                flash(f"Success! Your password has been reset, please log in", "success")
                return redirect(url_for('login'))

            elif password1 != password2:
                message = "The two new passwords you wrote do not match. Try again"
                return render_template('resetpassword.html', form=form, message=message)




@app.route('/updatepassword', methods=["GET", "POST"])    
def updatepassword() -> 'html':
    userUpdatePW = UserLogin()
    email = session["email"]
    user = User(*userUpdatePW.getUserByEmail(email))
    form = UpdatePasswordForm()
    message=""

    if form.validate_on_submit():
        oldpassword = form.oldpassword.data
        if userUpdatePW.canLogIn(email, oldpassword,bcrypt):
            password1=form.password1.data
            password2=form.password2.data
            if password1==password2:
                password_hash = bcrypt.generate_password_hash(password1)
                userUpdatePW.updateUserPassword(email,password_hash)
                message += "Password updated!"
                return render_template('message_landing_page.html', message=message)
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
    user = User(*userView.getUserByEmail(email))
    return render_template('viewuser.html',user=user, title="User details")

@app.route('/updateuser', methods=["GET", "POST"])    
def updateuser() -> 'html':
    userUpdate = UserLogin()
    email = session["email"]
    user = User(*userUpdate.getUserByEmail(email))
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
        session["username"] = username
        message = "User info updated!"
        return render_template('message_landing_page.html', message=message)

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

