from functools import wraps
from flask import (
    Blueprint, flash, jsonify, redirect, render_template,
    request, session, url_for,
)
from werkzeug.security import check_password_hash
from .db import get_db

bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            wants_json = (
                request.is_json
                or request.path.startswith("/api/")
                or request.path in ("/me",)
                or request.accept_mimetypes.best == "application/json"
            )
            if wants_json:
                return jsonify(error="authentication required"), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "Admin":
            return jsonify(error="admin only"), 403
        return view(*args, **kwargs)
    return wrapped


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""

        db = get_db()
        row = db.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if row is None or not check_password_hash(row["password_hash"], password):
            if request.is_json:
                return jsonify(error="invalid credentials"), 401
            flash("Invalid credentials")
            return render_template("login.html"), 401

        session.clear()
        session["user"] = row["username"]
        session["role"] = row["role"]
        if request.is_json:
            return jsonify(user=row["username"], role=row["role"])
        return redirect(url_for("clients.list_clients"))

    return render_template("login.html")


@bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    if request.is_json or request.method == "GET":
        return jsonify(status="logged out") if request.is_json else redirect(
            url_for("programs.list_programs")
        )
    return jsonify(status="logged out")


@bp.route("/me")
@login_required
def me():
    return jsonify(user=session.get("user"), role=session.get("role"))
