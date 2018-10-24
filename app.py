from flask import Flask, render_template, request,session,url_for,redirect,flash
import sqlite3
import os
import csv
import time

DB_FILE = "northpoint.db"
app = Flask(__name__)
app.secret_key=os.urandom(32)
num_of_stories = 0
story_title = ""
edit_story_title = ""

db = sqlite3.connect(DB_FILE)
c = db.cursor()
c.execute("CREATE TABLE IF NOT EXISTS stories (story_id INTEGER, name TEXT, edit TEXT, editor TEXT, timestamp INTEGER)")
#c.execute("IF SELECT COUNT(*) FROM stories = 0 THEN INSERT VALUES (0, 'default', 'default-content', 'default-editor', 0)") #how do we do the if statement??

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("home.html", Title="Northpoint's Story Thingie")

#=============================================================
# LOGIN/REGISTER
#=============================================================

@app.route("/register", methods=['POST', 'GET'])
def register():
    if session.get("new_username"):
        return render_template("welcome.html")
    return render_template("register.html", Title='Yeeters')

@app.route("/login", methods=['POST',"GET"])
def login():
    #print(session)
    if session.get("uname"):
        username = session.get("uname")
        db = sqlite3.connect(DB_FILE)
        u = db.cursor()
        v = db.cursor()

        u.execute("SELECT name FROM stories WHERE stories.editor = (?)", (username,)) #edited
        v.execute("SELECT name FROM stories WHERE NOT stories.editor = (?)", (username,)) #non-edited
        return render_template("welcome.html", stories=u, noeditstories=v)
    return render_template("login.html",Title = 'Login')

@app.route("/auth", methods=['POST'])
def auth():
    db = sqlite3.connect(DB_FILE)
    u = db.cursor()
    u.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, pwd TEXT)")
    givenUname=request.form["username"]
    givenPwd=request.form["password"]
    u.execute("SELECT name, pwd FROM users");
    found = False #if the user is found
    for person in u:
        #print(person[0], person[1])
        if givenUname==person[0]:
            found = True
            if givenPwd==person[1]:
                session["uname"]=givenUname
                if session.get("error"):
                        session.pop("error")
            else:
                flash("Incorrect password")#means password was wrong
        if (found):
            break #exit for loop is user is found
    if (not found):
        flash("Incorrect username")#username was wrong
    db.commit();
    db.close();
    return redirect(url_for("login"))

@app.route("/create_account", methods=['POST'])
def create_account():
    db = sqlite3.connect(DB_FILE)
    u = db.cursor()
    u.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, pwd TEXT)")
    givenUname=request.form["new_username"]
    givenPwdA=request.form["new_pass"]
    givenPwdB=request.form["confirm_pass"]
    u.execute("SELECT name, pwd FROM users");
    for person in u:
        if givenUname==person[0]:
            flash("Username taken")# username already exists
    if givenPwdA != givenPwdB:
        flash("Passwords don\'t match") # given passwords don't match
    else:
        u.execute("INSERT INTO users values(?,?)", (givenUname, givenPwdA))
    db.commit();
    db.close();
    return redirect(url_for("home"))

@app.route("/logout", methods=['POST',"GET"])
def logout():
    if session.get("uname"):
        session.pop("uname")
        #print(session)
    return redirect(url_for("home"))

#=============================================================
# STORIES
#=============================================================
@app.route("/create_story", methods=['POST', 'GET'])
def create_story():
    return render_template("create.html", Title="tis make story")
"""
@app.route("/results", methods=['GET'])
def results():
    db = sqlite3.connect(DB_FILE)
    s = db.cursor()
    search=request.form["search_term"]
    s.execute("SELECT {0},{1},{2},{3} FROM {4} WHERE regexp_like({5},{6},'i')".format("story_id","name", "editor", "timestamp", "name", "search")
    for row in s:
        print(row)
    db.commit();
    db.close();
    return render_template("results.html", Title="Results")
"""
@app.route("/input_story", methods=['POST'])
def input_story():
    db = sqlite3.connect(DB_FILE)
    s = db.cursor()
    title=request.form["story_title"]
    beginning_text=request.form["story_content"]

    s.execute("SELECT MAX(story_id) FROM stories")
    if s.fetchone()[0] is int:
        num_of_stories = s.fetchone()[0] + 1
    else:
        num_of_stories = 0
    print("NUM OF STORES:", num_of_stories)
    params = (num_of_stories, title, beginning_text, session.get("uname"), int(time.time()))
    s.execute("INSERT INTO stories VALUES(?,?,?,?,?)", params)
    db.commit();
    db.close();
    return redirect(url_for("login"))

@app.route("/edit")
def edit():
    edit_story_title = request.args['title']
    print(edit_story_title)
    return render_template("edit.html", Title="Edit", e_story_title = edit_story_title)

@app.route("/edit_story")
def edit_story():
    db = sqlite3.connect(DB_FILE)
    s = db.cursor()
    title = request.form['title']
    print("TITLE: ", title)
    s.execute("SELECT story_id FROM stories WHERE stories.name = (?)", (title,))
    num = s.fetchone()[0]
    edits = request.form["story_content"]
    s.execute("INSERT INTO stories VALUES(?,?,?,?,?)", (num, title, edits, session.get("uname"), int(time.time())))
    db.commit();
    db.close();
    return redirect(url_for("login"))



@app.route("/story") #was tryna do something but didn't work
def show_story():
    story_title = request.args['title']
    db = sqlite3.connect(DB_FILE)
    s = db.cursor()

    editted = s.execute("SELECT editor FROM stories WHERE stories.name = (?)", (story_title,))

    #if the user is amongst the editors
    for user in editted:
        if user[0] == session.get('uname'):
            story_content = []
            edits = s.execute("SELECT * FROM stories WHERE stories.name = (?)", (story_title,))
            for s_id in edits:
                story_content.append((s_id[2]))
            return render_template("story.html", title=story_title, content=story_content)

    #if the user is not amongst the editors
    s.execute("SELECT MAX(timestamp) FROM stories WHERE stories.name = (?)", (story_title,))
    highest_time = s.fetchone()[0]
    print(highest_time)
    s.execute("SELECT edit FROM stories WHERE timestamp = (?)", (highest_time,))
    latest_edit = s.fetchone()[0]
    story_content = [latest_edit]
    db.commit()
    db.close()

    return render_template("story.html", title=story_title, content=story_content)



if __name__ == "__main__":
    app.debug = True
    app.run()
