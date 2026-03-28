import sqlite3

# connection and cursor setup
connection = sqlite3.connect("workout_planner.db")
cursor = connection.cursor()

# One user can have many workout_plans
# One workout_plan can have many workout_exercises
# One exercise can appear in many workout_exercises


# Creates users
# Password is hashed 
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
""")

# Creates workout plans
cursor.execute("""
CREATE TABLE workout_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

# Creates exercises 
cursor.execute("""
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT NOT NULL,
    muscles_worked TEXT NOT NULL,
    description TEXT
);
""")

# connection commit and close
connection.commit()
connection.close()

print("Database created successfully!")

