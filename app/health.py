from flask import Blueprint, current_app, jsonify
from . import db as db_module

bp = Blueprint("health", __name__)


@bp.route("/health")
def health():
    return jsonify(
        status="ok",
        version=current_app.config["APP_VERSION"],
        feature_level=current_app.config["FEATURE_LEVEL"],
    )


@bp.route("/ready")
def ready():
    try:
        conn = db_module.get_db()
        conn.execute("SELECT 1").fetchone()
        return jsonify(status="ready"), 200
    except Exception as exc:
        return jsonify(status="not-ready", error=str(exc)), 503
