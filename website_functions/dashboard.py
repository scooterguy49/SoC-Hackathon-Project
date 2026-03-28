from app import app
from flask import request, redirect, session, render_template
import sqlite3

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")