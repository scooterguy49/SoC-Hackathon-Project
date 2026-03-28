from app import app
from flask import request, redirect, session, render_template, jsonify
import sqlite3

DB = "workout_planner.db"

def get_db():
    return sqlite3.connect(DB, check_same_thread=False)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/dashboard/save", methods=["POST"])
def save_dashboard():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    exercises = data.get("exercises", [])

    conn = get_db()
    cur = conn.cursor()

    user_id = session["user_id"]

    # Get or create workout plan for user
    cur.execute("SELECT id FROM workout_plans WHERE user_id = ?", (user_id,))
    plan = cur.fetchone()

    if plan:
        plan_id = plan[0]
    else:
        cur.execute(
            "INSERT INTO workout_plans (user_id, plan_name) VALUES (?, ?)",
            (user_id, "My Plan")
        )
        plan_id = cur.lastrowid

    for ex in exercises:
        name = ex.get("exercise")
        time = ex.get("time")
        muscles = ex.get("muscles")

        if not name:
            continue

        cur.execute("""
            SELECT id FROM exercises 
            WHERE exercise_name = ? AND muscles_worked = ?
        """, (name, muscles))

        row = cur.fetchone()

        if row:
            exercise_id = row[0]
        else:
            # Insert only if it does not exist
            cur.execute("""
                INSERT INTO exercises (exercise_name, muscles_worked)
                VALUES (?, ?)
            """, (name, muscles))
            exercise_id = cur.lastrowid

        # Link exercise to workout plan
        cur.execute("""
            INSERT INTO workout_exercises (plan_id, exercise_id, duration_minutes)
            VALUES (?, ?, ?)
        """, (plan_id, exercise_id, time))

    conn.commit()
    conn.close()

    return jsonify({"message": "Saved successfully"})