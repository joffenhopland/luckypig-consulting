import random
import secrets
import uuid
import itertools
import random
import pandas as pd
import os
from dotenv import load_dotenv

from flask import Flask, flash, request, redirect, render_template, url_for, session, Markup, jsonify
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

from classes import DragAndDropService
from database import db
from UserLogin import UserLogin
from forms import RegistrerForm, LoginForm, forgetPasswordForm, UpdatePasswordForm, UpdateUserForm, resetPasswordForm, \
    validate_password, ReportForm, CreateGroupForm, CreateContestForm, SearchForm, ChooseRoleForm
from User import User
import json
from classes import Exercise, Dropdown, Group

import json
import urllib.parse

from datetime import datetime, timedelta

load_dotenv()  # load environment variables from .flaskenv file


app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
bcrypt = Bcrypt(app)
app.config['PERMANENT_SESSION_LIFETIME'] = 25200 #7 days
app.config['SESSION_COOKIE_SECURE'] = False #set to true when app is live
app.config['SESSION_COOKIE_SAMESITE'] = "Lax" 
app.config['SESSION_COOKIE_HTTPONLY'] = True


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'luckypig2023@gmail.com',
    "MAIL_PASSWORD": 'cjhfysvonlfcegwm'
    # "MAIL_USERNAME": os.environ.get("MAIL_USERNAME"),
    # "MAIL_PASSWORD": os.environ.get("MAIL_PASSWORD")
}

app.config.update(mail_settings)
mail = Mail(app)

app.secret_key = secrets.token_urlsafe(16)

@app.route("/")
def home():
    return render_template("mainPage.html")

@app.route("/theme")
def theme():
    database = db()
    themeId = int(request.args.get("themeId"))
    #the user has just logged in and the program get the active and inactive (not started) courses
    if themeId == -1:
        userThemes = database.getUserThemes(session["idUser"])
        themes = database.getThemes()
        inactiveThemes = [theme for theme in themes if theme not in userThemes]
        return render_template("theme.html", userThemes = userThemes, inactiveThemes = inactiveThemes)

    # the user has choosen the theme
    else:
        #the user changes the theme (from dropdown choice or from innlogging)
        if session["themeId"] != themeId:
            session["courseId"] = -1
            session["level"] = 1
            session["themeId"] = themeId
            session["init_course"] = 1
            session["new_level"] = 0
            return redirect(url_for("course", fromTheme = 1))
        else:
            return redirect(url_for("learn"))


@app.route("/learn")
def learn():
    #open the learn page (home page for course) with the right parameters (totalPoints, login_streak, theme)
    database = db()
    totalPoints = database.getTotalPoints(session["idUser"])
    login_streak = database.get_login_streak(session["idUser"])
    themeId = session["themeId"]
    checklevel()
    return render_template("learn.html", total_points = totalPoints, themeId = themeId, login_streak=login_streak, level=session['level_name'])


@app.route("/course", methods=['GET', 'POST'])
def course():
    #manage the progress the progress of the course
    database = db()
    fromTheme = request.args.get("fromTheme")
    questions = session["questions"]

    #find existing course or create if None.
    if session["courseId"] == -1:
        session["courseId"] = database.getCourseIdByUserIdAndTheme(session["idUser"], session['themeId'])

        #create a new course because user starts a new theme or a new level inside the same theme
        if session["courseId"] == None or session["new_level"] == 1:
            session["new_level"] = 0
            #vi lager en ny kurs
            createANewCourse(database)

        session["level"] = database.get_level(session["courseId"])

        #if existing course is done, go to next level and create a new course. Go to learn page
        if database.checkCourseDone(session["courseId"]) == 1:
            session["level"] += 1

            if session["level"] < 4:
                createANewCourse(database)
            return redirect(url_for("learn"))

        session["questions"] = []

        #user has just logged in or changed them, then go to learn page, otherwise start the course
        if fromTheme:
            return redirect(url_for("learn"))
        else:
            return redirect(url_for("course"))




    # start course and get all the undone questions for the course
    if session["courseId"] > -1 and len(questions) == 0 and session["init_course"] == 1:

        level_points = database.get_level_points(session["courseId"])
        session["level_points"] = level_points
        database.update_levelpoints(session["courseId"], level_points)
        session["init_course"] = 0
        info = database.get_level_theme(session["courseId"])

        theme = info[1]
        session["level"] = info[0]

        allQuestions = (database.get_new_questions(session["level"], theme))
        allQuestionslst = list(itertools.chain(*allQuestions))

        question_done = (database.get_questions_done(session["courseId"]))
        question_donelst = list(itertools.chain(*question_done))

        questions = [x for x in allQuestionslst if x not in question_donelst]
        random.shuffle(questions)
        session["questions"] = questions

        #if all questions are done, send a message to the user
        if len(session["questions"]) == 0:
            flash(f'Du har gjort alle oppgavene', "success")
            return redirect(url_for("learn"))

        #otherwise get the first exercise in the exercises list
        session["exerciseId"] = session["questions"].pop(0)
        first = int(str(session["exerciseId"])[0])
        view = checknumber(first)
        checklevel()
        return redirect(url_for(view))

    # course started - user go to the next question
    if session["courseId"] > -1 and len(questions) > 0:

        if len(session["questions"]) == 0:
            flash(f'Du har gjort alle oppgavene', "success")
            return redirect(url_for("learn"))

        session["exerciseId"] = session["questions"].pop(0)
        first = int(str(session["exerciseId"])[0])
        view = checknumber(first)
        checklevel()
        
        return redirect(url_for(view))

    # user has done alle questions in one level and successrate is good
    if session["courseId"] > -1 and len(questions) == 0 and database.success_rate(session["courseId"]):
        database.delete_question_done(session["courseId"])

        #user go to the next level
        if session["level"] < 4:
            level = session["level"]
            level += 1
            session["level"] = level
            #Set the course as done
            database.setCourseDone(session["courseId"])

            #prepare to start a new course for the new level
            session["courseId"] = -1
            session["init_course"] = 1
            session["new_level"] = 1
            if session["level"] < 4:
                flash(f'Gratulerer, du har oppnådd nok poeng til å nå neste level', "success")
                return redirect(url_for("learn"))
            else:
                flash(f'Gratulerer, du har oppnådd gull og dermed fullført språkkurset!', "success")
                return redirect(url_for("learn"))

    # user has done alle questions in one level and successrate is NOT good
    if session["courseId"] > -1 and len(questions) == 0 and database.success_rate(session["courseId"]) == False:
        #user stay in the same level and must do all the questions again
        level_points = 0
        database.update_levelpoints(session["courseId"], level_points)
        database.delete_question_done(session["courseId"])
        session["init_course"] = 1
        flash(f'Du har dessverre ikke klart nok oppgaver og må gjøre nivået på nytt', "danger")
        return redirect(url_for("learn"))
    return redirect(url_for("learn"))

