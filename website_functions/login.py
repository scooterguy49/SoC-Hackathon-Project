from app import app
from flask import request, redirect, session, render_template
import sqlite3

# defines database
DB = "workout_planner.db"

# creates and returns database 
def get_db():
    return sqlite3.connect(DB)


# "/login " is a url for website. GET shows form, POST processes form
@app.route("/login", methods=["GET", "POST"])
def login():

    # If user submits info this runs
    if request.method == "POST":

        # Get form data
        username = request.form["username"]
        password = request.form["password"]

        # Look up user in database
        conn = get_db()
        cur = conn.cursor()

        # Finds the user with that username
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        conn.close()

        # Check if user exists AND password matches
        if user and user[2] == password:
            session["user_id"] = user[0]  # log them in
            return redirect("/dashboard")
        else:
            return "Invalid login"

    # If GET request → show login page
    return render_template("login.html")