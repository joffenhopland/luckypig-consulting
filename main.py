import random
import secrets
import uuid
import itertools
import random

from flask import Flask, flash, request, redirect, render_template, url_for, session
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

from classes import DragAndDropService
from database import db
from UserLogin import UserLogin
from forms import RegistrerForm, LoginForm, forgetPasswordForm, UpdatePasswordForm, UpdateUserForm, resetPasswordForm, validate_password
from User import User
import json
from classes import Exercise, Dropdown, CourseStatus

import json
import urllib.parse

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


@app.route("/course", methods=['GET', 'POST'])
def course():
    database = db()
    print(f'58. session["courseId"]: {session["courseId"]}')
    questions = session["questions"]
    level_points = database.get_level_points(session["courseId"])
    session["level_points"] = level_points
    print(f'level_points: {level_points}')

    '''
    #find course or create if None. This is needed if user takes courses in several themes
    if session["courseId"] == -1:
        session["theme"] = 1 #dette må sendes fra learn siden et kurs ikke har blitt opprettet
        session["language"] = 1 #Kan øke med flere språk i fremtiden

        session["courseId"] = database.course_status(session["idUser"])
        #session["courseId"] = database.course_status(session["idUser"],session["level"],session["theme"])

        if session["courseId"] == None:
            #Vi lager et nytt active course for brukeren
            database.initiate_course(session["idUser"])
            #Vi henter id for det nye kurset
            #course_status = database.course_status(session["idUser"])
            session["courseId"] = database.course_status(session["idUser"])
            print(f'77. course_status: {session["courseId"]}')
            #Vi setter ny course_status for det kurset
            #database.new_course_status(session["theme"], session["language"], course_status)
            database.new_course_status(session["theme"], session["language"], session["courseId"])

        session["questions"] = []
        return redirect(url_for("course"))
    '''
    # existing course - user returns or new course
    if len(questions) == 0 and session["init_course"] == 1:
        level_points = 0
        session["level_points"] = level_points
        database.update_levelpoints(session["courseId"], level_points)
        session["init_course"] = 0
        print(f'session["courseId"]: {session["courseId"]}')
        info = database.get_level_theme(session["courseId"])
        print(f'info: {info}')

        theme = info[1]
        session["level"] = info[0]

        allQuestions = (database.get_new_questions(session["level"], theme))
        allQuestionslst = list(itertools.chain(*allQuestions))

        question_done = (database.get_questions_done(session["courseId"]))
        question_donelst = list(itertools.chain(*question_done))

        questions = [x for x in allQuestionslst if x not in question_donelst]
        random.shuffle(questions)
        print(f'questions at start: {questions}')
        # temporary just to test multiple choice ex.
        # questions = [3002, 3003, 3004, 3005, 3006, 3007]

        session["questions"] = questions
        if len(session["questions"]) == 0:
            flash(f'Du har gjort alle oppgavene', "success")
            return redirect(url_for("learn"))
        session["exerciseId"] = session["questions"].pop(0)
        first = int(str(session["exerciseId"])[0])
        print(f'first: {first}')
        view = checknumber(first)
        # print(f'questions in /course: {session["questions"]}')
        # print(f'exerciseId in /course: {session["exerciseId"]}')
        checklevel()
        return redirect(url_for(view))

    # existing course - user submit question
    if len(questions) > 0:
        # id = questions[0]
        # first = int(str(id)[0])

        # # Convert the list to a string representation
        # questions_str = str(questions)

        # # Remove the square brackets at the beginning and end of the string
        # questions_str = questions_str[1:-1]
        if len(session["questions"]) == 0:
            flash(f'Du har gjort alle oppgavene', "success")
            return redirect(url_for("learn"))
        session["exerciseId"] = session["questions"].pop(0)
        first = int(str(session["exerciseId"])[0])
        print(f'first: {first}')
        view = checknumber(first)
        print(f'questions in /course: {session["questions"]}')
        print(f'exerciseId in /course: {session["exerciseId"]}')
        # checkLevel sets session["level_name"] to the name of the level
        checklevel()
        
        return redirect(url_for(view))

    # user has done alle questions in one level and successrate is good
    if len(questions) == 0 and database.success_rate(session["courseId"]):
        print(f'session["level"]: {session["level"]}')
        # level_points = database.get_level_points(session["courseId"])
        # print(f'level_points: {level_points}')
        if session["level"] < 3:
            level = session["level"]
            level += 1
            print(f'session["level"] if: {session["level"]}')
            # Vi øker level med 1 og setter inn i DB
            database.update_level(level, session["courseId"])
            # Vi sletter level_points. Hvor mange poeng brukeren har oppnådd i det levelet
            level_points = 0
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], level_points)
            session["level"] = level
            #should we remove the question done once level done?
            database.delete_question_done(session["courseId"])
            session["init_course"] = 1
            flash(f'Gratulerer, du har oppnådd nok poeng til å nå neste level', "success")
            return redirect(url_for("learn"))
        else:
            level_points = 0
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], level_points)
            flash(f'Gratulerer, du har oppnådd gull og dermed fullført språkkurset!', "success")
            return redirect(url_for("learn"))

    # user has done alle questions in one level and successrate is NOT good
    if len(questions) == 0 and database.success_rate(session["courseId"]) == False:
        level_points = 0
        database.update_levelpoints(session["courseId"], level_points)
        database.delete_question_done(session["courseId"])
        session["init_course"] = 1
        flash(f'Du har dessverre ikke klart nok oppgaver og må gjøre nivået på nytt', "danger")
        return redirect(url_for("learn"))
    return redirect(url_for("learn"))