def createANewCourse(database):
    # create a new course
    database.initiate_course(session["idUser"])
    # get the courseId
    session["courseId"] = database.course_status(session["idUser"])
    # create a new course status for this course
    database.new_course_status(session["themeId"], session["language"], session["courseId"], session["level"])

def checknumber(id):
    #return the type of exercise
    if id == 1:
        return "dropdown"
    elif id == 3:
        return "multiple_choice"
    elif id == 5:
        return "drag_and_drop"

def checklevel():
    #return the name of the level
    if session["level"] == 1:
        session["level_name"] = "Bronse"
    elif session["level"] == 2:
        session["level_name"] = "Sølv"
    elif session["level"] >= 3:
        session["level_name"] = "Gull"


@app.route("/skipExercise", methods=['GET'])
def skipExercise():
    #skip the exercise
    database = db()
    success = 0
    database.question_done(session['exerciseId'], success, session["level"], session["courseId"])
    database.question_history(session['exerciseId'], success, session["level"], session["courseId"])

    return redirect(url_for("course"))

@app.route("/multiple-choice", methods=['GET', 'POST'])
def multiple_choice():
    #Mulitple choice exercise: show the exercise and check the answer
    database = db()
    #get the exerciseId
    exerciseId = session['exerciseId']

    #Check the user's answer and update the database accordingly
    if request.method == 'POST':
        exercise = Exercise(exerciseId, 3)
        exercise.getExercise()
        question = exercise.question
        choices = exercise.choices
        right_answer = exercise.answer
        answer = request.form['answer']

        if answer == right_answer:
            flash(f'Korrekt', "success")
            exercise.number_succeed += 1
            success = 1
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            database.question_history(exerciseId, success, session["level"], session["courseId"])

            # Increase users current level points
            level_points = database.get_level_points(session["courseId"])
            level_points += 1
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], session["level_points"])
        else:
            flash(Markup(f"Du svarte feil. Riktig svar er:  {right_answer}"), "danger")
            success = 0
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            database.question_history(exerciseId, success, session["level"], session["courseId"])
        
        exercise.number_asked += 1
        exercise.updateExercise()
        return render_template('multiple_choice.html', question=question, choices=choices, level_name=session["level_name"], level_points=session["level_points"])

    #get the exercise text (question + choices) and show it to the user
    exercise = Exercise(exerciseId, 3)
    exercise.getExercise()
    question = exercise.question
    choices = exercise.choices
    return render_template('multiple_choice.html', question=question, choices=choices, level_name=session["level_name"], level_points=session["level_points"])

