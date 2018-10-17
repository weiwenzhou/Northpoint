from flask import Flask, render_template, request,session,url_for,redirect,flash
import os
import csv
app = Flask(__name__)

app.secret_key=os.urandom(32)

@app.route("/", methods=['POST',"GET"])
def home():
    if session.get("uname"):
        return render_template("welcome.html")
    return render_template("login.html",Title = 'Login')

@app.route("/auth", methods=['POST'])
def auth():
    givenUname=request.form["username"]
    givenPwd=request.form["password"]
    if givenUname=="usr": 
        if givenPwd=="pwd":
            session["uname"]=givenUname
            if session.get("error"):
                session.pop("error")
        else:
            flash("Incorrect password")
    else:
        flash("Incorrect username")
    return redirect(url_for("home"))

@app.route("/logout", methods=['POST',"GET"])
def logout():
    if session.get("uname"):
        session.pop("uname")
        print(session)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.debug = True
    app.run()
