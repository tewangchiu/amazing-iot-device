"""
Settings module for IoT device agent.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError

from amazing_iot_device import db
from amazing_iot_device.models import Settings
from amazing_iot_device.mqtt_service import mqtt_service

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

class SettingForm(FlaskForm):
    """Form for updating settings."""
    value = StringField('Value', validators=[DataRequired()])
    submit = SubmitField('Update')

class MQTTSettingsForm(FlaskForm):
    """Form for MQTT settings."""
    mqtt_enabled = BooleanField('Enable MQTT Service')
    mqtt_broker_host = StringField('Broker Host', validators=[DataRequired()])
    mqtt_broker_port = IntegerField('Broker Port', validators=[DataRequired(), NumberRange(min=1, max=65535)])
    mqtt_username = StringField('Username', validators=[Optional()])
    mqtt_password = PasswordField('Password', validators=[Optional()])
    mqtt_topic_prefix = StringField('Topic Prefix', validators=[DataRequired()])
    mqtt_publish_interval = IntegerField('Publish Interval (seconds)', 
                                         validators=[DataRequired(), NumberRange(min=5, message="Interval must be at least 5 seconds")])
    submit = SubmitField('Save Settings')
    
    def validate_mqtt_broker_host(self, field):
        """Validate the host field."""
        if not field.data:
            raise ValidationError('Broker host cannot be empty')
        
    def validate_mqtt_topic_prefix(self, field):
        """Validate the topic prefix field."""
        if not field.data:
            raise ValidationError('Topic prefix cannot be empty')
        if '/' not in field.data:
            raise ValidationError('Topic prefix should include at least one hierarchy level (e.g., iot/device)')

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

@settings_bp.route('/mqtt', methods=['GET', 'POST'])
@login_required
def mqtt():
    """Manage MQTT settings."""
    form = MQTTSettingsForm()
    
    # Query all MQTT settings
    mqtt_settings = {s.key: s.value for s in Settings.query.filter(
        Settings.key.in_([
            'mqtt_enabled',
            'mqtt_broker_host',
            'mqtt_broker_port',
            'mqtt_username',
            'mqtt_password',
            'mqtt_topic_prefix',
            'mqtt_publish_interval'
        ])
    ).all()}
    
    if form.validate_on_submit():
        # Update settings in database
        settings_to_update = {
            'mqtt_enabled': 'true' if form.mqtt_enabled.data else 'false',
            'mqtt_broker_host': form.mqtt_broker_host.data,
            'mqtt_broker_port': str(form.mqtt_broker_port.data),
            'mqtt_username': form.mqtt_username.data,
            'mqtt_password': form.mqtt_password.data,
            'mqtt_topic_prefix': form.mqtt_topic_prefix.data,
            'mqtt_publish_interval': str(form.mqtt_publish_interval.data)
        }
        
        for key, value in settings_to_update.items():
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Settings(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        
        # Restart MQTT service with new settings
        mqtt_service.stop()
        if form.mqtt_enabled.data:
            mqtt_service._load_settings()
            mqtt_service._setup_mqtt_client()
            mqtt_service.start()
            flash('MQTT settings updated and service restarted!', 'success')
        else:
            flash('MQTT settings updated and service stopped!', 'warning')
            
        return redirect(url_for('settings.mqtt'))
    
    # Pre-fill the form with current values
    if request.method == 'GET':
        form.mqtt_enabled.data = mqtt_settings.get('mqtt_enabled', 'false').lower() == 'true'
        form.mqtt_broker_host.data = mqtt_settings.get('mqtt_broker_host', 'localhost')
        form.mqtt_broker_port.data = int(mqtt_settings.get('mqtt_broker_port', '1883'))
        form.mqtt_username.data = mqtt_settings.get('mqtt_username', '')
        form.mqtt_password.data = mqtt_settings.get('mqtt_password', '')
        form.mqtt_topic_prefix.data = mqtt_settings.get('mqtt_topic_prefix', 'iot/device')
        form.mqtt_publish_interval.data = int(mqtt_settings.get('mqtt_publish_interval', '60'))
    
    # Get MQTT status (connected or not)
    mqtt_status = mqtt_service.client and mqtt_service.client.is_connected() if mqtt_service.is_running else False
    
    return render_template('settings/mqtt.html', 
                          form=form, 
                          mqtt_settings=mqtt_settings, 
                          mqtt_status=mqtt_status,
                          last_published=None)  # You could track last published time

def init_default_settings(app):
    """Initialize default settings if they don't exist."""
    default_settings = {
        'device_name': 'Amazing IoT Device',
        'refresh_interval': '60',  # seconds
        'notifications_enabled': 'true',
        'theme': 'light',
        # MQTT default settings are handled in mqtt_service.py
    }
    
    with app.app_context():
        for key, value in default_settings.items():
            if not Settings.query.filter_by(key=key).first():
                setting = Settings(key=key, value=value)
                db.session.add(setting)
        db.session.commit()