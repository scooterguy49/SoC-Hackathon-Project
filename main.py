# split3 is used to work with a SQL database. 
# flask is the backend web framework 
# request is used to access inputs from login and signup
# session stores information accross pages
# render template renders HTML files

import sqlite3
from flask import Flask, request, redirect, session, render_template

# Creates web application using Flask. 
app = Flask(__name__)

# We want to change the secret_key to make it stronger. For now it's ok
# It's used to remmber login users
app.secret_key = "secret_key"  # required for sessions

# This is SQL database. Everything is stored here
DB = "workout_planner.db"

# Function that creates and returns a connection from database
def get_db():
    return sqlite3.connect(DB)

# Starts website
if __name__ == "__main__":
    app.run(debug=True)
