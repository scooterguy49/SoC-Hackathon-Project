import sqlite3
from flask import Flask, request, jsonify, g

app = Flask(__name__)
DATABASE = "workout_planner.db"

# Retrieves Database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# Closes Database
@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# Basic endpoint to check if API is running
@app.route("/")
def home():
    return {"message": "Workout Planner API is running"}

# Workout Plan Endpoints
@app.route("/plans", methods=["GET"])
def get_plans():
    db = get_db()
    plans = db.execute("SELECT * FROM workout_plans").fetchall()
    return jsonify([dict(plan) for plan in plans])

# Endpoint to create a new workout plan
@app.route("/plans", methods=["POST"])
def create_plan():
    data = request.get_json()

    plan_name = data.get("plan_name")
    goal = data.get("goal")

    if not plan_name:
        return jsonify({"error": "plan_name is required"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO workout_plans (plan_name, goal) VALUES (?, ?)",
        (plan_name, goal)
    )
    db.commit()

    return jsonify({
        "message": "Workout plan created",
        "id": cursor.lastrowid
    }), 201

# Workout Day Endpoints
@app.route("/days", methods=["POST"])
def create_day():
    data = request.get_json()

    plan_id = data.get("plan_id")
    day_name = data.get("day_name")
    notes = data.get("notes")

    if not plan_id or not day_name:
        return jsonify({"error": "plan_id and day_name are required"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO workout_days (plan_id, day_name, notes) VALUES (?, ?, ?)",
        (plan_id, day_name, notes)
    )
    db.commit()

    return jsonify({
        "message": "Workout day created",
        "id": cursor.lastrowid
    }), 201

# Exercise Log Endpoints
@app.route("/logs", methods=["POST"])
def create_log():
    data = request.get_json()

    # Required fields: workout_day_id, exercise_name, sets, reps
    workout_day_id = data.get("workout_day_id")
    exercise_name = data.get("exercise_name")
    sets = data.get("sets")
    reps = data.get("reps")
    weight = data.get("weight")
    notes = data.get("notes")

    # Validate required fields
    if not all([workout_day_id, exercise_name, sets, reps]):
        return jsonify({
            "error": "workout_day_id, exercise_name, sets, and reps are required"
        }), 400

    db = get_db()
    cursor = db.execute("""
        INSERT INTO exercise_logs
        (workout_day_id, exercise_name, sets, reps, weight, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (workout_day_id, exercise_name, sets, reps, weight, notes))
    db.commit()

    return jsonify({
        "message": "Exercise log created",
        "id": cursor.lastrowid
    }), 201

if __name__ == "__main__":
    app.run(debug=True)