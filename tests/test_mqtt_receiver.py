"""
Tests for MQTT receiver cloud service
"""
import json
import os

# Add the cloud-service directory to the path for imports
import sys
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'cloud-service', 'mqtt-receiver'))

import receiver  # Import the receiver module


@pytest.fixture
def mock_mqtt_client():
    """Create a mock MQTT client."""
    with patch('paho.mqtt.client.Client') as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        yield mock_client_instance

@pytest.fixture
def mock_env_vars():
    """Setup mock environment variables."""
    with patch.dict(os.environ, {
        'MQTT_BROKER_HOST': 'test-broker',
        'MQTT_BROKER_PORT': '1883',
        'MQTT_USERNAME': 'test_user',
        'MQTT_PASSWORD': 'test_password',
        'MQTT_TOPIC': 'test/device/#',
        'DATA_DIR': '/tmp/test-data'
    }):
        yield

def test_on_connect(mock_mqtt_client):
    """Test the on_connect callback."""
    # Create a client
    client = mock_mqtt_client

    # Setup logger mock
    with patch('logging.getLogger') as mock_logger:
        mock_log = MagicMock()
        mock_logger.return_value = mock_log

        # Test successful connection (rc=0)
        userdata ={'host': 'mosquitto', 'port': 1883, 'topic': 'iot/device/#'}
        receiver.on_connect(client, userdata, None, 0)

        # Check that success was logged and subscription was made
        mock_log.info.assert_called()
        client.subscribe.assert_called_once()

        # Test failed connection (rc=1)
        receiver.on_connect(client, None, None, 1)

        # Check that error was logged
        mock_log.error.assert_called()

def test_on_message():
    """Test the on_message callback."""
    # Create a message mock
    mock_msg = MagicMock()
    mock_msg.topic = "iot/device/abc123/system"
    mock_msg.payload = json.dumps({
        "device_id": "abc123",
        "timestamp": "2023-01-01T12:00:00",
        "os_name": "TestOS",
        "cpu_percent": 25.0
    }).encode('utf-8')

    # Setup client mock
    mock_client = MagicMock()

    # Setup logger mock
    with patch('logging.getLogger') as mock_logger:
        mock_log = MagicMock()
        mock_logger.return_value = mock_log

        # Mock the store_data function
        with patch('receiver.store_data') as mock_store:
            # Call the on_message function
            receiver.on_message(mock_client, None, mock_msg)

            # Check that message was logged
            mock_log.info.assert_called()

            # Check that store_data was called
            mock_store.assert_called_once()

def test_store_data(mock_env_vars):
    """Test the store_data function."""
    # Create test data
    device_id = "test-device"
    topic = "iot/device/test-device/system"
    timestamp = "2023-01-01T12:00:00"
    data = {
        "device_id": device_id,
        "timestamp": timestamp,
        "os_name": "TestOS",
        "cpu_percent": 25.0
    }

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir, \
         patch.dict(os.environ, {'DATA_DIR': temp_dir}), \
         patch('builtins.open', mock_open()) as mock_file:
                # Call the store_data function
                receiver.store_data(device_id, topic, timestamp, data)

                # Check that a file was opened for writing
                mock_file.assert_called_once()

                # Check that the data was written to the file
                mock_file().write.assert_called_once_with(json.dumps(data) + '\n')

def test_main(mock_mqtt_client, mock_env_vars):
    """Test the main function."""
    # Mock the loop_forever function to avoid blocking
    mock_mqtt_client.loop_forever.side_effect = KeyboardInterrupt()

    # Setup logger mock
    with patch('logging.getLogger') as mock_logger:
        mock_log = MagicMock()
        mock_logger.return_value = mock_log

        # Call the main function
        receiver.main()

        # Check that client was created and configured correctly
        mock_mqtt_client.username_pw_set.assert_called_once_with('test_user', 'test_password')
        assert mock_mqtt_client.on_connect is receiver.on_connect
        assert mock_mqtt_client.on_message is receiver.on_message
        mock_mqtt_client.connect.assert_called_once_with('test-broker', 1883, 60)
        mock_mqtt_client.loop_forever.assert_called_once()
        mock_mqtt_client.disconnect.assert_called_once()

def test_json_decode_error():
    """Test handling of JSON decode error in on_message."""
    # Create a message with invalid JSON
    mock_msg = MagicMock()
    mock_msg.topic = "iot/device/abc123/system"
    mock_msg.payload = b"This is not JSON"

    # Setup client mock
    mock_client = MagicMock()

    # Setup logger mock
    with patch('logging.getLogger') as mock_logger:
        mock_log = MagicMock()
        mock_logger.return_value = mock_log

        # Call the on_message function
        receiver.on_message(mock_client, None, mock_msg)

        # Check that error was logged
        mock_log.error.assert_called()

        # Verify store_data was not called
        with patch('receiver.store_data') as mock_store:
            assert not mock_store.called
