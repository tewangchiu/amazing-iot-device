#!/usr/bin/env python
"""
Run script for the Amazing IoT Device Agent application.
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from amazing_iot_device import create_app
from amazing_iot_device.auth import init_admin
from amazing_iot_device.settings import init_default_settings
from amazing_iot_device.mqtt_service import init_mqtt_service

# Create the Flask application
app = create_app()

# Initialize admin user if not exists
init_admin(app)

# Initialize default settings
init_default_settings(app)

# Initialize and start MQTT service
init_mqtt_service(app)

if __name__ == '__main__':
    # Get port from environment or use default 5000
    port = int(os.environ.get('PORT', 5050))
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=True)