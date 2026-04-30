import random
from datetime import date
from flask import Blueprint, abort, jsonify, render_template, request
from .auth import login_required
from .db import get_db

bp = Blueprint("workouts", __name__)

CLIENT_LOOKUP_SQL = "SELECT 1 FROM clients WHERE name = ?"

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}

WORKOUT_TYPES = {"Strength", "Hypertrophy", "Cardio", "Mobility"}


@bp.route("/workouts/<client_name>", methods=["GET"])
@login_required
def list_workouts(client_name):
    db = get_db()
    rows = db.execute(
        """SELECT id, date, workout_type, duration_min, notes
           FROM workouts WHERE client_name = ? ORDER BY date DESC""",
        (client_name,),
    ).fetchall()
    workouts = [dict(r) for r in rows]
    if request.args.get("format") == "json":
        return jsonify(client=client_name, workouts=workouts)
    return render_template(
        "workouts.html", client_name=client_name, workouts=workouts
    )


@bp.route("/workouts/<client_name>", methods=["POST"])
@login_required
def add_workout(client_name):
    payload = request.get_json(silent=True) or request.form
    workout_type = (payload.get("workout_type") or "").strip()
    if workout_type not in WORKOUT_TYPES:
        return jsonify(error=f"workout_type must be one of {sorted(WORKOUT_TYPES)}"), 400
    try:
        duration = int(payload.get("duration_min", 0))
    except (TypeError, ValueError):
        return jsonify(error="duration_min must be an integer"), 400
    if duration <= 0:
        return jsonify(error="duration_min must be > 0"), 400

    workout_date = payload.get("date") or date.today().isoformat()
    notes = payload.get("notes") or ""

    db = get_db()
    if db.execute(CLIENT_LOOKUP_SQL, (client_name,)).fetchone() is None:
        abort(404, description=f"client {client_name} not found")
    cur = db.execute(
        """INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (client_name, workout_date, workout_type, duration, notes),
    )
    db.commit()
    return jsonify(id=cur.lastrowid, client=client_name, date=workout_date), 201


@bp.route("/workouts/<int:workout_id>/exercises", methods=["POST"])
@login_required
def add_exercise(workout_id):
    payload = request.get_json(silent=True) or request.form
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify(error="exercise name is required"), 400
    try:
        sets = int(payload.get("sets", 0))
        reps = int(payload.get("reps", 0))
        weight = float(payload.get("weight")) if payload.get("weight") not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify(error="sets/reps must be integers, weight numeric"), 400
    if sets <= 0 or reps <= 0:
        return jsonify(error="sets and reps must be > 0"), 400

    db = get_db()
    if db.execute("SELECT 1 FROM workouts WHERE id = ?", (workout_id,)).fetchone() is None:
        abort(404, description=f"workout {workout_id} not found")
    cur = db.execute(
        """INSERT INTO exercises (workout_id, name, sets, reps, weight)
           VALUES (?, ?, ?, ?, ?)""",
        (workout_id, name, sets, reps, weight),
    )
    db.commit()
    return jsonify(id=cur.lastrowid, workout_id=workout_id, name=name), 201


@bp.route("/metrics/<client_name>", methods=["POST"])
@login_required
def add_metric(client_name):
    payload = request.get_json(silent=True) or request.form
    try:
        weight = float(payload.get("weight")) if payload.get("weight") not in (None, "") else None
        waist = float(payload.get("waist")) if payload.get("waist") not in (None, "") else None
        bodyfat = float(payload.get("bodyfat")) if payload.get("bodyfat") not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify(error="weight/waist/bodyfat must be numeric"), 400
    if all(v is None for v in (weight, waist, bodyfat)):
        return jsonify(error="at least one metric required"), 400

    metric_date = payload.get("date") or date.today().isoformat()
    db = get_db()
    if db.execute(CLIENT_LOOKUP_SQL, (client_name,)).fetchone() is None:
        abort(404, description=f"client {client_name} not found")
    db.execute(
        """INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
           VALUES (?, ?, ?, ?, ?)""",
        (client_name, metric_date, weight, waist, bodyfat),
    )
    db.commit()
    return jsonify(client=client_name, date=metric_date), 201


@bp.route("/metrics/<client_name>", methods=["GET"])
@login_required
def list_metrics(client_name):
    db = get_db()
    rows = db.execute(
        """SELECT date, weight, waist, bodyfat FROM metrics
           WHERE client_name = ? ORDER BY date""",
        (client_name,),
    ).fetchall()
    return jsonify(client=client_name, metrics=[dict(r) for r in rows])


@bp.route("/program-generator/<client_name>", methods=["POST"])
@login_required
def generate_program(client_name):
    db = get_db()
    if db.execute(CLIENT_LOOKUP_SQL, (client_name,)).fetchone() is None:
        abort(404, description=f"client {client_name} not found")
    program_type = random.choice(list(PROGRAM_TEMPLATES.keys()))
    program_detail = random.choice(PROGRAM_TEMPLATES[program_type])
    db.execute(
        "UPDATE clients SET program = ? WHERE name = ?",
        (program_detail, client_name),
    )
    db.commit()
    return jsonify(client=client_name, program_type=program_type, program=program_detail)


@bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    db = get_db()
    clients = db.execute("SELECT name, program, calories FROM clients ORDER BY name").fetchall()
    return render_template(
        "dashboard.html",
        clients=[dict(c) for c in clients],
    )
