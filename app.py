from flask import Flask, request, jsonify, render_template, session
import sqlite3
import os
from dotenv import load_dotenv

# Creates web application
app = Flask(__name__)
DATABASE = "workout_planner.db"

# Used for cookies and session. We get key from env file
load_dotenv("key.env")  
app.secret_key = os.getenv("SECRET_KEY")

# used to connect to the database
def get_db_connection():
    try:
        connection = sqlite3.connect(DATABASE, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")

#Global Error Handling
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad Request", "details":str(e)}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource Not Found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# Routes to login
@app.route("/")
def home():
    return render_template("login.html")

# User Management. Gets all user info from database
@app.route("/users", methods=["GET"])
def get_users():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        return jsonify([dict(user) for user in users])
    except sqlite3.Error as e:
        return jsonify({"error": "Failed to fetch users", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()



@app.route("/users", methods=["POST"])
def create_user():
    connection = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        username = data.get("username")
        password_hash = data.get("password_hash")

        if not username or not password_hash:
            return jsonify({"error": "username, and password_hash are required"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

    
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, (username, password_hash))

        connection.commit()
        new_id = cursor.lastrowid
        return jsonify({"message": "User Created", "user_id": new_id}), 201
    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.Error as e:
        return jsonify({"error": "Database Error", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()

#----------------
# Workout Plans
#----------------

# Get all workout plans
@app.route("/plans", methods=["GET"])
def get_plans():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        user_id = session["user_id"]

        cursor.execute("""
            SELECT * FROM workout_plans
            WHERE user_id = ?
        """, (user_id,))

        plans = cursor.fetchall()
        return jsonify([dict(plan) for plan in plans])
    except sqlite3.Error as e:
        return jsonify({"error": "Failed to fetch plans", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Create a new workout plan

@app.route("/plans", methods=["POST"])
def create_plan():
    connection = None
    try:
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
 
        plan_name = data.get("plan_name", "").strip()
 
        if not plan_name:
            return jsonify({"error": "plan_name is required"}), 400
 
        user_id = session["user_id"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO workout_plans (user_id, plan_name)
            VALUES (?, ?)
        """, (user_id, plan_name))

        connection.commit()
        new_id = cursor.lastrowid

        return jsonify({"message": "Workout plan created", "plan_id": new_id}), 201
 
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()

#--------------
# Exercises
#--------------

# Get all exercises
@app.route("/exercises", methods=["GET"])
def get_exercises():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM exercises")
        exercises = cursor.fetchall()
        return jsonify([dict(exercise) for exercise in exercises])
    except sqlite3.Error as e:
        return jsonify({"error": "Failed to fetch exercises", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Create a new exercise
@app.route("/exercises", methods=["POST"])
def create_exercise():
    connection = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
 
        exercise_name = data.get("exercise_name", "").strip()
        muscles_worked = data.get("muscles_worked", "").strip()
        description = data.get("description", "").strip()
 
        if not exercise_name or not muscles_worked:
            return jsonify({"error": "exercise_name and muscles_worked are required"}), 400
 
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO exercises (exercise_name, muscles_worked, description) VALUES (?, ?, ?)",
            (exercise_name, muscles_worked, description)
        )
        connection.commit()
        new_id = cursor.lastrowid
        return jsonify({"message": "Exercise created", "exercise_id": new_id}), 201
 
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()

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
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
 
        cursor.execute("SELECT id FROM workout_plans WHERE id = ?", (plan_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Workout plan not found"}), 404
 
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
            JOIN exercises ON workout_exercises.exercise_id = exercises.id
            WHERE workout_exercises.plan_id = ?
        """, (plan_id,))
 
        exercises = cursor.fetchall()
        return jsonify([dict(exercise) for exercise in exercises])
 
    except sqlite3.Error as e:
        return jsonify({"error": "Failed to fetch plan exercises", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()


# -----------------------------
# GET TOTAL DURATION FOR A PLAN
# -----------------------------

@app.route("/plans/<int:plan_id>/total-duration", methods=["GET"])
def get_total_duration(plan_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
 
        cursor.execute("SELECT id FROM workout_plans WHERE id = ?", (plan_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Workout plan not found"}), 404
 
        cursor.execute("SELECT SUM(duration_minutes) FROM workout_exercises WHERE plan_id = ?", (plan_id,))
        result = cursor.fetchone()[0]
        total_duration = result if result is not None else 0
        return jsonify({"plan_id": plan_id, "total_duration_minutes": total_duration})
 
    except sqlite3.Error as e:
        return jsonify({"error": "Failed to calculate duration", "details": str(e)}), 500
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)