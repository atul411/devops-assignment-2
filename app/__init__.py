import os
from flask import Flask, redirect, url_for
from . import db as db_module
from .config import Config, TestConfig


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=False)

    if config_object is None:
        config_object = TestConfig if os.environ.get("FLASK_TESTING") else Config
    app.config.from_object(config_object)

    db_path = app.config["DATABASE"]
    if db_path not in (":memory:", None):
        os.makedirs(os.path.dirname(os.path.abspath(db_path)) or ".", exist_ok=True)

    db_module.init_app(app)

    with app.app_context():
        db_module.init_db()

    from .health import bp as health_bp
    app.register_blueprint(health_bp)

    feature_level = app.config["FEATURE_LEVEL"]

    if feature_level >= 1:
        from .programs import bp as programs_bp
        app.register_blueprint(programs_bp)

    if feature_level >= 2:
        from .clients import bp as clients_bp
        app.register_blueprint(clients_bp, url_prefix="/clients")

    if feature_level >= 3:
        from .auth import bp as auth_bp
        from .workouts import bp as workouts_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(workouts_bp)

    @app.route("/", methods=["GET"])
    def index():
        return redirect(url_for("programs.list_programs"))

    return app
