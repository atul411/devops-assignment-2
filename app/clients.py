from datetime import datetime
from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from .db import get_db
from .models import calorie_for, get_program

bp = Blueprint("clients", __name__)


def _row_to_dict(row):
    return {key: row[key] for key in row.keys()} if row else None


@bp.route("/", methods=["GET"])
def list_clients():
    db = get_db()
    rows = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
    clients = [_row_to_dict(r) for r in rows]
    if request.args.get("format") == "json":
        return jsonify(clients=clients)
    return render_template("client_list.html", clients=clients)


@bp.route("/", methods=["POST"])
def create_client():
    payload = request.get_json(silent=True) or request.form
    name = (payload.get("name") or "").strip()
    program = (payload.get("program") or "").strip().upper()
    if not name:
        return jsonify(error="name is required"), 400
    if not program or get_program(program) is None:
        return jsonify(error="program must be one of FL, MG, BG"), 400

    try:
        age = int(payload.get("age")) if payload.get("age") not in (None, "") else None
        height = float(payload.get("height")) if payload.get("height") not in (None, "") else None
        weight = float(payload.get("weight")) if payload.get("weight") not in (None, "") else None
        target_weight = float(payload.get("target_weight")) if payload.get("target_weight") not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify(error="age/height/weight/target_weight must be numeric"), 400

    calories = None
    if weight is not None:
        try:
            calories = calorie_for(weight, program)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400

    db = get_db()
    try:
        cur = db.execute(
            """INSERT INTO clients (name, age, height, weight, program, calories,
               target_weight, membership_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')""",
            (name, age, height, weight, program, calories, target_weight),
        )
        db.commit()
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return jsonify(error=f"client {name} already exists"), 409
        return jsonify(error=str(exc)), 500

    if request.is_json:
        return jsonify(id=cur.lastrowid, name=name, program=program, calories=calories), 201
    return redirect(url_for("clients.get_client", name=name))


@bp.route("/<name>", methods=["GET"])
def get_client(name):
    db = get_db()
    row = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if row is None:
        abort(404, description=f"client {name} not found")
    progress = db.execute(
        "SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY id",
        (name,),
    ).fetchall()
    progress_list = [{"week": p["week"], "adherence": p["adherence"]} for p in progress]
    if request.args.get("format") == "json":
        return jsonify(client=_row_to_dict(row), progress=progress_list)
    return render_template(
        "client_detail.html",
        client=_row_to_dict(row),
        progress=progress_list,
    )


@bp.route("/<name>", methods=["PUT", "PATCH"])
def update_client(name):
    payload = request.get_json(silent=True) or request.form
    db = get_db()
    row = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if row is None:
        abort(404, description=f"client {name} not found")

    fields = {}
    for key in ("age", "height", "weight", "target_weight"):
        if key in payload and payload.get(key) not in (None, ""):
            try:
                fields[key] = float(payload.get(key))
            except (TypeError, ValueError):
                return jsonify(error=f"{key} must be numeric"), 400
    if payload.get("program"):
        program = payload.get("program").upper()
        if get_program(program) is None:
            return jsonify(error="program must be FL, MG, or BG"), 400
        fields["program"] = program

    weight = fields.get("weight", row["weight"])
    program = fields.get("program", row["program"])
    if weight and program:
        fields["calories"] = calorie_for(weight, program)

    if not fields:
        return jsonify(error="no updatable fields supplied"), 400

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [name]
    db.execute(f"UPDATE clients SET {set_clause} WHERE name = ?", values)
    db.commit()
    return jsonify(updated=name, fields=list(fields.keys()))


@bp.route("/<name>", methods=["DELETE"])
def delete_client(name):
    db = get_db()
    cur = db.execute("DELETE FROM clients WHERE name = ?", (name,))
    db.commit()
    if cur.rowcount == 0:
        abort(404, description=f"client {name} not found")
    return jsonify(deleted=name)


@bp.route("/<name>/progress", methods=["POST"])
def add_progress(name):
    payload = request.get_json(silent=True) or request.form
    try:
        adherence = int(payload.get("adherence"))
    except (TypeError, ValueError):
        return jsonify(error="adherence must be an integer 0-100"), 400
    if not 0 <= adherence <= 100:
        return jsonify(error="adherence must be 0-100"), 400

    week = payload.get("week") or datetime.utcnow().strftime("Week %U - %Y")

    db = get_db()
    if db.execute("SELECT 1 FROM clients WHERE name = ?", (name,)).fetchone() is None:
        abort(404, description=f"client {name} not found")
    db.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (name, week, adherence),
    )
    db.commit()
    return jsonify(client=name, week=week, adherence=adherence), 201


@bp.route("/<name>/progress", methods=["GET"])
def list_progress(name):
    db = get_db()
    rows = db.execute(
        "SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY id",
        (name,),
    ).fetchall()
    return jsonify(client=name, progress=[dict(r) for r in rows])
