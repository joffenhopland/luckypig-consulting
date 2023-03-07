import os
import secrets
import uuid

from flask import Flask,flash,request,redirect,render_template, url_for,session
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

from database import db
from UserLogin import UserLogin
from forms import RegistrerForm, LoginForm, forgetPasswordForm, UpdatePasswordForm, UpdateUserForm, resetPasswordForm, validate_password
from User import User
from classes import MultipleChoiceExercise

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

@app.route("/multiple-choice", methods=['GET', 'POST'])
def multiple_choice():
    #get the exercise from the database: to be tested when the exercises are filled in the database

    # making question and answer choices just for testing
    question = "Jeg lager mat."
    choices = ["I love food", "I made food", "I am making food", "Food is nice"]
    exerciseId =1
    if request.method == 'POST':
        exerciseId = request.form['exerciseId']              #to be changed when the course is running
        #exercise = MultipleChoiceExercise()
        #exercise.getExerciseByID(exerciseId)
        #question = exercise.question
        #choices = exercise.choices
        #right_answer = exercise.answer
        answer = request.form['answer']
        if answer == "I am making food":
            message = "Correct!"
            flash(f'Correct!', "success")
            '''#need to update user score
            exercise.number_succeed += 1
            #need to get a new exercise number from course
            #jeg tror html trenger exerciseId som hidden field i form'''
        else:
            message = "Wrong!"
            flash(f'Wrong!', "danger")
        '''exercise.number_asked += 1
        exercise.updateExercise()'''
        return render_template('multiple_choice.html', question=question, choices=choices, exerciseId=exerciseId)
    # need to get a new exercise number from course and get the new exercise
    return render_template('multiple_choice.html', question=question, choices=choices, exerciseId=exerciseId)
@ app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrerForm(request.form)
    database = db()
    if form.validate_on_submit and database.attemptedUser(form.email.data):
        flash("Epost-adressen er allerede registrert. Vennligst bruk en annen epost-adresse.", "danger")
        return render_template('register.html', form=form)
    elif form.validate_on_submit and database.usernameCheck(form.username.data):
        flash("Brukernavnet er allerede registrert. Vennligst bruk et annet brukernavn", "danger")
        return render_template('register.html', form=form)
    elif form.validate_on_submit() and database.attemptedUser(form.email.data) == False \
        and validate_password(form.password1.data) == 1 and database.usernameCheck(form.username.data) == False:
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password1.data)
        role = 1
        verificationId = str(uuid.uuid4())

        new_user = (firstname, lastname, username, email, password, role, verificationId)
        database.newUser(new_user)
        mail = Mail(app)
        msg = Message("Verifisere konto",
                      sender=app.config.get("MAIL_USERNAME"), recipients=[email])
        msg.body = "Velkommen som bruker til vår nettside. Vennligst verifisere din konto for å kunne tilgang til språkkurset."
        verification_link = url_for('verify', code=verificationId, token=app.secret_key, _external=True)
        msg.html = f'<b> Confirm email </b>' + '<a href="{}"> CONFIRM </a>'.format(verification_link)
        with app.app_context():
            mail.send(msg)
            return redirect(url_for('register_landing_page'))
    return render_template('register.html', form=form)


@ app.route('/register-landing-page', methods=["GET", "POST"])
def register_landing_page():
    message = "Tusen takk for registreringen! Vennligst sjekk din epost-konto for å verifisere din konto."
    return render_template('message_landing_page.html', message=message)


@ app.route('/verified/<code>')
def verify(code):
    database = db()
    if database.verify(code) == True:
        flash(f"Vellykket! Din konto er verifisert. Vennligst logge inn.", "success")
        return redirect(url_for('login'))
    else:
        flash(f'Verifseringen feilet...', "danger")
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
            flash(f'Det er ingen bruker som er registrert med denne eposten "{email}". Vennligst prøv igjen eller registrer ny bruker', "danger")
            return render_template('login.html', title='Logge inn',
                                   form=form)

        emailconfirmed = userlogin.emailConfirmed(email)

        if not emailconfirmed:
            return render_template('confirmemail.html')

        if userlogin.canLogIn(email, form.password.data,bcrypt):
            session["logged in"] = True
            user = userlogin.getUser(email)

            session["username"] = user.username
            session["idUser"] = user.user_id
            session["role"] = user.role
            flash(f'Du er logget inn!', "success")
            return render_template('learn.html')

        else:
            flash(f'Eposten og/eller passordet er feil. Prøv igjen!', "danger")
            return render_template('login.html', title='Loggge inn', form=form)

    else:
        return render_template('login.html', title='Logge inn', form=form)