@app.route('/dropdown', methods=['GET', 'POST'])
def dropdown():
    #Dropdown exercise: show the exercise and check the answer

    database = db()
    #get the exerciseId
    exerciseId = session['exerciseId']

    #Check the user's answer and update the database accordingly
    if request.method == 'POST':
        exercise = Dropdown(exerciseId, 1)
        exercise.getExercise()
        norwegian_question = exercise.question
        english_question = exercise.question_translated
        choices = exercise.choices
        right_answer = exercise.answer
        answer = request.form['answer']

        if answer == right_answer:
            flash(f'Korrekt!', "success")
            exercise.number_succeed += 1
            success = 1
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            database.question_history(exerciseId, success, session["level"], session["courseId"])
            # Increase users current level points
            level_points = database.get_level_points(session["courseId"])
            level_points += 1
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], session["level_points"])

        else:
            flash(Markup(f"Du svarte feil. Riktig svar er:  {right_answer}"), "danger")
            success = 0
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            database.question_history(exerciseId, success, session["level"], session["courseId"])

            # flash(f'Sorry, that is wrong. The answer was "{right_answer}".', "danger")
        exercise.number_asked += 1
        exercise.updateExercise()
            #to remove indicators of placement for the dropdown manu
        blank_placeholders = '{ blank }', '{blank}'
        for blank_placeholder in blank_placeholders:
            if blank_placeholder in english_question:
            # identify the position of the placeholder
                placeholder_index = english_question.find(blank_placeholder)
        return render_template('dropdown.html', choices=choices, nortext=norwegian_question, text=english_question, placeholder_index=placeholder_index, level_name=session["level_name"], level_points=session["level_points"])

    #get the exercise text (question + choices) and show it to the user
    exercise = Dropdown(exerciseId, 1)
    exercise.getExercise()
    norwegian_question = exercise.question
    english_question = exercise.question_translated
    choices = exercise.choices    
        #to remove indicators of placement for the dropdown manu
    blank_placeholders = '{ blank }', '{blank}'
    for blank_placeholder in blank_placeholders:
        if blank_placeholder in english_question:
        # identify the position of the placeholder
            placeholder_index = english_question.find(blank_placeholder)
    return render_template('dropdown.html', choices=choices, nortext=norwegian_question, text=english_question, placeholder_index=placeholder_index, level_name=session["level_name"], level_points=session["level_points"])



dragAndDropService = DragAndDropService()

@app.route('/drag-and-drop', methods=["GET", 'POST'])
def drag_and_drop():
    #Drag and drop exercise: show the exercise and check the answer

    database = db()
    #get the exerciseId
    exerciseId = session['exerciseId']

    #Check the user's answer and update the database accordingly
    if request.method == 'POST':
        exercise = dragAndDropService.getExercise(exerciseId)
        question = exercise.question
        choices = exercise.choices
        right_answer = exercise.answer
        order = [int(q) for q in request.form.getlist('answer')[0].split(',')]
        new_dragdrop = []
        user_answer = []
        for item in order:
            for elem in exercise.choices:
                if elem['id'] == item:
                    new_dragdrop.append(elem)
                    user_answer.append(elem['text'])


        if " ".join(user_answer) == right_answer:
            flash(f'Korrekt!', "success")
            exercise.number_succeed += 1
            success = 1
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            database.question_history(exerciseId, success, session["level"], session["courseId"])
            # Increase users current level points
            level_points = database.get_level_points(session["courseId"])
            level_points += 1
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], session["level_points"])
        else:
            flash(Markup(f"Du svarte feil. Riktig svar er:  {right_answer}"), "danger")
            success = 0
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            database.question_history(exerciseId, success, session["level"], session["courseId"])
        exercise.number_asked += 1
        exercise.updateExercise()
        return render_template('drag_and_drop.html', dragdrop=new_dragdrop, question=question, exerciseId=exerciseId, level_name=session["level_name"], level_points=session["level_points"])
    
    #get the exercise text (question + choices) and show it to the user
    exercise = dragAndDropService.getExercise(exerciseId)
    question = exercise.question
    choices = exercise.choices
    random.shuffle(choices)
    order = []
    for choice in choices:
        order.append(choice['id'])
    return render_template('drag_and_drop.html', dragdrop=choices, question=question, exerciseId=exerciseId, level_name=session["level_name"], level_points=session["level_points"],order=order)




@ app.route('/register', methods=["GET", "POST"])
def register():
    #New user joins the platform
    form = RegistrerForm(request.form)
    database = db()
    #Checks forms and checks if the email exist in the system
    if form.validate_on_submit and database.attemptedUser(form.email.data):
        flash("Epost-adressen er allerede registrert. Vennligst bruk en annen epost-adresse.", "danger")
        return render_template('register.html', form=form)
    #Checks forms and checks if the username exist in the system
    elif form.validate_on_submit and database.usernameCheck(form.username.data):
        flash("Brukernavnet er allerede registrert. Vennligst bruk et annet brukernavn", "danger")
        return render_template('register.html', form=form)
    #Form is ok, email dont exist, password meets requirements and unique username. New user in database
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
        #Insert new user into database
        database.newUser(new_user)
        #Mail for verify user
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
    #Simple landing page after registration is complete. Ask to verify acount.
    message = "Tusen takk for registreringen! Vennligst sjekk din epost-konto for å verifisere din konto."
    return render_template('message_landing_page.html', message=message)


