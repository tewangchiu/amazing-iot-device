"""
Tests for MQTT service functionality
"""

import pytest
from unittest.mock import patch, MagicMock
from amazing_iot_device.mqtt_service import MQTTService


@pytest.fixture
def mock_mqtt_client():
    """Create a mock MQTT client."""
    with patch("paho.mqtt.client.Client") as mock_client:
        # Configure the mock client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        # Mock connection status
        mock_client_instance.is_connected.return_value = True

        # Mock publish method
        mock_client_instance.publish.return_value = MagicMock()
        mock_client_instance.publish.return_value.is_published.return_value = True
        mock_client_instance.publish.return_value.wait_for_publish.return_value = None

        yield mock_client_instance


def test_mqtt_service_init():
    """Test MQTT service initialization."""
    mqtt_service = MQTTService()

    # Check default attributes
    assert mqtt_service.is_running is False
    assert mqtt_service.client is None
    assert mqtt_service.broker_settings["host"] == "localhost"
    assert int(mqtt_service.broker_settings["port"]) == 1883
    assert mqtt_service.publish_interval == 60


@patch("paho.mqtt.client.Client")
def test_mqtt_service_setup(mock_client_class):
    """Test MQTT client setup."""
    # Configure the mock client
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    # Initialize MQTT service and set up the client
    mqtt_service = MQTTService()
    mqtt_service._setup_mqtt_client()

    # Check if client was created
    assert mqtt_service.client is not None
    assert mock_client_class.called

    # Check if callbacks were set
    assert mock_client_instance.on_connect is not None
    assert mock_client_instance.on_disconnect is not None
    assert mock_client_instance.on_publish is not None


def test_mqtt_service_with_auth():
    """Test MQTT service with authentication."""
    with patch("paho.mqtt.client.Client") as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        # Create MQTT service with authentication
        mqtt_service = MQTTService()
        mqtt_service.broker_settings["username"] = "test_user"
        mqtt_service.broker_settings["password"] = "test_password"

        # Set up the client
        mqtt_service._setup_mqtt_client()

        # Check if username_pw_set was called
        mock_client_instance.username_pw_set.assert_called_once_with(
            "test_user", "test_password"
        )


@patch("time.sleep", return_value=None)  # To avoid actual sleep in tests
def test_mqtt_publish_hardware_info(mock_sleep, mock_mqtt_client):
    """Test publishing hardware information."""
    # Create MQTT service with the mock client
    mqtt_service = MQTTService()
    mqtt_service.client = mock_mqtt_client

    # Mock hardware info
    sample_hardware_info = {
        "timestamp": "2023-01-01T00:00:00",
        "device_id": "test-device",
        "system": {"os_name": "Test OS"},
        "network": {"hostname": "test-host"},
        "resources": {"cpu_percent": 10},
    }

    # Mock the _get_hardware_info method
    with patch.object(
        mqtt_service, "_get_hardware_info", return_value=sample_hardware_info
    ):
        # Call the publish method
        mqtt_service._publish_hardware_info()

        # Check that publish was called 4 times (for each topic)
        assert mock_mqtt_client.publish.call_count == 4

        # Check that the correct topics were used
        topic_prefix = mqtt_service.broker_settings["topic_prefix"]
        expected_topics = [
            f"{topic_prefix}/system",
            f"{topic_prefix}/network",
            f"{topic_prefix}/resources",
            f"{topic_prefix}/full",
        ]

        actual_topics = [
            call[1]["topic"] for call in mock_mqtt_client.publish.call_args_list
        ]
        for topic in expected_topics:
            assert topic in actual_topics


@patch("paho.mqtt.client.Client")
def test_mqtt_on_connect_callback(mock_client_class):
    """Test the on_connect callback."""
    # Configure the mock client
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    # Initialize MQTT service
    mqtt_service = MQTTService()
    mqtt_service._setup_mqtt_client()

    # Get the on_connect callback
    on_connect = mock_client_instance.on_connect

    # Test successful connection (rc=0)
    with patch("logging.getLogger") as mock_logger:
        mock_log = MagicMock()
        mock_logger.return_value = mock_log

        # Call the callback with success code
        on_connect(mock_client_instance, None, None, 0)

        # Check that success was logged
        mock_log.info.assert_called()

        # Test failed connection (rc=1)
        on_connect(mock_client_instance, None, None, 1)

        # Check that error was logged
        mock_log.error.assert_called()