def checknumber(id):
    if id == 1:
        return "dropdown"
    elif id == 3:
        return "multiple_choice"
    elif id == 5:
        return "drag_and_drop"

def checklevel():
    if session["level"] == 1:
        session["level_name"] = "Level: Bronse"
        # return "Level: Bronze"
    elif session["level"] == 2:
        session["level_name"] = "Level: Sølv"
        # return "Level: Sølv"
    elif session["level"] == 3:
        session["level_name"] = "Level: Gull"
        # return "Level: Gull"

@app.route("/multiple-choice", methods=['GET', 'POST'])
def multiple_choice():
    database = db()
    exerciseId = session['exerciseId']
    print(f'questions_str: {session["questions"]}')
    print(f'exerciseId in /multiple-choice: {exerciseId}')

    if request.method == 'POST':
        exercise = Exercise(exerciseId, 3)
        exercise.getExercise()
        question = exercise.question
        choices = exercise.choices
        right_answer = exercise.answer
        answer = request.form['answer']

        if answer == right_answer:
            flash(f'Correct!', "success")
            exercise.number_succeed += 1
            success = 1
            print(f'questino_done: {exerciseId}, {success}, {session["level"]}, {session["courseId"]}')
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            # need to update user score
            # get current score from course_status
            # add exercise.score to the current score
            # write new score to active_course

            # Increase the users total points:
            courseStatus = CourseStatus(session['courseId'])
            print(f'exercise.score: {exercise.score}')
            courseStatus.updatePoints(exercise.score)
            # Increase users current level points
            level_points = database.get_level_points(session["courseId"])
            level_points += 1
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], session["level_points"])
        else:
            flash(f'Wrong!', "danger")
            success = 0
            database.question_done(exerciseId, success, session["level"], session["courseId"])
        
        exercise.number_asked += 1
        exercise.updateExercise()
        return render_template('multiple_choice.html', question=question, choices=choices, level_name=session["level_name"], level_points=session["level_points"])

    print(f'exerciseId: {exerciseId}')
    exercise = Exercise(exerciseId, 3)
    exercise.getExercise()
    question = exercise.question
    choices = exercise.choices
    return render_template('multiple_choice.html', question=question, choices=choices, level_name=session["level_name"], level_points=session["level_points"])

