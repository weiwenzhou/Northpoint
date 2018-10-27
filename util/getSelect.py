import sqlite3
DB_FILE = "northpoint.db"
def getAll(query):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute(query)
    result = c.fetchall()
    db.commit()
    db.close()
    return result

def getFirst(query):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute(query)
    result = c.fetchone()[0]
    db.commit()
    db.close()
    return result
