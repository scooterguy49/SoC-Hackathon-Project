from app import app
from flask import request, redirect, render_template
import sqlite3

DB = "workout_planner.db"

def get_db():
    return sqlite3.connect(DB)

# "/signup " is a url for website. GET shows form, POST processes form
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # If user submits info this runs.
    if request.method == "POST":

        # Get form data
        username = request.form["username"] 
        password = request.form["password"]

        # Save/Connect to database
        conn = get_db()
        cur = conn.cursor()

        # Insert data to database
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password)
        )

        # Saves data and closes from database
        conn.commit()
        conn.close()

        # Go to login page
        return redirect("/login")

    # If GET request, it will show the form
    return render_template("signup.html")