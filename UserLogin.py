from hashlib import new
import mysql.connector
from mysql.connector import errorcode
from mysqlx import Result
from User import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt

class UserLogin:
    
    def __init__(self):
        self.dbconfig = {'host': '34.121.34.57',
                        'user': 'luckypig2023',
                        'password': 'LuckypigProject#1',
                        'database': 'LuckyPig1',}
        self.conn = mysql.connector.connect(**self.dbconfig)
        self.cursor = self.conn.cursor(prepared=True)
        self.users = []
        self.loadUsers()

    
    def loadUsers(self):
        try:
            self.cursor.execute("SELECT * from user")
            result = self.cursor.fetchall()
            for row in result:

                (user_id,firstname, lastname, username, email, password_hash, emailVerified, role, verificationId) = row
                newUser = User(user_id,firstname, lastname, username, email, password_hash, emailVerified, role, verificationId)
                self.users.append(newUser)

        except mysql.connector.Error as err:
            print(err)
    
    def getAllUsers(self):
        return self.users

    def isUser(self, email):
        for user in self.users:
            if email == user.email:
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
            
    def isCorrectPassword(self, email, password):
        user = self.getUser(email)
        if user:
            return user.password_hash == password
            #return check_password_hash(user.password_hash, password)--------------------------------------------to be changed to hash password!!!!
        return False 

    def canLogIn(self, email, password):

        if self.isUser(email) and self.isCorrectPassword(email, password) and self.emailConfirmed(email):
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