@ app.route('/verified/<code>')
def verify(code):
    #When user press link in mail for verify. We check that is exist and set verify = true in database.
    database = db()
    if database.verify(code) == True:
        flash(f"Vellykket! Din konto er verifisert. Vennligst logge inn.", "success")
        return redirect(url_for('login'))
    else:
        flash(f'Verifseringen feilet...', "danger")
        return render_template('mainPage.html')


@app.route('/login', methods=["GET", "POST"])
def login() -> 'html':
    #login
    database = db()
    form = LoginForm()

    #user sends login info
    if form.validate_on_submit():
        print()
        session["email"] = form.email.data
        email = session["email"]
        userlogin = UserLogin()

        #user gives wrong email or password
        if not userlogin.isUser(email):
            flash(f'Eposten og/eller passordet er feil. Prøv igjen!', "danger")
            return render_template('login.html', title='Logge inn',
                                   form=form)

        emailconfirmed = userlogin.emailConfirmed(email)

        #user has not confirmed by email
        if not emailconfirmed:
            return render_template('confirmemail.html')

        #user gives the right info to login so session is initiated
        if userlogin.canLogIn(email, form.password.data,bcrypt):
            session["logged in"] = True
            user = userlogin.getUser(email)

            session["username"] = user.username
            session["idUser"] = user.user_id
            session["role"] = user.role
            session["language"] = 1
            session["courseId"] = -1
            session["themeId"] = -1
            session["level"] = 1
            session["questions"] = []
            session["exerciseId"] = 0
            session["init_course"] = 1
            session["new_level"] = 0
            session["level_name"] = ""
            checklevel()

            # check last login and update last login and login streak
            last_login_date = user.last_login
            login_streak = user.login_streak
            if last_login_date != None:
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                if last_login_date == yesterday:
                    login_streak += 1
                    new_login_date = today.strftime("%Y-%m-%d")
                    database.update_user_last_login_login_streak(user.user_id, new_login_date, login_streak)
                else:
                    login_streak = 1
                    new_login_date = today.strftime("%Y-%m-%d")
                    database.update_user_last_login_login_streak(user.user_id, new_login_date, login_streak)
            else:
                login_streak = 1
                today = datetime.now().date()
                new_login_date = today.strftime("%Y-%m-%d")
                database.update_user_last_login_login_streak(user.user_id, new_login_date, login_streak)

            flash(f'Du er logget inn!', "success")
            return redirect(url_for('theme', themeId = session["themeId"]))

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
                database = db()
                total_points = database.getTotalPoints(session["idUser"])
                return render_template('viewuser.html', user=user, title="Brukerinformasjon",total_points=total_points, level=session['level_name'], role=session['role'])

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
    database = db()
    total_points = database.getTotalPoints(session["idUser"])
    login_streak = database.get_login_streak(session["idUser"])
    checklevel()
    if database.checkGoldLevelCompleted(session['idUser'], session['themeId']):
        completedLevel = 1
    else:
        completedLevel = 0
    return render_template('viewuser.html', user=user, title="Brukerinformasjon",total_points=total_points, level=session['level_name'], role=session['role'], login_streak=login_streak,themeId = session['themeId'], completedLevel = completedLevel)

@app.route('/updateuser', methods=["GET", "POST"])    
def updateuser() -> 'html':
    #user wants to change his contact informations
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
        database = db()
        total_points = database.getTotalPoints(session["idUser"])
        return render_template('viewuser.html',user=user, title="Brukerinformasjon",total_points=total_points, level=session['level_name'], role=session['role'])

    return render_template('updateuser.html',firstname=firstname, lastname=lastname, title="Brukerinformasjon", form=form, message=message)


@app.route('/logout', methods=["GET", "POST"])
def logout() -> 'html':
    session.pop("email", None)
    session.pop("logged in", None)
    session.pop("username", None)
    session.pop("access", None)
    session.pop("idUser", None)
    session.pop("role", None)
    session.pop("courseId", None)
    session.pop("questions", None)
    session.pop("exerciseId", None)
    session.pop("language", None)
    session.pop("themeId", None)
    session.pop("level", None)
    session.pop("init_course", None)
    session.pop("new_level", None)
    flash(f'Du er logget ut!', "info")
    return redirect(url_for('home'))

@app.route('/change_role', methods=["GET", "POST"])
def change_role() -> 'html':
    form = SearchForm(request.form)
    role_form = ChooseRoleForm([])

    if request.method == 'POST':
        if 'form-submit' in request.form:  # search-form submission
            if form.validate_on_submit():
                database = db()
                search = form.search.data
                all_users = database.search_user(search)
                role_form = ChooseRoleForm([(user[1], user[0]) for user in all_users])
                return render_template('change_role.html', form=form, role_form=role_form, allusers=all_users)

        elif 'role_form-submit' in request.form:  # role-form submission
            new_role = role_form.role.data
            database = db()
            userId = request.form.get('user')
            print(f'Changing role for user {userId} to {new_role}')
            database.update_user_role(new_role, userId)
            return redirect(url_for('change_role'))

    return render_template("change_role.html", allusers=[], form=form, role_form=role_form)


