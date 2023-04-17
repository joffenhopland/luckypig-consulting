import mysql.connector
import itertools
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .flaskenv file

class db:
    def __init__(self) -> None:
        dbconfig = {'host': os.environ.get('HOST'),
                    'user': 'luckypig2023',
                    'password': os.environ.get('PASSWORD'),
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

    def getAllUser(self):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT userId, username FROM user ORDER BY userId")
            result = cursor.fetchall()
            if result == None:
                return result
            else:
                users = []
                for user in result:
                    users.append(user)
                return users
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

    def checkCourseDone(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT done FROM course_status WHERE courseId=(%s) ", (courseId,))
            result = cursor.fetchone()
            print(result[0])
            return result[0]
        except mysql.connector.Error as err:
            print(err)

    def setCourseDone(self, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''UPDATE course_status SET done = (%s) WHERE courseId = (%s)'''
            update = (1,courseId)
            cursor.execute(sql1, update)
            conn.commit()
            conn.close()
            return True
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
            print(f'result: {result}')
            if result[0] is None:
                return False
            elif result[0] >= 0.8:
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

    def question_history(self,exerciseId,success,level, courseId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO question_history (exerciseId, success, courseId, level)
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

    def checkGoldLevelCompleted(self, userId, themeId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute('''SELECT course_status.courseId FROM course_status 
                INNER JOIN active_course ON course_status.courseId=active_course.courseId 
                WHERE active_course.userId = (%s) AND course_status.themeId = (%s) 
                AND course_status.level = (%s) AND course_status.done = (%s)''', (userId, themeId, 3, 1))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
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
    def get_group(self, teacher_userID = None):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            if teacher_userID is None:
                cursor.execute("SELECT * FROM group_table")
            else:
                cursor.execute("SELECT * FROM group_table WHERE userID=(%s)", (teacher_userID,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)
    def get_users_teacher(self, teacher_userID):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM group_user_view WHERE teacher_id=(%s)", (teacher_userID,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)
          
    # report - user
    def user_view(self, role, teacher_user_id=None, group_id=None, theme_id=None, user_id=None, level=None):
        query, values_sql = self.get_sql_query_for_user_view(role, teacher_user_id=teacher_user_id, group_id=group_id, theme_id=theme_id, user_id=user_id, level=level)
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            if values_sql != []:
                cursor.execute(query, (values_sql))
            else:
                cursor.execute(query, (values_sql))
            result = cursor.fetchall()
            return (result,query)
        except mysql.connector.Error as err:
            print(err)
            
    def get_sql_query_for_user_view(self, role, teacher_user_id=None, group_id=None, theme_id=None, user_id=None, level=None):
        select_sql = "SELECT "
        from_sql = " FROM "
        where_sql = ""
        values_sql = []
        
        #Role=Admin
        if role == 3:
            if group_id == None:
                select_sql += "u.username, u.number_tasks, u.number_correct, u.successrate"
                from_sql += "user_view as u" 
                
                if theme_id != None or user_id != None or level != None:
                    where_sql = " WHERE "  
                
            else:
                select_sql += "u.username, g.group_name, u.number_tasks, u.number_correct, u.successrate"
                from_sql += "group_user_view AS g, user_view AS u"
                where_sql += " WHERE g.userId = u.user_id AND g.group_id = (%s)"
                values_sql.append(group_id)
                
                if theme_id != None or user_id != None or level != None:
                    where_sql += " AND "
             
            
        #Role=Lærer
        elif role == 2:
            select_sql += "u.username, g.group_name, u.number_tasks, u.number_correct, u.successrate"
            from_sql += "group_user_view AS g, user_view AS u"
            where_sql += " WHERE g.userId = u.user_id AND g.teacher_id = (%s)"
            if teacher_user_id != None:
                values_sql.append(teacher_user_id)
            else:
                print("Missing user_teacher_id")
                return None
            
            if group_id != None:
                where_sql += " AND g.group_id = (%s)"
                values_sql.append(group_id)
                
            if theme_id != None or user_id != None or level != None:
                where_sql += " AND "
        
        #Role=?
        else:
            print("User_view in database.py has not received a correct role value.")
            return None
        
        if theme_id != None:
            select_sql += ", u.theme_id"
            where_sql += "u.theme_id = (%s) "
            values_sql.append(theme_id)
        if user_id != None:
            select_sql += ", u.user_id"
            if theme_id != None:
                where_sql += "AND "
            where_sql += "u.user_id = (%s) "
            values_sql.append(user_id)
        if level != None:
            select_sql += ", u.current_level"
            if user_id != None or theme_id != None:
                where_sql += "AND "
            where_sql += "u.current_level = (%s) "
            values_sql.append(level)
        
        query = select_sql+from_sql+where_sql 
        return query, values_sql
    
    
    # report - tasks     
    def all_tasks_report_view(self,role, n_rows=10, teacher_user_id=None, group_id=None, theme_id=None, level=None):
        query, values_sql = self.get_sql_query_for_all_tasks_report_view(role, teacher_user_id=teacher_user_id, group_id=group_id, theme_id=theme_id, level=level)
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            if values_sql != []:
                cursor.execute(query, (values_sql))
            else:
                cursor.execute(query, (values_sql))
            result = cursor.fetchall()
            if len(result) >= n_rows:
                return (result[:n_rows],query)
            else:
                return (result,query)
        except mysql.connector.Error as err:
            print(err)
    
    def get_sql_query_for_all_tasks_report_view(self, role, teacher_user_id=None, group_id=None, theme_id=None, user_id=None, level=None): 
        select_sql = "SELECT "
        from_sql = "FROM "
        where_sql = ""
        values_sql = []
        
        #Role=Admin
        if role == 3:
            select_sql += "g.exerciseId as exercise_id, sum(g.antall_riktig) as number_asked, sum(g.antall_utført) as number_success, (100 / sum(g.antall_utført) * sum(g.antall_riktig)) as percent, a.level, a.themeId as theme_id "
            from_sql += "group_questions as g left join all_tasks_view as a ON a.exerciseId = g.exerciseId "
        
            if group_id != None or theme_id !=None or level != None:
                where_sql += "WHERE "
                
            if group_id != None:
                where_sql += "g.groupId = (%s) "
                values_sql.append(group_id)
            '''
            if theme_id != None:
                if group_id != None:
                    where_sql += "AND "
                where_sql += "a.themeId = (%s) "
                values_sql.append(theme_id)
                '''
                
            if level != None:
                if group_id != None or theme_id != None:
                    where_sql += "AND "
                where_sql += "a.level = (%s) "
                values_sql.append(level)
        
            query = select_sql+from_sql+where_sql+"GROUP BY g.exerciseId, a.level, a.themeId ORDER BY percent ASC "
                
        #Role=Lærer
        elif role == 2:
            select_sql += "g.exerciseId as exercise_id, sum(g.antall_riktig) as number_asked, sum(g.antall_utført) as number_success, (100 / sum(g.antall_utført) * sum(g.antall_riktig)) as percent, gv.groupId as group_id, gv.userID as teacher_user_id "
            from_sql += "group_questions as g, gruppe_view as gv "
            where_sql += "WHERE g.groupId = gv.groupId AND gv.userId = (%s) "
            
            if teacher_user_id == None:
                print("Missing user_teacher_id")
                return None
            values_sql.append(teacher_user_id)
            
            if group_id != None:
                where_sql += "AND g.groupId = (%s) "
                values_sql.append(group_id)
            
            query = select_sql+from_sql+where_sql+"GROUP BY g.exerciseId, gv.groupId ORDER BY percent ASC " 
              
        #Role=?
        else:
            print("User_view in database.py has not received a correct role value.")
            return None
          
        return query, values_sql
    
    # Group
    def get_not_member_users(self, group_id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT u.userId, u.username FROM user AS u, user_group AS ug WHERE u.userId = ug.userId AND ug.groupId not like (%s)", (group_id,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)
    
    def add_group_member(self,group_id, group_member_id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO user_group (groupId, userId)
                VALUES (%s, %s)'''
            cursor.execute(sql1, (group_id, group_member_id,))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)
            
    def remove_group_member(self,group_id, group_member_id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_group WHERE groupId = (%s) AND userId = (%s)", (group_id, group_member_id,))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)
        
        
    def invite_request_group_member(self, group_id, group_member_id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO group_invitation (groupId, userId)
                VALUES (%s, %s)'''
            cursor.execute(sql1, (group_id, group_member_id,))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)
            
    def get_invite_request_group_member(self, group_id):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT g.userId, u.username FROM group_invitation AS g, user AS u WHERE u.userId = g.userId AND g.groupId = (%s)", (group_id,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)
            
    def answer_invite_request_group_member(self, group_id, request_member_id, accept): #accept: boolean
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM group_invitation WHERE groupId = (%s) AND userId = (%s)", (group_id, request_member_id,))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)
        
        try:   
            if accept == True:
                conn = mysql.connector.connect(**self.configuration)
                cursor = conn.cursor()
                sql1 = '''INSERT INTO user_group (groupId, userId)
                VALUES (%s, %s)'''
                cursor.execute(sql1, (group_id, request_member_id,))
                conn.commit()
                conn.close()
        except mysql.connector.Error as err:
            print(err)
  
    def getGroups(self, userId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM group_table WHERE userId=(%s)
                            UNION
                            SELECT group_table.* FROM group_table 
                            INNER JOIN user_group ON group_table.groupId=user_group.groupId 
                            WHERE user_group.userId = (%s) ''', (userId, userId))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def createGroup(self, name, userId, group_typeId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO group_table (name, userId, group_typeId)
                VALUES (%s, %s, %s)'''
            insert = (name, userId, group_typeId)
            cursor.execute(sql1, insert)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)


    def getAllGroupName(self):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM group_table")
            results = cursor.fetchall()
            resultlist = []
            if results is not None:
                resultlist = [result[0] for result in results]
            return resultlist
        except mysql.connector.Error as err:
            print(err)

    def get_leaderboard(self):
        #Implementerer grupper her senere
        all_user_leaderboard = """
        select username, SUM(points) as total_points
        from user_view
        group by user_id
        order by total_points DESC"""

        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(all_user_leaderboard)
            result = cursor.fetchall()
            leaderboard_data = [{'username': row[0], 'points': row[1]} for row in result]
            return leaderboard_data
        except mysql.connector.Error as err:
            print(err)

    def getQuestionsForContest(self, question_type, level, theme):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            query = "SELECT exerciseID, question FROM `{}` WHERE level = %s AND themeID = %s".format(question_type)
            cursor.execute(query, (level,theme,))
            result = cursor.fetchall()
            choices = [(str(row[0]), row[1]) for row in result]
            return choices
        except mysql.connector.Error as err:
            print(err)

    def get_group_members(self, groupId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("SELECT user.username, user.userId from user, group_table, user_group \
                        where group_table.groupId = user_group.groupId \
                        and user_group.userId = user.userId \
                        and group_table.groupId = (%s)", (groupId,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def all_user_name(self):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, userId from user")
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def invite_request_group_member(self, groupId, userId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO group_invitation (groupId, userId, confirmed)
                            VALUES (%s, %s, %s)'''
            insert = (groupId, userId, 0)
            cursor.execute(sql1, insert)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

    def all_user_name_memberinvitation(self, groupId):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT username, userId FROM user 
                    WHERE NOT (userId IN (SELECT userId from user_group WHERE user_group.groupId = (%s)))
                        AND NOT (userId IN (SELECT userId FROM group_invitation WHERE groupId = (%s)))
                        AND NOT (userId = (SELECT userId FROM group_table WHERE groupId = (%s)))
                ''', (groupId, groupId, groupId))

            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def delete_group(self, group_id): 
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM group_table WHERE groupId = (%s)", (group_id, ))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

    def search_user(self, search):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            cursor.execute(
                    "select username, userId from user where username = (%s)  \
                    union \
                    select username, userId from user where email = (%s)  \
                    union \
                    select username, userId from user where lower(username) like (%s) or lower(username) like (%s) \
                    union \
                    select username, userId from user where lower(email) like (%s) or lower(email) like (%s)", (search, search, f'{search}%', f'%{search}', f'{search}%', f'%{search}'))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

def main():
    database = db()
    #z = database.get_group_members(1)
    #print(z)
    #database.delete_question_done(25)
    print(database.search_user("kristoffer"))
    #database.invite_request_group_member(2,6)
    #database.answer_invite_request_group_member(group_id=2, request_member_id=6, accept=True)
   
    
main()