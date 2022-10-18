import sqlite3
from abc import ABC

class IDBConnection(ABC):
    def __init__(self):
        self.conn = sqlite3.connect('auth_users.db')
        self.cur = self.conn.cursor()

class DBConnectionSelect(IDBConnection):
    def fetchone(self, username: str) -> tuple:
        self.cur.execute("SELECT * FROM users WHERE username = ?;",(username,))
        # self.cur.execute("SELECT * FROM users;")
        user_details = self.cur.fetchone()
        self.conn.commit()
        self.conn.close()
        return (user_details)

class DBConnectionInsert(IDBConnection):
    #class to control the insertion of data into the user db
    def account_create(self, user_details: dict) -> None:
        '''
        This method requires a dictionary of user atributes
        specifically username, email_address, salt and hash
        to create a user in the user table.
        '''
        self.cur.execute("""INSERT into users
                    (username, pin) 
                    values(?, ?,);""", 
                    (
                        user_details['username'], 
                        user_details['pin'], 
                    )
                    )
        print("Account Created")
        self.conn.commit()
        self.conn.close()