from flask import Flask, render_template, request,session,url_for,redirect,flash
import sqlite3
import os
import csv
import time
import util.getSelect as getSelect
import util.insertStory as insertStory

DB_FILE = "northpoint.db"
app = Flask(__name__)
app.secret_key=os.urandom(32)
num_of_stories = 0
story_title = ""
edit_story_title = ""

db = sqlite3.connect(DB_FILE)
c = db.cursor()
#Creating our tables in our database
c.execute("CREATE TABLE IF NOT EXISTS stories (story_id INTEGER, name TEXT, edit TEXT, editor TEXT, timestamp INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, pwd TEXT)")

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("home.html", Title="The Northpoint Goldfish Storytelling")

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
        editted = getSelect.getAll("SELECT DISTINCT name FROM stories WHERE stories.editor = '{0}'".format(username)) #editted
        not_editted = getSelect.getAll("SELECT DISTINCT name FROM stories WHERE NOT stories.editor = '{0}'".format(username)) #non-edited
        print('editted', 'before', editted)
        not_editted_temp = []
        for i in not_editted:
            not_editted_temp.append(i)

        for each in not_editted:
            if each in editted:
                not_editted_temp.remove(each)
        not_editted = not_editted_temp

        print('not_editted', 'after', not_editted)
        print('editted', 'after', editted)
        return render_template("welcome.html", stories=editted, noeditstories=not_editted)
    return render_template("login.html",Title = 'Login')

@app.route("/auth", methods=['POST'])
def auth():
    db = sqlite3.connect(DB_FILE)
    u = db.cursor()
    givenUname=request.form["username"]
    givenPwd=request.form["password"]
    u.execute("SELECT name, pwd FROM users");
    found = False #if the user is found
    for person in u: #for every person in the users table
        if givenUname==person[0]:
            found = True #user exists
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
        if givenUname==person[0]: #checks if your username is unique
            flash("Username taken")# username already exists
            return render_template("register.html")
    if givenPwdA != givenPwdB:
        flash("Passwords don\'t match") # given passwords don't match
        return render_template("register.html")
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

'''
Used in our search bar.
Takes the input from the user and outputs the data from least recent to most recent.
'''
@app.route("/results", methods=['GET'])
def results():
    search=request.args["search_term"]
    #selects stories that contain the text the user has searched anywhere in it's name
    command = "SELECT name, editor FROM stories WHERE name LIKE '%{0}%' GROUP BY name ORDER BY timestamp;".format(search)
    results = getSelect.getAll(command)
    authors = []
    for each in results:
        author = og_author(each[0])
        authors.append(author)
    count = len(results)
    return render_template("results.html", current_search=search, search_results=results, author_results=authors, result_count=count)

'''
Used when user wants to create a story
First checks if the title is a duplicate title from any other story
If the title already exists, users will have to use a different one.
If not, the story will get placed in our stories database.
'''

@app.route("/input_story", methods=['POST'])
def input_story():
    title=request.form["story_title"]
    beginning_text=request.form["story_content"]
    if getSelect.getAll("SELECT name FROM stories WHERE stories.name = '{0}'".format(title)): #returns true if title already exists
        print("TITLE ALREADY EXISTS")
        flash("Please input a different title")
        return redirect(url_for("create_story"))
    else:
        print("FETCHONE RETURNS INT")
        num_of_stories = int(getSelect.getFirst("SELECT MAX(story_id) FROM stories")) + 1
        print("NUM OF STORES:", num_of_stories)
        insertStory.insert((num_of_stories, title, beginning_text, session.get("uname"), int(time.time())))
        return redirect(url_for("login"))

'''
Used when users want to edit a story
'''
@app.route("/edit_story")
def edit_story():
    print("Request args:", request.args)
    print(request.form)
    title = request.args['story_title']
    print("TITLE: ", title)
    num = getSelect.getFirst("SELECT story_id FROM stories WHERE stories.name = '{0}'".format(title))
    edits = request.args["story_content"]
    insertStory.insert((num, title, edits, session.get("uname"), int(time.time()))) #inserts edits into database
    return redirect(url_for("login"))



@app.route("/story")
def show_story():
    story_title = request.args['title']
    db = sqlite3.connect(DB_FILE)
    s = db.cursor()

    editted = s.execute("SELECT DISTINCT editor FROM stories WHERE stories.name = (?)", (story_title,)).fetchall()
    first_author = og_author(story_title)

    #if the user is amongst the editors
    for user_tuple in editted:
        if session.get('uname') in user_tuple[0]:
            story_content = []
            edits = s.execute("SELECT * FROM stories WHERE stories.name = (?)", (story_title,))
            for edit in edits:
                story_content.append((edit[2]))
            is_edited = True
            return render_template("story.html", title=story_title, content=story_content, author=first_author, edited_status=is_edited)

    #if the user is not amongst the editors
    highest_time = getSelect.getFirst("SELECT MAX(timestamp) FROM stories WHERE stories.name = '{0}'".format(story_title))
    latest_edit = getSelect.getFirst("SELECT edit FROM stories WHERE timestamp = {0}".format(highest_time))
    story_content = [latest_edit]
    is_edited = False
    db.commit()
    db.close()
    return render_template("story.html", title=story_title, content=story_content, author=first_author, edited_status=is_edited)

#=====================================
# MISC FUNCTIONS
#=====================================

def og_author(story_title):
    first_time = getSelect.getFirst("SELECT MIN(timestamp) FROM stories WHERE stories.name = '{0}'".format(story_title))
    first_author = getSelect.getFirst("SELECT editor FROM stories WHERE stories.name = '{0}' AND stories.timestamp = {1}".format(story_title, first_time))
    return first_author

if __name__ == "__main__":
    app.debug = True
    app.run()
