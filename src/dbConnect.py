import sqlite3

# =================== db connection =======================
connection = sqlite3.connect('../data/main.db')
cursor = connection.cursor()
# print(cursor.execute('select * from lib_user').fetchall())
