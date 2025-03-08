"""
Dashboard module for IoT device agent.
"""
import platform
import os
from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Display the main dashboard with system information."""
    system_info = {
        'os_name': platform.system(),
        'os_version': platform.version(),
        'os_release': platform.release(),
        'device_version': os.environ.get('DEVICE_VERSION', '0.1.0'),
        'python_version': platform.python_version(),
        'hostname': platform.node(),
        'processor': platform.processor(),
        'architecture': platform.machine()
    }
    return render_template('dashboard/index.html', system_info=system_info)