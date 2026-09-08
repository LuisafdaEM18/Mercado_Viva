from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db
from auth import auth_bp
from returns import returns_bp


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_overrides:
        app.config.update(config_overrides)

    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if db_uri.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri.replace("postgres://", "postgresql://", 1)

    db.init_app(app)
    CORS(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(returns_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app
