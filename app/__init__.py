import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask

from config import config_by_name
from .extensions import bcrypt, csrf, db, login_manager


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    env_name = config_name or app.config.get("ENV") or "default"
    app.config.from_object(config_by_name.get(env_name, config_by_name["default"]))

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.student_login"
    login_manager.login_message_category = "warning"

    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)
    configure_logging(app)

    return app


def register_blueprints(app):
    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.student import student_bp
    from .routes.tpo import tpo_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(tpo_bp)


def register_error_handlers(app):
    from .errors.handlers import forbidden, not_found, server_error

    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(500, server_error)


def register_cli(app):
    from .models import User

    @app.cli.command("init-db")
    def init_db():
        """Create database tables."""
        db.create_all()
        print("Database tables created.")

    @app.cli.command("upgrade-db")
    def upgrade_db():
        """Upgrade old raw-SQL tables to the refactored ORM shape."""
        from .utils import upgrade_legacy_schema

        upgrade_legacy_schema()
        print("Database schema upgraded.")

    @app.cli.command("create-admin")
    def create_admin():
        """Create the first admin using ADMIN_* values from .env."""
        import os

        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        if not all([username, email, password]):
            print("Set ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD in .env first.")
            return
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("Admin user already exists.")
            return
        user = User(username=username, email=email, role="admin", is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("Admin user created.")

    @app.cli.command("create-tpo")
    def create_tpo():
        """Create a TPO user using TPO_* values from .env."""
        import os

        username = os.getenv("TPO_USERNAME")
        email = os.getenv("TPO_EMAIL")
        password = os.getenv("TPO_PASSWORD")
        if not all([username, email, password]):
            print("Set TPO_USERNAME, TPO_EMAIL, and TPO_PASSWORD in .env first.")
            return
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("TPO user already exists.")
            return
        user = User(username=username, email=email, role="tpo", is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("TPO user created.")


def configure_logging(app):
    if app.debug:
        return
    log_dir = Path(app.instance_path) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_dir / "app.log", maxBytes=1024 * 1024, backupCount=5)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
