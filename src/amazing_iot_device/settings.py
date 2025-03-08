"""
Settings module for IoT device agent.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from amazing_iot_device import db
from amazing_iot_device.models import Settings

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

class SettingForm(FlaskForm):
    """Form for updating settings."""
    value = StringField('Value', validators=[DataRequired()])
    submit = SubmitField('Update')

@settings_bp.route('/')
@login_required
def index():
    """Display all available settings."""
    settings = Settings.query.all()
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/edit/<key>', methods=['GET', 'POST'])
@login_required
def edit(key):
    """Edit a specific setting value."""
    setting = Settings.query.filter_by(key=key).first_or_404()
    form = SettingForm()
    
    if form.validate_on_submit():
        setting.value = form.value.data
        db.session.commit()
        flash(f'Setting {key} updated successfully!')
        return redirect(url_for('settings.index'))
    
    # Pre-fill the form with the current setting value
    if request.method == 'GET':
        form.value.data = setting.value
    
    return render_template('settings/edit.html', form=form, setting=setting)

def init_default_settings(app):
    """Initialize default settings if they don't exist."""
    default_settings = {
        'device_name': 'Amazing IoT Device',
        'refresh_interval': '60',  # seconds
        'notifications_enabled': 'true',
        'theme': 'light',
    }
    
    with app.app_context():
        for key, value in default_settings.items():
            if not Settings.query.filter_by(key=key).first():
                setting = Settings(key=key, value=value)
                db.session.add(setting)
        db.session.commit()