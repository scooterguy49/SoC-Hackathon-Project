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
    password_hash TEXT NOT NULL
)
""")

# Creates workout plans
cursor.execute("""
CREATE TABLE workout_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Creates workout exercises 
cursor.execute("""
CREATE TABLE workout_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    duration_minutes INTEGER,
    FOREIGN KEY (plan_id) REFERENCES workout_plans(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
)
""")

# Creates exercises 
cursor.execute("""
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT NOT NULL,
    muscles_worked TEXT NOT NULL
)
""")



# connection commit and close
connection.commit()
connection.close()

print("Database created successfully!")