@app.route('/change_role_submit', methods=['POST'])
def change_role_submit():
    if request.method == 'POST':
        return jsonify({'status': 'success'})

@app.route('/reportgeneration', methods=["GET", "POST"])
def reportgeneration() -> 'html':
    database = db()
    themeId = session["themeId"]

    if session["role"] == 3:

        form = ReportForm()

        groups =[(0,"-")]
        groupDB = database.get_group()
        if groupDB is not None:
            for group in groupDB:
                groups.append((group[0],str(group[0]) + " - " + group[1]))
        form.groupID.choices = groups

        users =[(0,"-")]
        userDB = database.getAllUser()
        if userDB is not None:
            for user in userDB:
                users.append((user[0],str(user[0]) + " - " + user[1]))
        form.userID.choices = users

        if form.validate_on_submit():
            report_type = form.report_type.data
            groupID = form.groupID.data
            theme = form.theme.data
            level = form.level.data
            userID = form.userID.data
            print(f"Admin report: report-type: {report_type}, groupID: {groupID} theme: {theme}, level: {level},userID: {userID}")
            url = url_for('report', report_type=report_type, groupID= groupID, theme=theme, level=level, userID=userID)
            return redirect(url)
        return render_template('reportgeneration_admin.html', form=form, themeId=themeId)

    elif session["role"] == 2:

        form = ReportForm()
        teacher_userID = session["idUser"]

        groups =[(0,"-")]
        groupDB = database.get_group(teacher_userID)
        if groupDB is not None:
            for group in groupDB:
                groups.append((group[0],str(group[0]) + " - " + group[1]))
        form.groupID.choices = groups

        users = [(0, "-")]
        userDB = database.get_users_teacher(teacher_userID)
        if userDB is not None:
            for user in userDB:
                users.append((user[0],str(user[0]) + " - " + user[1]))
        form.userID.choices = users

        if form.validate_on_submit():
            report_type = form.report_type.data
            groupID = form.groupID.data
            theme = form.theme.data
            level = form.level.data
            userID = form.userID.data
            url = url_for('report', report_type=report_type, groupID=groupID, theme=theme, level=level, userID=userID)
            return redirect(url)
        return render_template('reportgeneration_teacher.html', form=form, themeId=themeId)
    else:
        return render_template("learn.html")
@app.route('/report')
def report():
    database = db()
    report_type = request.args.get('report_type')
    role = session["role"]
    groupID = request.args.get('groupID')
    theme = request.args.get('theme')
    level = request.args.get('level')
    userID = request.args.get('userID')

    if userID == "0":
        userID = None
    if groupID == "0":
        groupID = None
    if level == "None":
        level = None
    if theme == "None":
        theme = None

    if role == 2:
        teacher_userID = session["idUser"]
    else:
        teacher_userID = None

    headers = []
    resultTable = []
    if report_type == "user_reports":
        headers, resultTable = database.user_view(role, teacher_userID, groupID, theme, userID, level)
    elif report_type == "difficult_tasks":
        headers, resultTable = database.all_tasks_report_view(role, 10, teacher_userID, groupID, theme, level)
    else:
        print("Error, no valid report type selected")

    df = pd.DataFrame(data=resultTable,columns=headers)
    styled_table = df.style.hide_index().set_table_attributes('class="table table-bordered"')
    html_table = styled_table.to_html()
    return render_template("report.html", table=html_table)

@app.route('/viewgroup', methods=["GET", "POST"])
def viewgroup() -> 'html':
    #return an overview of the user's list of groups
    database = db()
    DBgroups = database.getGroups(session["idUser"])
    groups = [Group(*(DBgroup)) for DBgroup in DBgroups]
    classes = []
    friendgroups = []
    for group in groups:
        #chek role (Admin/Medlem) in group
        if group.adminId == session['idUser']:
            group.role = "Admin"

        #check group type (class/friendgroup) and append to the appropriate list
        if group.groupTypeId == 1:
            classes.append(group)
        elif group.groupTypeId == 2:
            friendgroups.append(group)
    return render_template('viewgroup.html', title="Mine grupper",classes=classes, friendgroups=friendgroups, role=session['role'])

@app.route('/creategroup', methods=["GET", "POST"])
def creategroup() -> 'html':
    #create a new group
    form = CreateGroupForm()

    #user send info of the new group and the database is updated
    if request.method == 'POST':
        database = db()
        names = database.getAllGroupName()
        groupName = form.name.data

        #check if the group name is already in use
        if groupName in names:
            flash(f'Gruppenavnet finnes allerede. Velg et nytt gruppenavn', "danger")
            return render_template('creategroup.html', form=form)

        #create the group
        else:
            groupAdminId = session["idUser"]
            if session["role"] == 1:
                groupe_typeId = 2
            else:
                groupe_typeId = 1

            database.createGroup(groupName,groupAdminId,groupe_typeId)
            return redirect(url_for('viewgroup'))

    else:
        return render_template('creategroup.html', form=form)