@app.route('/forgetpassword', methods=["GET", "POST"])
def forgetpassword() -> 'html':
    form = forgetPasswordForm()
    if request.method == "POST":
        email: object = form.email.data
        database = db()
        usr = database.getUser(email)

        if not usr:
            flash(f'Det er ingen bruker som er registrert med denne eposten. Vennligst prøv igjen eller registrer ny bruker', "danger")
            return render_template('mainPage.html')

        elif usr and form.validate_on_submit():
            verificationId = str(uuid.uuid4())
            database.updateUuid(email,verificationId)
            mail = Mail(app)
            verification_link = url_for('verifyResetPassword', code=verificationId, token=app.secret_key, _external=True)

            msg = Message("Verifiserings kode: ",
                          sender=app.config.get("MAIL_USERNAME"), recipients=[email])
            msg.body = "Vennligst trykk på linken for å tilbakestill passordet ditt."
            msg.html = f'<b> Reset password </b>' + '<a href="{}"> RESET </a>'.format(verification_link)
            with app.app_context():
                mail.send(msg)
                print(msg) #todo remove
                flash(f"Link for å tilbakestille passordet ditt er sendt til eposten din.", "info")
                return render_template('mainPage.html')
    if request.method == "GET":
        return render_template('forgetpassword.html', form=form)
    
@ app.route('/verifyResetPassword/<code>')
def verifyResetPassword(code):
    database = db()
    if database.verify(code) == True:
        form = resetPasswordForm()
        form.verificationId.data = code
        return render_template('resetpassword.html',form=form)
    else:
        flash(f'Verifiseringen feilet...', "danger")
        return render_template('mainPage.html')   



@app.route('/resetpassword', methods=["GET", "POST"])
def resetpassword() -> 'html':
    form = resetPasswordForm()
    uuid = form.verificationId.data
    database = db()
    user = database.getUserByUUID(uuid)
    

    if not user:
        return render_template('message_landing_page.html', message="Ugyldig tilbakestilling passord")
    if request.method == "GET":
        message = "Vennligst tilbakestill ditt passord."
        return render_template('resetpassword.html', form=form, message=message)
    else:
        password1 = form.password1.data
        password2 = form.password2.data

        if form.validate_on_submit() and validate_password(password1) == 1:
            if password1 == password2:
                userUpdatePW = db()
                password = form.password1.data
                password_hash = bcrypt.generate_password_hash(password)
                userUpdatePW.resetPassword(uuid, password_hash)
                flash(f"vellykket! Ditt passord har blitt tilbakestilt, vennligst logge inn", "success")
                return redirect(url_for('login'))

            elif password1 != password2:
                flash(f'Passordene du skrev stemmer ikke overens. Prøv igjen!', "danger")
                return render_template('resetpassword.html', form=form)




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
            if password1==password2 and validate_password(password1) == 1:
                password_hash = bcrypt.generate_password_hash(password1)
                userUpdatePW.updateUserPassword(email,password_hash)
                message += "Passordet er oppdatert!"
                flash(f"Passordet er oppdatert!", "success")
                return render_template('viewuser.html',user=user, title="Brukerinformasjon")
            else:
                flash(f'Passordene du skrev stemmer ikke overens. Prøv igjen!', "danger")
                message += "Passordene du skrev stemmer ikke overens. Prøv igjen!"
        else:
            flash(f'Ditt gamle passord var ikke riktig. Vennligst prøv igjen!', "danger")
            message += "Ditt gamle passord var ikke riktig. Vennligst prøv igjen!"

        return render_template('updatepassword.html',user=user, title="Oppdater passord",message=message, form=form)

    return render_template('updatepassword.html', title="Oppdater", form=form, message=message)

@app.route('/viewuser', methods=["GET", "POST"])    
def viewuser() -> 'html':
    userView = UserLogin()
    email = session["email"]
    user = User(*userView.getUserByEmail(email))
    return render_template('viewuser.html',user=user, title="Brukerinformasjon")

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
        flash(f'Brukerinformasjonen er oppdatert!', "success")
        user = User(*userUpdate.getUserByEmail(email))
        return render_template('viewuser.html',user=user, title="Brukerinformasjon")

    return render_template('updateuser.html',firstname=firstname, lastname=lastname, title="Brukerinformasjon", form=form, message=message)



@app.route('/logout', methods=["GET", "POST"])
def logout() -> 'html':
    session.pop("email", None)
    session.pop("logged in", None)
    session.pop("username", None)
    session.pop("access", None)
    session.pop("idUser", None)
    session.pop("role", None)
    flash(f'Du er logget ut!', "info")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int("3000"))


