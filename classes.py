from database import db

class MultipleChoiceExercise:
    def __init__(self, exerciseID,level, question, answer, score, number_asked, number_succeed, themeId, choices):
        self.exerciseID = exerciseID
        self.level = level
        self.question = question
        self.answer = answer
        self.score = score
        self.number_asked = number_asked
        self.number_succeed = number_succeed
        self.themeId = themeId
        self.choices = choices
        self.type = 3

    def getExerciseByID(self, exerciseID):
        database = db()
        exerciseID = 1

        #fill exercise info
        (exerciseID, level, question, answer, score, number_asked, number_succeed, themeId) = database.getExerciseById(exerciseID, self.type)
        self.exerciseID = exerciseID
        self.level = level
        self.question = question
        self.answer = answer
        self.score = score
        self.number_asked = number_asked
        self.number_succeed = number_succeed
        self.themeId = themeId

        #fill option
        choices = database.getOptionsByExerciseId(exerciseID, self.type)
        self.choices = choices

    def updateExercise(self):
        database = db()
        database.updateExerciseByExerciseIdandType(self.exerciseID,self.type,self.number_asked,self.number_succeed)

