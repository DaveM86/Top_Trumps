import sqlite3

conn = sqlite3.connect('users.db')

cur = conn.cursor()

# cur.execute("""CREATE TABLE users(
#         username text,
#         pin text
# );""")

