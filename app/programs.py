from flask import Blueprint, abort, jsonify, render_template, request
from .models import PROGRAMS, SITE_METRICS, calorie_for, get_program

bp = Blueprint("programs", __name__)


@bp.route("/programs", methods=["GET"])
def list_programs():
    if request.accept_mimetypes.best == "application/json" or \
            request.args.get("format") == "json":
        return jsonify(programs=list(PROGRAMS.values()), site=SITE_METRICS)
    return render_template(
        "programs.html",
        programs=PROGRAMS,
        site=SITE_METRICS,
    )


@bp.route("/programs/<key>", methods=["GET"])
def get_program_view(key):
    program = get_program(key)
    if program is None:
        abort(404, description=f"Program {key} not found")
    if request.args.get("format") == "json":
        return jsonify(program)
    return render_template("program_detail.html", program=program)


@bp.route("/programs/<key>/calories", methods=["GET"])
def calorie_calc(key):
    weight = request.args.get("weight", type=float)
    if weight is None:
        return jsonify(error="weight query parameter required"), 400
    try:
        calories = calorie_for(weight, key)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(program=key.upper(), weight=weight, calories=calories)
