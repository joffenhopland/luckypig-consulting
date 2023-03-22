import mysql.connector
import itertools

class db:
    def __init__(self) -> None:
        dbconfig = {'host': '34.121.34.57',
                    'user': 'luckypig2023',
                    'password': 'LuckypigProject#1',
                    'database': 'Luckypig database', }
        self.configuration = dbconfig

    def __enter__(self):
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor(prepared=True)
        return self

#Puts a new user into the database
    def newUser(self, user):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO user (first_name, last_name, username, email, password, role, verificationId)
                VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql1, user)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

    #Checks if the verificationId exists
    #If yes, the user is verified
    def verify(self, verificationId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT userId from user where verificationId=(%s)", (verificationId,))
            result = cursor.fetchone()
        except mysql.connector.Error as err:
            print(err)

        if result == None:
            return False

        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE user
            SET emailVerified = (%s) WHERE verificationId = (%s)'''
            oppdater = (1, verificationId)
            cursor.execute(sql1, oppdater)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

    #Checks if the email exists
    def attemptedUser(self, email):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email from user where email=(%s)", (email,))
            result = cursor.fetchone()
            if result == None:
                return False
            else:
                return result[0]
        except mysql.connector.Error as err:
            print(err)

    def usernameCheck(self, username):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username from user where username=(%s)", (username,))
            result = cursor.fetchone()
            if result == None:
                return False
            else:
                return result[0]
        except mysql.connector.Error as err:
            print(err)

    #Gets all information about an user. For logging in.
    def getUser(self, email):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user WHERE email=(%s)", (email,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err)


    #Gets all information from user after verification. For logging in automatic after link pressed.
    def getUser2(self, kode):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bruker WHERE verifiseringskode=(%s)", (kode,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err)


    def updateUuid(self, email, uuid):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE user
            SET verificationId = (%s) WHERE email = (%s)'''
            oppdater = (uuid,email)
            cursor.execute(sql1, oppdater)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

    def resetPassword(self, email, password):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE user
            SET password = (%s) WHERE verificationId = (%s)'''
            oppdater = (password,email)
            cursor.execute(sql1, oppdater)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

    def getUserByUUID(self, uuid):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user WHERE verificationId=(%s)", (uuid,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err)

    def getExerciseByIdandType(self, exerciseID, type):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            if type == 1:
                cursor.execute(
                    "SELECT * FROM drop_down WHERE exerciseID=(%s)", (exerciseID,))
            elif type == 3:
                cursor.execute(
                    "SELECT * FROM multiple_choice WHERE exerciseID=(%s)", (exerciseID,))
            elif type == 5:
                cursor.execute(
                    "SELECT * FROM drag_and_drop WHERE exerciseID=(%s)", (exerciseID,))
            result = cursor.fetchone()
            print(f'getExerciseByIdandType: {result}')
            return result
        except mysql.connector.Error as err:
            print(err)

    def getOptionsByExerciseIdandType(self, exerciseID, type):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            if type == 1:
                cursor.execute(
                    "SELECT choice FROM drop_down_choice WHERE dropId=(%s)", (exerciseID,))
            elif type == 3:
                cursor.execute(
                    "SELECT choice FROM multiple_choice_choice WHERE multipleId=(%s)", (exerciseID,))
            elif type == 5:
                #hent dictionary med text og id, ikke bare text per choice
                cursor.execute(
                    "SELECT choice, choiceId FROM drag_choices WHERE dragId=(%s)", (exerciseID,))
                result = cursor.fetchall()
                options = []
                for option in result:
                    options.append({"id":option[1],"text":option[0]})
                return options

            result = cursor.fetchall()
            options = []
            for option in result:
                options.append(option[0])
            return options
        except mysql.connector.Error as err:
            print(err)

    def updateExerciseByExerciseIdandType(self, exerciseID, type, number_asked,number_succeed):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            if type == 1:
                sql1 = '''UPDATE drop_down 
                 SET number_asked = (%s), number_succeed = (%s) WHERE exerciseID = (%s)'''
            elif type == 3:
                sql1 = '''UPDATE multiple_choice 
                  SET number_asked = (%s), number_succeed = (%s) WHERE exerciseID = (%s)'''
            elif type == 5:
                sql1 = '''UPDATE drag_and_drop 
                                  SET number_asked = (%s), number_succeed = (%s) WHERE exerciseID = (%s)'''
            oppdater = (number_asked, number_succeed, exerciseID)
            cursor.execute(sql1, oppdater)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

        
    def getCourseStatusByCourseId(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM course_status WHERE courseId=(%s)", (courseId,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err)

    def getTotalPoints(self, userId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT SUM(level_points) FROM course_status
                INNER JOIN active_course ON course_status.courseId=active_course.courseId 
                WHERE active_course.userId = (%s)''', (userId,))
            result = cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            print(err)

    def course_status(self, id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT courseId from active_course where userId=(%s) ORDER BY courseId DESC ", (id,))
            result = cursor.fetchone()
            if result == None:
                return False
            else:
                return result[0]
        except mysql.connector.Error as err:
            print(err)

    def getCourseIdByUserIdAndTheme(self, userId, themeId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
            '''SELECT course_status.courseId FROM course_status 
                INNER JOIN active_course ON course_status.courseId=active_course.courseId 
                WHERE active_course.userId = (%s) AND course_status.themeId = (%s)
                ORDER BY course_status.level DESC''', (userId, themeId))
            result = cursor.fetchone()
            if result == None:
                return result
            else:
                return result[0]
        except mysql.connector.Error as err:
            print(err)

    def initiate_course(self, id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO active_course (userId)
                VALUES (%s)'''
            insert = (id,)
            cursor.execute(sql1, insert)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

    def new_course_status(self, themeId, languageId, courseId, level):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO course_status (themeId, languageId, courseId, level)
                VALUES (%s, %s, %s, %s)'''
            insert = (themeId, languageId, courseId,level)
            cursor.execute(sql1, insert)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

    def get_new_questions(self, level, theme):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT exerciseId from multiple_choice where level=(%s) and themeId=(%s) \
                           UNION \
                           SELECT exerciseId from drag_and_drop where level=(%s) and themeId=(%s) \
                           UNION \
                           SELECT exerciseId from drop_down where level=(%s) and themeId =(%s)",(level, theme, level, theme, level, theme,))
            result = cursor.fetchall()
            return result
                
        except mysql.connector.Error as err:
            print(err)

    def get_questions_done(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT exerciseId from question_done where courseId=(%s)", (courseId,))
            result = cursor.fetchall()
            if result == None:
                return []
            else:
                return result
        except mysql.connector.Error as err:
            print(err)

    def get_level_theme(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT level, themeId from course_status where courseId=(%s)", (courseId,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err)

    def get_level_points(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT level_points from course_status where courseId=(%s)", (courseId,))
            result = cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            print(err)

    def success_rate(self, courseId ):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(case success when 1 then 1 else null end)/COUNT(exerciseId) from question_done where courseId=(%s)", (courseId,))
            result = cursor.fetchone()
            if result[0] >= 0.8:
                return True
            else:
                return False
        except mysql.connector.Error as err:
            print(err)

        
    def update_level(self, level, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE course_status
            SET level = (%s) WHERE courseId = (%s)'''
            update = (level, courseId)
            cursor.execute(sql1, update)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

    def update_levelpoints(self, courseId, level_points):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE course_status
            SET level_points = (%s) WHERE courseId = (%s)'''
            update = (level_points, courseId)
            cursor.execute(sql1, update)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

    def delete_question_done(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = "DELETE FROM question_done where courseId = (%s)"
            delete = (courseId,)
            cursor.execute(sql1, delete)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)

    def question_done(self, exerciseId, success, level, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO question_done (exerciseId, success, courseId, level)
                VALUES (%s, %s, %s, %s)'''
            insert = (exerciseId, success, courseId, level)
            cursor.execute(sql1, insert)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

    def get_total_points(self, userId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute('''select sum(scores.score) as total
                    from active_course ac
                        join question_done qd on ac.courseId = qd.courseId
                        join (
                             select exerciseID, score
                             from multiple_choice mc
                             union
                             select exerciseID, score
                             from drop_down dd
                             union
                             select exerciseID, score
                             from drag_and_drop drag
                         ) scores
                        on scores.exerciseID = qd.exerciseId
                        where userId = (%s);''', (userId,))
            result = cursor.fetchone()
            print(result[0])
            if result[0] == None:
                return 0
            else:
                return result[0]
        except mysql.connector.Error as err:
            print(err)
    def getUserThemes(self, userId):
            try:
                conn = mysql.connector.connect(**self.configuration)
                cursor = conn.cursor()
                cursor.execute(
                '''SELECT distinct(course_status.themeId), theme.theme FROM course_status 
                    INNER JOIN active_course ON course_status.courseId=active_course.courseId 
                    INNER JOIN theme ON theme.themeId = course_status.themeId
                    WHERE active_course.userId = (%s) ORDER BY theme.theme''',
                    (userId,))
                result = cursor.fetchall()
                themes = []
                for theme in result:
                    themes.append(theme)
                return themes
            except mysql.connector.Error as err:
                print(err)

    def getThemes(self):
            try:
                conn = mysql.connector.connect(**self.configuration)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM theme")
                result = cursor.fetchall()
                themes = []
                for theme in result:
                    themes.append(theme)
                return themes
            except mysql.connector.Error as err:
                print(err)

    def get_level(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT level from course_status where courseId=(%s)", (courseId,))
            result = cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            print(err)

    def get_userview(self): #is currently only used for testing report. It needs to select from user_view later
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT * from user")
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)
    
    def update_user_last_login_login_streak(self, user_id, new_login_date, login_streak):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE user
            SET last_login = (%s), login_streak = (%s) WHERE userId = (%s)'''
            update = (new_login_date, login_streak, user_id)
            cursor.execute(sql1, update)
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(err)
    
    def get_login_streak(self, user_id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT login_streak from user where userId=(%s)", (user_id,))
            result = cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            print(err)


def main():
    database = db()
    #database.delete_question_done(25)
    print(database.get_level_theme(34))
main()