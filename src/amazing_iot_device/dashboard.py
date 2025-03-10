"""
Dashboard module for IoT device agent.
"""

import os
import platform

import psutil
from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    """Display the main dashboard with system information."""
    # Get system information
    system_info = {
        "os_name": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "device_version": os.environ.get("DEVICE_VERSION", "0.1.0"),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "processor": platform.processor(),
        "architecture": platform.machine(),
    }

    # Get CPU and memory usage
    resource_usage = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used": f"{psutil.virtual_memory().used / (1024**3):.2f} GB",
        "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "disk_percent": psutil.disk_usage("/").percent,
        "disk_used": f"{psutil.disk_usage('/').used / (1024**3):.2f} GB",
        "disk_total": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
    }

    return render_template(
        "dashboard/index.html", system_info=system_info, resource_usage=resource_usage
    )