@app.route('/leaderboard')
def leaderboard():
    database = db()
    global_leaderboard = database.get_leaderboard()
    return render_template('leaderboard.html', global_leaderboard=global_leaderboard)

@app.route('/leaderboard-group')
def leaderboard_group():
    database = db()
    user_id = session["idUser"]
    groups_for_user = database.get_groups_for_user(user_id)

    group_leaderboards = []
    for group in groups_for_user:
        groupId, groupName = group
        leaderboard = database.get_group_leaderboard(groupId)
        print (leaderboard)
        group_leaderboards.append({
           'group_name': groupName,
           'group_id': groupId,
           'leaderboard': leaderboard })

    return render_template('leaderboard_group.html', leaderboards=group_leaderboards)

@app.route('/contest_result')
def contest_result():
    #show the contest result and update the database
    database = db()
    points = session["contest_points"]
    leaderboardPoints = database.getLeaderboardPoints(session["idUser"], session['group_id'])
    if leaderboardPoints == None:
        database.createLeaderboardPoints(session["idUser"], session['group_id'], points)
    else:
        totalPoints = points + int(leaderboardPoints[0])
        database.updateLeaderboardPoints(session["idUser"], session['group_id'], totalPoints)
    groupDB = database.getGroupInfo(session['group_id'])
    group = Group(*(groupDB))
    # chek role (Admin/Medlem) in group
    if group.adminId == session['idUser']:
        group.role = "Admin"

    return render_template('contest_result.html', points=points, group=group)

@app.route('/createcontest', methods=["GET", "POST"])
def createcontest() -> 'html':
    group_id = session["group_id"]
    database = db()
    group_name = database.get_group_name(group_id)
    form = CreateContestForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form.get('name')
        time = request.form.get('time')
        selected_questions = request.form.get('selected_questions').split(",")
        
        date = datetime.now().date() + timedelta(days=int(time))
        deadline_date = date.strftime("%Y-%m-%d")
        
        database.add_contest(group_id=group_id ,name=name, deadline_date=deadline_date, selected_questions = selected_questions)
        return redirect(url_for('active_contests'))
    else:
        print(form.errors)
        return render_template('create_contest.html', form=form, group_name=group_name)
    
@app.route('/active_contests')
def active_contests() -> 'html':
    group_id = session["group_id"]
    user_id = session["idUser"]
    database = db()
    active_contests, not_active_contests = database.get_all_contests(group_id, user_id)

    groupDB = database.getGroupInfo(session['group_id'])
    group = Group(*(groupDB))
    # chek role (Admin/Medlem) in group
    if group.adminId == session['idUser']:
        group.role = "Admin"

    return render_template('active_contests.html', active_contests=active_contests, not_active_contests=not_active_contests, group=group)

@app.route('/get_dynamic_data', methods=['POST'])
def get_dynamic_data():
    question_type = request.form.get('question_type', '', type=str)
    level = request.form.get('level', '', type=int)
    theme = request.form.get('theme', '', type=int)
    database = db()
    questions = database.getQuestionsForContest(question_type, level,theme)
    return jsonify(questions)

@app.route('/admin_group', methods=["GET", "POST"])
def admin_group() -> 'html':
    database = db()
    form = SearchForm(request.form)
    groupId = request.args.get('groupId')
    if groupId != None:
        access = database.check_group_id_access(admin_user_id=session["idUser"])
        if int(groupId) in access: 
            session["group_id"] = groupId
        else:
            print("User does not have access to this group")
            return url_for('viewgroup')
    else:
        groupId = session["group_id"]
        
    groupName = database.get_group_name(groupId)
    memberId = request.args.get("id")
    accept = bool(request.args.get("accept"))
    add = request.args.get('add')
    userId = request.args.get('userId')
    delete = request.args.get("delete")
    delete_group = request.args.get("deletegroup")

        
    if memberId:
        #admin has accept or declines invitation
        memberId = int(memberId)
        database.answer_invite_request_group_member(groupId, memberId, accept)
        invites = database.get_invite_request_group_member(groupId)
        members = database.get_group_members(groupId)
        return render_template('admin_group.html', name=groupName, invites=invites, groupId=groupId, members = members)
    
    elif add:
        #Admin added a member from user list
        all_users = database.all_user_name_memberinvitation(groupId)
        invites = database.get_invite_request_group_member(groupId)
        members = database.get_group_members(groupId)
        return render_template('admin_group.html', name=groupName, invites=invites, groupId=groupId, members = members, allusers = all_users, form=form)
    
    elif userId:
        #Adds the user 
        database.add_group_member(groupId, userId)
        members = database.get_group_members(groupId)
        invites = database.get_invite_request_group_member(groupId)
        all_users = database.all_user_name_memberinvitation(groupId)
        return render_template('admin_group.html', name=groupName, invites=invites, groupId=groupId, members = members, allusers = all_users, form=form)
    
    elif delete:
        #deletes a member from the member-list
        print("delete -----------")
        database.remove_group_member(groupId, delete)
        members = database.get_group_members(groupId)
        invites = database.get_invite_request_group_member(groupId)
        return render_template('admin_group.html', name=groupName, invites=invites, groupId=groupId, members = members)
    
    elif delete_group:
        #Delete the group
        database.delete_group(delete_group)
        return url_for('viewgroup')
    
    elif request.method == 'POST' and form.validate_on_submit():
        #Search for user in database
        search = form.search.data
        members = database.get_group_members(groupId)
        invites = database.get_invite_request_group_member(groupId)
        all_users = database.search_user(search)
        return render_template('admin_group.html', name=groupName, invites=invites, groupId=groupId, members = members, form=form, allusers = all_users)

    else:
        invites = database.get_invite_request_group_member(groupId)
        members = database.get_group_members(groupId)
        return render_template('admin_group.html', name=groupName, invites=invites, groupId=groupId, members = members)


