"""
Amazing IoT Device Agent
------------------------
A Flask-based web application for IoT device management.
"""

import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()
# Initialize LoginManager
login_manager = LoginManager()


def create_app(test_config=None):
    """
    Create and configure the Flask application
    """
    app = Flask(__name__, instance_relative_config=True)

    # Configure default settings
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),  # Should be overridden in production
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "device.sqlite"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # Load the instance config, if it exists
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:  # noqa: SIM105
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Register blueprints
    from amazing_iot_device.auth import auth_bp
    from amazing_iot_device.dashboard import dashboard_bp
    from amazing_iot_device.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)

    # Create a route for the index page that redirects to dashboard if logged in
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    # Make current_user available to templates
    @app.context_processor
    def inject_user():
        return {"current_user": current_user}

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
