import mysql.connector
import pandas as pd


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
    
    def read_file(self):
        data = pd.read_csv("new_questions.csv", delimiter=";", encoding= 'unicode_escape')
        for i in range(len(data)):
            line = data.iloc[i].tolist()
            line[1] = int(line[1])
            line[2] = int(line[2])
            line[5] = int(line[5])
            question = line[1:6]
            choice = line[6:]
            if line[0] == 1:
                self.insert_drop(question, choice)
            elif line[0] == 3:
               self.insert_multiple(question, choice)
            elif line[0] == 5:
                self.insert_drag(question, choice)
    
    def insert_drop(self, question, choice):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO drop_down (level, themeId, question, answer, score)
                VALUES (%s, %s, %s, %s, %s)'''
            cursor.execute(sql1, question)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

        for choices in choice:
            try:
                conn = mysql.connector.connect(**self.configuration)
                cursor = conn.cursor()
                cursor.execute("SELECT max(exerciseId) from drop_down")
                result = cursor.fetchone()
                val = (choices, int(result[0]))
                sql1 = '''INSERT INTO drop_down_choice (choice, dropId)
                    VALUES (%s, %s)'''
                cursor.execute(sql1, val)
                conn.commit()
                conn.close()
            except mysql.connector.Error as err:
                print(err)

    
    def insert_multiple(self, question, choice):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO multiple_choice (level, themeId, question, answer, score)
                VALUES (%s, %s, %s, %s, %s)'''
            cursor.execute(sql1, question)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

        for choices in choice:
            try:
                conn = mysql.connector.connect(**self.configuration)
                cursor = conn.cursor()
                cursor.execute("SELECT max(exerciseId) from multiple_choice")
                result = cursor.fetchone()
                val = (choices, int(result[0]))
                sql1 = '''INSERT INTO multiple_choice_choice (choice, multipleId)
                    VALUES (%s, %s)'''
                cursor.execute(sql1, val)
                conn.commit()
                conn.close()
            except mysql.connector.Error as err:
                print(err)
    
    def insert_drag(self, question, choice):
        try:
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO drag_and_drop (level, themeId, question, answer, score)
                VALUES (%s, %s, %s, %s, %s)'''
            cursor.execute(sql1, question)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(err)

        for choices in choice:
            try:
                conn = mysql.connector.connect(**self.configuration)
                cursor = conn.cursor()
                cursor.execute("SELECT max(exerciseId) from drag_and_drop")
                result = cursor.fetchone()
                val = (choices, int(result[0]))
                sql1 = '''INSERT INTO drag_choices (choice, dragId)
                    VALUES (%s, %s)'''
                cursor.execute(sql1, val)
                conn.commit()
                conn.close()
            except mysql.connector.Error as err:
                print(err)
    

#def main():
#    database = db()
#    database.read_file()
#main()