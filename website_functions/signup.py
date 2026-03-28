from app import app
from flask import request, redirect, render_template
import sqlite3
import bcrypt

DB = "workout_planner.db"

def get_db():
    return sqlite3.connect(DB, check_same_thread=False)

# "/signup " is a url for website. GET shows form, POST processes form
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"

        conn.close()
        return redirect("/login")

    return render_template("signup.html")
