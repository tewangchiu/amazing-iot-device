"""
Tests for settings functionality
"""
from amazing_iot_device.models import Settings


def test_settings_page_access(client, auth):
    """Test that settings page requires authentication and loads correctly."""
    # Unauthenticated access should redirect
    response = client.get('/settings/')
    assert response.status_code == 302

    # Authenticated access should load successfully
    auth.login()
    response = client.get('/settings/')
    assert response.status_code == 200
    assert b'System Settings' in response.data

def test_settings_display(client, auth, app):
    """Test that settings are correctly displayed."""
    auth.login()
    response = client.get('/settings/')

    # Check for specific settings that should be visible
    assert b'device_name' in response.data
    assert b'refresh_interval' in response.data

def test_edit_setting(client, auth, app):
    """Test editing a setting."""
    auth.login()

    # Make a POST request to edit a setting
    response = client.post(
        '/settings/edit/device_name',
        data={'value': 'Updated Device Name'},
        follow_redirects=True
    )

    assert b'Setting device_name updated successfully' in response.data

    # Verify the setting was updated in the database
    with app.app_context():
        setting = Settings.query.filter_by(key='device_name').first()
        assert setting.value == 'Updated Device Name'

def test_mqtt_settings_page(client, auth):
    """Test MQTT settings page loads correctly."""
    auth.login()
    response = client.get('/settings/mqtt')
    assert response.status_code == 200
    assert b'MQTT Settings' in response.data
    assert b'Broker Host' in response.data
    assert b'Broker Port' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data
    assert b'Topic Prefix' in response.data

def test_mqtt_settings_update(client, auth, app):
    """Test updating MQTT settings."""
    auth.login()

    # Make a POST request to update MQTT settings
    response = client.post(
        '/settings/mqtt',
        data={
            'mqtt_enabled': True,
            'mqtt_broker_host': 'test-broker.example.com',
            'mqtt_broker_port': 1883,
            'mqtt_username': 'test_user',
            'mqtt_password': 'test_password',
            'mqtt_topic_prefix': 'test/device',
            'mqtt_client_id': 'test-device',
            'mqtt_publish_interval': 30
        },
        follow_redirects=True
    )

    # Check for success message
    assert b'MQTT settings updated' in response.data

    # Verify settings were updated in the database
    with app.app_context():
        mqtt_host = Settings.query.filter_by(key='mqtt_broker_host').first()
        assert mqtt_host.value == 'test-broker.example.com'

        mqtt_topic = Settings.query.filter_by(key='mqtt_topic_prefix').first()
        assert mqtt_topic.value == 'test/device'

        mqtt_interval = Settings.query.filter_by(key='mqtt_publish_interval').first()
        assert mqtt_interval.value == '30'
