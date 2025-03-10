"""
Tests for dashboard functionality
"""
from unittest.mock import patch


def test_dashboard_access(client, auth):
    """Test dashboard access requires authentication."""
    # Unauthenticated access should redirect
    response = client.get('/dashboard/')
    assert response.status_code == 302

    # Authenticated access should load successfully
    auth.login()
    response = client.get('/dashboard/')
    assert response.status_code == 200
    assert b'Device Information' in response.data

def test_system_info_display(client, auth):
    """Test that dashboard displays system information."""
    auth.login()
    response = client.get('/dashboard/')

    # Check for system information sections
    assert b'System Information' in response.data
    assert b'Hardware Information' in response.data
    assert b'System Resource Usage' in response.data

    # Check for specific elements that should be in the page
    assert b'OS Name' in response.data
    assert b'OS Version' in response.data
    assert b'Hostname' in response.data
    assert b'CPU Usage' in response.data
    assert b'Memory Usage' in response.data
    assert b'Disk Usage' in response.data

@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
@patch('psutil.disk_usage')
def test_resource_usage_data(mock_disk, mock_memory, mock_cpu, client, auth):
    """Test that resource usage data is correctly provided to the template."""
    # Mock system resource data
    mock_cpu.return_value = 25.5

    mock_memory.return_value.percent = 60.0
    mock_memory.return_value.used = 4 * 1024 ** 3  # 4 GB
    mock_memory.return_value.total = 8 * 1024 ** 3  # 8 GB

    mock_disk.return_value.percent = 45.0
    mock_disk.return_value.used = 100 * 1024 ** 3  # 100 GB
    mock_disk.return_value.total = 250 * 1024 ** 3  # 250 GB

    # Access dashboard
    auth.login()
    response = client.get('/dashboard/')

    # Check if mocked values appear in the response
    assert b'25.5%' in response.data  # CPU
    assert b'60.0%' in response.data  # Memory
    assert b'45.0%' in response.data  # Disk
