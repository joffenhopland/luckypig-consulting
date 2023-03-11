import os
import secrets
import uuid
import itertools
import random

from flask import Flask,flash,request,redirect,render_template, url_for,session
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

from database import db
from UserLogin import UserLogin
from forms import RegistrerForm, LoginForm, forgetPasswordForm, UpdatePasswordForm, UpdateUserForm, resetPasswordForm, validate_password
from User import User
import json
from classes import Exercise

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
    database = db()
    #Er det er kurs registrert på denne personen? 0 hvis ikke, courseId hvir ja
    course_status = database.course_status(session["idUser"])
    return render_template("learn.html", course_status = course_status)


@app.route("/course", methods=['GET', 'POST'])
def course():
    database = db()
    course_status = request.arg.get("course_status")
    questions = request.arg.get("questions")

    #new course
    if course_status == False:
        theme = 1 # request.arg.get("theme") #todo - sett dropdown tema lik 1 (kokk), 2 (bilmekaniker) eller 3 (finans)
        language = 1
        
        #Vi lager et nytt active course for brukeren
        database.initiate_course(session["idUser"])
        #Vi henter id for det nye kurset
        course_status = database.course_status(session["idUser"])
        #Vi setter ny course_status for det kurset
        database.new_course_status(theme, language, course_status)
        questions = None
        return url_for("course", course_status = course_status, questions = questions)

    #existing course - user returns or new course
    if course_status and not questions: 
        level = 1 #todo - hente fra DB eller annet
        allQuestions = (database.get_new_questions(level, theme))
        #gjør tuple om til list
        allQuestionslst = list(itertools.chain(*allQuestions))
        question_done = (database.get_questions_done(course_status))
        #Gjør tuple om til list
        question_donelst = list(itertools.chain(*question_done))
        #Henter ut alle spørsmål brukeren ikke har gjort
        questions = [x for x in allQuestions if x not in question_donelst]
        #Setter spørsmålene i tilfeldig rekkefølge
        random.shuffle(questions)

        #Henter første oppgaveid, first er for å se hvilken oppgavetype det der. Sender videre for sjekk
        id = questions[0]
        first = int(str(id)[0])
        checknumber(first, questions)
    
    #existing course - user submit question
    if course_status and questions:
        
        id = questions[0]
        first = int(str(id)[0])
        checknumber(first, questions)
    
    
    #user has done alle questions in one level and successrate is good
    if course_status == 1 and len(questions) == 0 and database.success_rate(): 
        flash(f'Gratulerer, du har oppnådd nok poeng til å nå neste level', "success")
        return url_for("home")
    
    #user has done alle questions in one level and successrate is NOT good
    if course_status == 1 and len(questions) == 0 and database.success_rate(): 
        flash(f'Gratulerer, du har oppnådd nok poeng til å nå neste level', "success")
        return url_for("home")
    
def checknumber(id, questions):
    if id == 1:
        return redirect(url_for("multiple_choice", questions = questions))
    elif id == 3:
        return redirect(url_for("drop_down", questions = questions))
    elif id == 5:
        return redirect(url_for("drag_and_drop", questions = questions))


@app.route("/multiple-choice", methods=['GET', 'POST'])
def multiple_choice():
    #Her må dere ta i mot listen og pop ut (hente ut og fjern) oppgaveId

    #get the exercise from the database: to be tested when the exercises are filled in the database

    # making question and answer choices just for testing
    # question = "Jeg lager mat."
    # choices = ["I love food", "I made food", "I am making food", "Food is nice"]
    exerciseId = 3003
    if request.method == 'POST':
        exerciseId = request.form['exerciseId']              #to be changed when the course is running
        exercise = Exercise(exerciseId,3)
        exercise.getExercise()
        print(f'exercise: {exercise}')
        question = exercise.question
        print(f'question: {question}')
        choices = exercise.choices
        print(f'choices: {choices}')
        right_answer = exercise.answer
        answer = request.form['answer']
        #if answer == "I am making food":
        if answer == right_answer:
            flash(f'Correct!', "success")
            exercise.number_succeed += 1
            exercise.score
            # need to update user score
            # get current score from course_status
            # add exercise.score to the current score
            # write new score to active_course

        else:
            flash(f'Wrong!', "danger")
        exercise.number_asked += 1
        exercise.updateExercise()
        return render_template('multiple_choice.html', question=question, choices=choices, exerciseId=exerciseId)
    # need to get a new exercise number from course and get the new exercise
    exerciseId
    print(f'exerciseId: {exerciseId}')
    exercise = Exercise(exerciseId, 3)
    exercise.getExercise()
    print(f'exercise: {exercise.exerciseID}')
    question = exercise.question
    print(f'question: {question}')
    choices = exercise.choices
    print(f'choices: {choices}')
    return render_template('multiple_choice.html', question=question, choices=choices, exerciseId=exerciseId)

@app.route('/drag_and_drop', methods=["GET", 'POST'])
def drag_and_drop() -> 'html':
    question = "Jeg like eple."
    dragdrop = [{"id": 3, "text": "apple"}, {"id": 1, "text": "I"}, {"id": 2, "text": "like"}]

    if request.method == 'POST':
        correct_answer = [q["id"] for q in dragdrop]
        correct_answer.sort()
        order = [int(q) for q in request.form.getlist('answer')[0].split(',')]
        new_dragdrop = []
        for item in order:
            for elem in dragdrop:
                if elem['id'] == item:
                    new_dragdrop.append(elem)

        if order == correct_answer:
            flash(f'Correct!', "success")

        else:
            flash(f'Wrong!', "danger")
        return render_template('drag_and_drop.html', dragdrop=new_dragdrop, question=question)

    return render_template('drag_and_drop.html', dragdrop=dragdrop, question=question)


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
            flash(f'Eposten og/eller passordet er feil. Prøv igjen!', "danger")
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


