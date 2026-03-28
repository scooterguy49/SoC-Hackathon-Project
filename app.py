from flask import Flask, request, jsonify, render_template
import sqlite3

# Creates web application
app = Flask(__name__)
DATABASE = "workout_planner.db"

# Used for cookies and session
app.secret_key = "secret_key"

# used to connect to the database
def get_db_connection():
    connection = sqlite3.connect(DATABASE, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection

@app.route("/")
def home():
    return render_template("signup.html")


# ----------------
# User Management
# ----------------
@app.route("/users", methods=["GET"])
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, username")
    users = cursor.fetchall()

    connection.close()

    return jsonify([dict(user) for user in users])


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    username = data.get("username")
    password_hash = data.get("password_hash")

    if not username or not password_hash:
        return jsonify({"error": "username, and password_hash are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?, ?)
        """, (username, password_hash))

        connection.commit()
        new_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({"error": "Username already exists"}), 400

    connection.close()

    return jsonify({
        "message": "User created",
        "user_id": new_id
    }), 201

#----------------
# Workout Plans
#----------------

# Get all workout plans
@app.route("/plans", methods=["GET"])
def get_plans():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM workout_plans")
    plans = cursor.fetchall()

    connection.close()

    return jsonify([dict(plan) for plan in plans])

# Create a new workout plan
@app.route("/plans", methods=["POST"])
def create_plan():
    data = request.get_json()

    plan_name = data.get("plan_name")
    notes = data.get("notes", "")

    if not plan_name:
        return jsonify({"error": "plan_name is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO workout_plans (plan_name, notes)
        VALUES (?, ?)
    """, (plan_name, notes))

    connection.commit()
    new_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Workout plan created",
        "plan_id": new_id
    }), 201

#--------------
# Exercises
#--------------

# Get all exercises
@app.route("/exercises", methods=["GET"])
def get_exercises():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM exercises")
    exercises = cursor.fetchall()

    connection.close()

    return jsonify([dict(exercise) for exercise in exercises])

# Create a new exercise
@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = request.get_json()

    exercise_name = data.get("exercise_name")
    muscles_worked = data.get("muscles_worked")
    description = data.get("description", "")

    if not exercise_name or not muscles_worked:
        return jsonify({"error": "exercise_name and muscles_worked are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO exercises (exercise_name, muscles_worked, description)
        VALUES (?, ?, ?)
    """, (exercise_name, muscles_worked, description))

    connection.commit()
    new_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Exercise created",
        "exercise_id": new_id
    }), 201

#-------------------------------
# Add exercises to workout plans
#-------------------------------

@app.route("/plans/<int:plan_id>/exercises", methods=["POST"])
def add_exercise_to_plan(plan_id):
    data = request.get_json()

    exercise_id = data.get("exercise_id")
    duration_minutes = data.get("duration_minutes", 0)

    if not exercise_id:
        return jsonify({"error": "exercise_id is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check that the plan exists
    cursor.execute("SELECT * FROM workout_plans WHERE id = ?", (plan_id,))
    plan = cursor.fetchone()
    if plan is None:
        connection.close()
        return jsonify({"error": "Workout plan not found"}), 404

    # Check that the exercise exists
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    exercise = cursor.fetchone()
    if exercise is None:
        connection.close()
        return jsonify({"error": "Exercise not found"}), 404

    cursor.execute("""
        INSERT INTO workout_exercises (plan_id, exercise_id, duration_minutes)
        VALUES (?, ?, ?)
    """, (plan_id, exercise_id, duration_minutes))

    connection.commit()
    new_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Exercise added to workout plan",
        "workout_exercise_id": new_id
    }), 201


# -----------------------------
# GET ALL EXERCISES IN A PLAN
# -----------------------------

@app.route("/plans/<int:plan_id>/exercises", methods=["GET"])
def get_plan_exercises(plan_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            workout_exercises.id,
            workout_exercises.plan_id,
            workout_exercises.exercise_id,
            workout_exercises.duration_minutes,
            exercises.exercise_name,
            exercises.muscles_worked,
            exercises.description
        FROM workout_exercises
        JOIN exercises
            ON workout_exercises.exercise_id = exercises.id
        WHERE workout_exercises.plan_id = ?
    """, (plan_id,))

    exercises = cursor.fetchall()
    connection.close()

    return jsonify([dict(exercise) for exercise in exercises])


# -----------------------------
# GET TOTAL DURATION FOR A PLAN
# -----------------------------

@app.route("/plans/<int:plan_id>/total-duration", methods=["GET"])
def get_total_duration(plan_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT SUM(duration_minutes)
        FROM workout_exercises
        WHERE plan_id = ?
    """, (plan_id,))

    result = cursor.fetchone()[0]
    total_duration = result if result is not None else 0

    connection.close()

    return jsonify({
        "plan_id": plan_id,
        "total_duration_minutes": total_duration
    })


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)