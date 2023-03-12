from database import db

class Exercise:
    def __init__(self, exerciseID, type):
        self.exerciseID = exerciseID
        self.level = 0
        self.score = 0
        self.number_asked = 0
        self.number_succeed = 0
        self.themeId = 0
        self.type = type
        self.question = ''
        self.answer = ''
        self.choices = []

    def getExercise(self):
        database = db()

        #fill exercise info
        (exerciseID, level, question, answer, score, number_asked, number_succeed, themeId) = database.getExerciseByIdandType(self.exerciseID, self.type)
        self.level = level
        self.question = question
        self.answer = answer
        self.score = score
        self.number_asked = number_asked
        self.number_succeed = number_succeed
        self.themeId = themeId

        #fill option
        choices = database.getOptionsByExerciseIdandType(self.exerciseID, self.type)
        self.choices = choices

    def updateExercise(self):
        database = db()
        database.updateExerciseByExerciseIdandType(self.exerciseID, self.type, str(self.number_asked), str(self.number_succeed))


class ActiveCourse:
    def __init__(self, statusId, level, points, themeId, number_exercises, number_login_week, last_login, languageId, courseId):
        self.statusId = statusId
        self.level = level
        self.points = points
        self.themeId = themeId
        self.number_exercises = number_exercises
        self.number_login_week = number_login_week
        self.last_login = last_login
        self.languageId = languageId
        self.courseId = courseId

class Dropdown(Exercise):
    def __init__(self, exerciseID, type):
        super().__init__(exerciseID, type)
        self.question_translated = ""

    def getExercise(self):
        database = db()

        #fill exercise info
        (exerciseID, level, question, answer, score, number_asked, number_succeed, themeId, question_translated) = database.getExerciseByIdandType(self.exerciseID, self.type)
        self.level = level
        self.question = question
        self.answer = answer
        self.score = score
        self.number_asked = number_asked
        self.number_succeed = number_succeed
        self.themeId = themeId
        self.question_translated = question_translated

        # fill option
        choices = database.getOptionsByExerciseIdandType(self.exerciseID, self.type)
        self.choices = choices
    def updateExercise(self):
        super().updateExercise()
