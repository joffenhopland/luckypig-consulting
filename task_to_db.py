import mysql.connector
import pandas as pd


class db:
    def __init__(self) -> None:
        dbconfig = {'host': '34.30.103.41',
                    'user': 'luckypig2023',
                    'password': 'LuckypigProject#1',
                    'database': 'Luckypig database', }
        self.configuration = dbconfig


    def __enter__(self):
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor(prepared=True)
        return self
    
    def read_file(self):
        data = pd.read_csv("new_questions2.csv", delimiter=";", encoding='ANSI')
        for i in range(len(data)):
            line = data.iloc[i].tolist()
            print(line[3])
            if line[0] == 1:
                self.insert_drop(line)
            elif line[0] == 3:
               self.insert_multiple(line)
            elif line[0] == 5:
                self.insert_drag(line)
    
    def insert_drop(self, line):
        try:
            line[1] = int(line[1])
            line[2] = int(line[2])
            line[6] = int(line[6])
            question = line[1:7]
            choice = line[7:]
            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor()
            sql1 = '''INSERT INTO drop_down (level, themeId, question, question_translated, answer, score)
                VALUES (%s, %s, %s, %s, %s, %s)'''
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

    
    def insert_multiple(self, line):
        try:
            line[1] = int(line[1])
            line[2] = int(line[2])
            line[5] = int(line[5])
            question = line[1:6]
            choice = line[6:]
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