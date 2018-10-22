from flask import Flask, render_template, request,session,url_for,redirect,flash
import sqlite3
import os
import csv
import time

DB_FILE = "northpoint.db"
app = Flask(__name__)
app.secret_key=os.urandom(32)
num_of_stories = 0

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
        return render_template("welcome.html")
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

@app.route("/results", methods=['GET'])
def results():
    return render_template("results.html", Title="Results")

@app.route("/edit", methods=['GET'])
def edit():
    return render_template("edit.html", Title="Edit")

@app.route("/input_story", methods=['POST'])
def input_story():
    db = sqlite3.connect(DB_FILE)
    s = db-cursor()
    s.execute("CREATE TABLE IF NOT EXISTS stories (story_id INTEGER PRIMARY KEY, name TEXT, edit TEXT, editor TEXT, timestamp INTEGER")
    title=request.form["story_title"]
    beginning_text=request.form["story_content"]
    s.execute("INSERT INTO stories values(?,?,?,?,?)", num_of_stories + 1, title, beginning_text, session.get("uname"), int(time.time()))
    db.commit();
    db.close();
    return render_template("welcome.html")

if __name__ == "__main__":
    app.debug = True
    app.run()