@app.route('/member_group', methods=["GET", "POST"])
def member_group() -> 'html':
    #to get an overview of the selected group
    #user can invite people, see the contests, create new contest or leave the group
    database = db()
    form = SearchForm(request.form)

    #check the groupId
    groupId = request.args.get('groupId')
    if groupId != None:
        access = database.check_group_id_access(member_user_id=session["idUser"])
        if int(groupId) in access: 
            session["group_id"] = groupId
        else:
            print("User does not have access to this group")
            return url_for('viewgroup')
    else:
        groupId = session["group_id"]
    groupName = database.get_group_name(groupId)
    invite = request.args.get('invite')
    userId = request.args.get('userId')
    leave = request.args.get("leave")

    # Member invite another member from user list
    if invite:
        all_users = database.all_user_name_memberinvitation(groupId)
        members = database.get_group_members(groupId)
        return render_template('member_group.html', name=groupName, groupId=groupId, members=members,
                               allusers=all_users, form=form)

    # Member invite another member from user list
    elif userId:
        database.invite_request_group_member(groupId,userId)
        members = database.get_group_members(groupId)
        all_users = database.all_user_name_memberinvitation(groupId)
        return render_template('member_group.html', name=groupName, groupId=groupId, members=members, allusers=all_users, form=form)

    # leave the group
    elif leave:
        print("leave -----------")
        database.remove_group_member(groupId, session["idUser"])
        return redirect(url_for('viewgroup'))

    #finish with invite members
    elif request.method == 'POST' and form.validate_on_submit():
        search = form.search.data
        members = database.get_group_members(groupId)
        all_users = database.search_user(search)
        return render_template('member_group.html', name=groupName, groupId=groupId, members=members, form=form, allusers=all_users)

    #create or see contests
    else:
        members = database.get_group_members(groupId)
        return render_template('member_group.html', name=groupName, groupId=groupId, members=members)


@app.route('/participate_contest', methods=["GET", "POST"])
def participate_contest() -> 'html':
    #participate to contest
    start = request.args.get('start')
    terminate = request.args.get('terminate')
    contestId = request.args.get('contestId')
    database = db()

    #start contest and get the exercises list
    if start:
        #get the list of exercises from the database
        session["contest_exercises"] = database.getAllContestExercises(contestId)
        session["contest_points"] = 0
        #set contest as done
        database.setContestDone(session['idUser'], contestId,session["group_id"])

        if len(session["contest_exercises"]) == 0:
            flash("Konkurransen har ingen oppgave", "danger")
            return redirect(url_for('participate_contest', terminate=1))
        return redirect(url_for('participate_contest'))

    # start contest and get the exercises list
    if terminate:
        print(f'Total result: {session["contest_points"]}')
        return redirect(url_for('contest_result'))

    #go to the next exercise
    elif len(session["contest_exercises"]) > 0:
        session["exerciseId"] = session["contest_exercises"].pop(0)
        first = int(str(session["exerciseId"])[0])
        view = checknumber(first) + "_contest"
        return redirect(url_for(view))

    #contest is done and go to the result side
    else:
        return redirect(url_for('contest_result'))



