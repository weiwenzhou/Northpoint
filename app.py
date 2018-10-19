from flask import Flask, render_template, request,session,url_for,redirect,flash
import sqlite3
import os
import csv

DB_FILE = "northpoint.db"

app = Flask(__name__)
app.secret_key=os.urandom(32)

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("home.html", Title="Northpoint's Story Thingie")

@app.route("/register", methods=['POST', 'GET'])
def register():
    return render_template("register.html", Title='Yeeters')

@app.route("/login", methods=['POST',"GET"])
def login():
    if session.get("uname"):
        return render_template("welcome.html")
    return render_template("login.html",Title = 'Login')

@app.route("/auth", methods=['POST'])
def auth():
    db = sqlite3.connect(DB_FILE)
    u = db.cursor()
    u.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, pwd TEXT)")
    givenUname=request.form["username"]
    givenPwd=request.form["password"]
    u.execute("SELECT name, pwd FROM users");
    for person in u:
        print(person[0], person[1])
        if givenUname==person[0]:
            if givenPwd==person[1]:
                session["uname"]=givenUname
                if session.get("error"):
                        session.pop("error")
            else:
                flash("Incorrect password")#means password was wrong
        else:
            flash("Incorrect username")#username was wrong

    db.commit();
    db.close();
    return redirect(url_for("login"))

@app.route("/logout", methods=['POST',"GET"])
def logout():
    if session.get("uname"):
        session.pop("uname")
        print(session)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.debug = True
    app.run()

