"""
Authentication module for IoT device agent.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from amazing_iot_device import db, login_manager
from amazing_iot_device.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm(FlaskForm):
    """Login form for user authentication."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database."""
    return User.query.get(int(user_id))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid username or password")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for("auth.login"))


# For initial setup, create an admin user (this would be replaced with proper user management)
def init_admin(app):
    """Create an admin user if none exists."""
    with app.app_context():
        if User.query.count() == 0:
            admin = User(username="admin")
            admin.set_password("admin")  # Default password, should be changed
            db.session.add(admin)
            db.session.commit()