@app.route('/dropdown', methods=['GET', 'POST'])
def dropdown():
    database = db()
    exerciseId = session['exerciseId']
    print(f'questions_str: {session["questions"]}')
    print(f'exerciseId in /dropdown: {exerciseId}')       #to be changed when the course is running
    # exercise = Dropdown(exerciseId, 1)
    # exercise.getExercise()
    # norwegian_question = exercise.question
    # english_question = exercise.question_translated
    # choices = exercise.choices
    # right_answer = exercise.answer



    if request.method == 'POST':
        exercise = Dropdown(exerciseId, 1)
        exercise.getExercise()
        norwegian_question = exercise.question
        english_question = exercise.question_translated
        choices = exercise.choices
        right_answer = exercise.answer
        answer = request.form['answer']

        if answer == right_answer:
            flash(f'Correct!', "success")
            exercise.number_succeed += 1
            success = 1
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            #Increase the user points:
            courseStatus = CourseStatus(session['courseId'])
            print(f'exercise.score: {exercise.score}')
            courseStatus.updatePoints(exercise.score)
            # Increase users current level points
            level_points = database.get_level_points(session["courseId"])
            level_points += 1
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], session["level_points"])
        else:
            flash(f'Wrong!', "danger")
            success = 0
            database.question_done(exerciseId, success, session["level"], session["courseId"])

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
    database = db()

    exerciseId = session['exerciseId']
    # exercise = dragAndDropService.getExercise(exerciseId)
    # question = exercise.question
    # choices = exercise.choices

    if request.method == 'POST':
        exercise = dragAndDropService.getExercise(exerciseId)
        # exercise = Exercise(exerciseId, 5)
        # exercise.getExercise()
        question = exercise.question
        choices = exercise.choices
        right_answer = exercise.answer
        print(f"equest.form.getlist('answer'): {request.form.getlist('answer')}")
        order = [int(q) for q in request.form.getlist('answer')[0].split(',')]
        new_dragdrop = []
        user_answer = []
        # user_answer = request.form['answer']
        for item in order:
            for elem in exercise.choices:
                if elem['id'] == item:
                    new_dragdrop.append(elem)
                    user_answer.append(elem['text'])

        print(f'riktig svar: {right_answer}')
        print(user_answer)
        print(f'user answer {" ".join(user_answer)}')

        if " ".join(user_answer) == right_answer:
            flash(f'Correct!', "success")
            print("ok")
            success = 1
            database.question_done(exerciseId, success, session["level"], session["courseId"])
            #Increase the user points:
            courseStatus = CourseStatus(session['courseId'])
            print(f'exercise.score: {exercise.score}')
            courseStatus.updatePoints(exercise.score)
            # Increase users current level points
            level_points = database.get_level_points(session["courseId"])
            level_points += 1
            session["level_points"] = level_points
            database.update_levelpoints(session["courseId"], session["level_points"])
        else:
            flash(f'Wrong!', "danger")
            success = 0
            database.question_done(exerciseId, success, session["level"], session["courseId"])
        exercise.number_asked += 1
        # exercise.updateExercise()
        return render_template('drag_and_drop.html', dragdrop=new_dragdrop, question=question, exerciseId=exerciseId, level_name=session["level_name"], level_points=session["level_points"])
    
    print(f'exerciseId: {exerciseId}')
    exercise = dragAndDropService.getExercise(exerciseId)

    # exercise = Exercise(exerciseId, 5)
    # exercise.getExercise()
    question = exercise.question
    choices = exercise.choices
    random.shuffle(choices)
    return render_template('drag_and_drop.html', dragdrop=choices, question=question, exerciseId=exerciseId, level_name=session["level_name"], level_points=session["level_points"])




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
    database = db()
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
            session["language"] = 1
            session["theme"] = 1
            session["level"] = 1
            session["courseId"] = getCourseId(session["idUser"],session["theme"],session["language"])
            (level,theme) = database.get_level_theme(session["courseId"])
            session["theme"] = theme
            session["level"] = level
            session["questions"] = []
            session["exerciseId"] = 0
            session["init_course"] = 1
            flash(f'Du er logget inn!', "success")
            return redirect(url_for('learn'))

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
    session.pop("courseId", None)
    session.pop("questions", None)
    session.pop("exerciseId", None)
    flash(f'Du er logget ut!', "info")
    return redirect(url_for('home'))

def getCourseId(idUser, theme, language):
    database = db()
    courseId = database.course_status(idUser)

    if courseId == False:
        # Vi lager et nytt active course for brukeren
        database.initiate_course(idUser)
        # Vi henter id for det nye kurset
        courseId = database.course_status(idUser)
        # Vi setter ny course_status for det kurset
        database.new_course_status(theme, language, courseId)
    return courseId


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int("3000"))


