'''
Main module to control the Authentication of user provided by the app.
'''
from auth_db_conn import DBConnectionSelect

class AuthenticationManager():
    '''
    Main class used to control the authentication of a user registered with
    this class. Instantiate the class with an instance of User and 
    call authenticate(), the class will handle the authentication.
    '''
    def __init__(self, username, pin):
        self.username = username
        self.pin = pin

    def login_check(self) -> list:
        #using the auth_db_conn module to retrieve user details
        db_man = DBConnectionSelect()
        user_details = db_man.fetchone(self.username)
        del(db_man)
        return user_details

    def authenticate(self) -> None:
        #function called by the app and controls the authentication
        user_details = self.login_check()
        try:
            (username, pin) = user_details
            if str(self.pin) == str(pin):
                return {"status": True, "authcode": "y0Uh@v3Acc3ss"}  
            else:
                return {"status": False}     
        except TypeError:
                return {"status": False}
