import mysql.connector
from classes import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .flaskenv file

class UserLogin:
    
    def __init__(self):
        self.dbconfig = {'host': os.environ.get('HOST'),
                     'user': 'luckypig2023',
                     'password': os.environ.get('PASSWORD'),
                     'database': 'Luckypig database', }
        self.conn = mysql.connector.connect(**self.dbconfig)
        self.cursor = self.conn.cursor(prepared=True)
        self.users = []
        self.loadUsers()

    
    def loadUsers(self):
        try:
            self.cursor.execute("SELECT * from user")
            result = self.cursor.fetchall()
            for row in result:

                (user_id,firstname, lastname, username, email, password_hash, emailVerified, role, verificationId, login_streak, last_login) = row
                newUser = User(user_id,firstname, lastname, username, email, password_hash, emailVerified, role, verificationId, login_streak, last_login)
                self.users.append(newUser)

        except mysql.connector.Error as err:
            print(err)
    
    def getAllUsers(self):
        return self.users

    def getUserByEmail(self, email):
        try:
            self.conn = mysql.connector.connect(**self.dbconfig)
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT * FROM user WHERE email=(%s)", (email,))
            result = self.cursor.fetchone()
            return result

        except mysql.connector.Error as err:
            print(err)

    def isUser(self, email):
        if self.getUserByEmail(email):
            return True
        return False

    def updateUser(self, firstname, lastname,username, email):

        try:
            insert_statment = (
                "UPDATE user SET first_name=%s, last_name=%s, username=%s WHERE email=%s")
            data = (firstname, lastname,username,email)

            self.cursor = self.conn.cursor(prepared=True)
            self.cursor.execute(insert_statment, data)
            self.conn.commit()

        except mysql.connector.Error as err:
            print(err)


    def updateUserPassword(self, email, password_hash):

        try:
            insert_statment = (
                "UPDATE user SET password=%s WHERE email=%s")
            data = (password_hash,email)

            self.cursor = self.conn.cursor(prepared=True)
            self.cursor.execute(insert_statment, data)
            self.conn.commit()

        except mysql.connector.Error as err:
            print(err)
            
    def isCorrectPassword(self, email, password,bcrypt):
        user = self.getUser(email)
        if user:
            return bcrypt.check_password_hash(user.password_hash, password)  
        return False 

    def canLogIn(self, email, password,bcrypt):

        if self.isUser(email) and self.isCorrectPassword(email, password,bcrypt) and self.emailConfirmed(email):
            return True

        return False
    
    def confirmEmail(self, email):
        try:
            insert_statment = ("UPDATE user SET emailVerified=1 WHERE email=%s")
            self.cursor = self.conn.cursor(prepared=True)
            self.cursor.execute(insert_statment, (email,))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)
    
    def getUser(self, email):
        self.loadUsers()
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def __str__(self):

        outputstring=""

        for user in self.users:
            outputstring += str(user) + "\n"

        return outputstring
    
    def emailConfirmed(self, email):
        user = self.getUser(email)
        if user.emailVerified:
            return True
        return False

    def updateUuid(self,email, uuid):

        try:
            insert_statment = (
                "UPDATE user SET uuid=%s,  WHERE email=%s")
            data = (uuid,email)

            conn = mysql.connector.connect(**self.configuration)
            cursor = conn.cursor(prepared=True)
            cursor.execute(insert_statment, data)
            conn.commit()

        except mysql.connector.Error as err:
            print(err)

