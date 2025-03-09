"""
Configuration for test environment.
"""
import os
import sys
import tempfile
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from amazing_iot_device import create_app, db
from amazing_iot_device.models import User, Settings

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
    })
    
    # Create the database and the tables
    with app.app_context():
        db.create_all()
        
        # Create a test user
        test_user = User(username='test_user')
        test_user.set_password('test_password')
        db.session.add(test_user)
        
        # Create some test settings
        default_settings = {
            'device_name': 'Test IoT Device',
            'refresh_interval': '30',
            'mqtt_enabled': 'false',
            'mqtt_broker_host': 'localhost',
            'mqtt_broker_port': '1883',
            'mqtt_topic_prefix': 'test/iot/device'
        }
        
        for key, value in default_settings.items():
            db.session.add(Settings(key=key, value=value))
        
        db.session.commit()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def login(self, username='test_user', password='test_password'):
            return client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )
        
        def logout(self):
            return client.get('/auth/logout')
    
    return AuthActions()