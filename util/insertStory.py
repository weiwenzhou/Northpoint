import sqlite3
DB_FILE = "northpoint.db"

def insert(params):
    db = sqlite3.connect(DB_FILE)
    s = db.cursor()
    s.execute("INSERT INTO stories VALUES(?,?,?,?,?)", params)
    db.commit()
    db.close()
