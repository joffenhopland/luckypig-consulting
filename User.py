class User:
    def __init__(self,user_id,firstname, lastname, username, email, password_hash, emailVerified, role,verificationId):
        self.user_id = user_id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.emailVerified = emailVerified
        self.role = role
        self.verificationId = verificationId
    
    def __str__(self):
        return str(self.firstname) + " " + str(self.lastname)
    
    def setConfirmation(self):
        self.emailVerified = 1

