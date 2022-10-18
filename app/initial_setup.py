import sqlite3

conn = sqlite3.connect('auth_users.db')

cur = conn.cursor()

cur.execute("""CREATE TABLE users(
        username text,
        pin text
);""")