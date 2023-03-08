from database import db

class MultipleChoiceExercise:
    def __init__(self, exerciseID):
        self.exerciseID = exerciseID
        self.level = 0
        self.score = 0
        self.number_asked = 0
        self.number_succeed = 0
        self.themeId = 0
        self.type = 3
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
        database.updateExerciseByExerciseIdandType(self.exerciseID,self.type,str(self.number_asked),str(self.number_succeed))