@app.route("/multiple-choice_contest", methods=['GET', 'POST'])
def multiple_choice_contest():
    #Mulitple exercise for contest: show the exercise and check the answer

    database = db()
    #get the exerciseId
    exerciseId = session['exerciseId']

    #Check the user's answer and update the database accordingly
    if request.method == 'POST':
        exercise = Exercise(exerciseId, 3)
        exercise.getExercise()
        question = exercise.question
        choices = exercise.choices
        right_answer = exercise.answer
        answer = request.form['answer']

        if answer == right_answer:
            flash(f'Korrekt', "success")
            exercise.number_succeed += 1
            #success = 1
            #database.question_history(exerciseId, success, session["level"], session["courseId"])

            # Increase users current contest points
            session["contest_points"] += 1
        else:
            flash(Markup(f"Du svarte feil. Riktig svar er:  {right_answer}"), "danger")
            #success = 0
            #database.question_history(exerciseId, success, session["level"], session["courseId"])

        exercise.number_asked += 1
        exercise.updateExercise()
        return render_template('multiple_choice_contest.html', question=question, choices=choices)

    #get the exercise text (question + choices) and show it to the user
    exercise = Exercise(exerciseId, 3)
    exercise.getExercise()
    question = exercise.question
    choices = exercise.choices
    return render_template('multiple_choice_contest.html', question=question, choices=choices)

@app.route('/dropdown_contest', methods=['GET', 'POST'])
def dropdown_contest():
    #Dropdown exercise for contest: show the exercise and check the answer

    database = db()
    #get the exerciseId
    exerciseId = session['exerciseId']

    #Check the user's answer and update the database accordingly
    if request.method == 'POST':
        exercise = Dropdown(exerciseId, 1)
        exercise.getExercise()
        norwegian_question = exercise.question
        english_question = exercise.question_translated
        choices = exercise.choices
        right_answer = exercise.answer
        answer = request.form['answer']

        if answer == right_answer:
            flash(f'Korrekt!', "success")
            exercise.number_succeed += 1
            #success = 1
            #database.question_history(exerciseId, success, session["level"], session["courseId"])

            # Increase users current contest points
            session["contest_points"] += 1
        else:
            flash(Markup(f"Du svarte feil. Riktig svar er:  {right_answer}"), "danger")
            #success = 0
            #database.question_history(exerciseId, success, session["level"], session["courseId"])

        exercise.number_asked += 1
        exercise.updateExercise()
        # to remove indicators of placement for the dropdown manu
        blank_placeholders = '{ blank }', '{blank}'
        for blank_placeholder in blank_placeholders:
            if blank_placeholder in english_question:
                # identify the position of the placeholder
                placeholder_index = english_question.find(blank_placeholder)
        return render_template('dropdown_contest.html', choices=choices, nortext=norwegian_question,
                               text=english_question, placeholder_index=placeholder_index)

    #get the exercise text (question + choices) and show it to the user
    exercise = Dropdown(exerciseId, 1)
    exercise.getExercise()
    norwegian_question = exercise.question
    english_question = exercise.question_translated
    choices = exercise.choices
    # to remove indicators of placement for the dropdown manu
    blank_placeholders = '{ blank }', '{blank}'
    for blank_placeholder in blank_placeholders:
        if blank_placeholder in english_question:
            # identify the position of the placeholder
            placeholder_index = english_question.find(blank_placeholder)
    return render_template('dropdown_contest.html', choices=choices, nortext=norwegian_question, text=english_question,
                           placeholder_index=placeholder_index)

dragAndDropService = DragAndDropService()

@app.route('/drag-and-drop_contest', methods=["GET", 'POST'])
def drag_and_drop_contest():
    #Drag and drop exercise for contest: show the exercise and check the answer

    database = db()
    #get the exerciseId
    exerciseId = session['exerciseId']

    #Check the user's answer and update the database accordingly
    if request.method == 'POST':
        exercise = dragAndDropService.getExercise(exerciseId)

        question = exercise.question
        right_answer = exercise.answer
        order = [int(q) for q in request.form.getlist('answer')[0].split(',')]
        new_dragdrop = []
        user_answer = []
        for item in order:
            for elem in exercise.choices:
                if elem['id'] == item:
                    new_dragdrop.append(elem)
                    user_answer.append(elem['text'])

        if " ".join(user_answer) == right_answer:
            flash(f'Korrekt!', "success")
            exercise.number_succeed += 1
            #success = 1
            #database.question_history(exerciseId, success, session["level"], session["courseId"])

            # Increase users current contest points
            session["contest_points"] += 1
        else:
            flash(Markup(f"Du svarte feil. Riktig svar er:  {right_answer}"), "danger")
            #success = 0
            #database.question_history(exerciseId, success, session["level"], session["courseId"])
        exercise.number_asked += 1
        exercise.updateExercise()
        return render_template('drag_and_drop_contest.html', dragdrop=new_dragdrop, question=question,exerciseId=exerciseId)

    #get the exercise text (question + choices) and show it to the user
    exercise = dragAndDropService.getExercise(exerciseId)
    question = exercise.question
    choices = exercise.choices
    random.shuffle(choices)
    order = []
    for choice in choices:
        order.append(choice['id'])
    return render_template('drag_and_drop_contest.html', dragdrop=choices, question=question, exerciseId=exerciseId, order=order)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int("3000"))


