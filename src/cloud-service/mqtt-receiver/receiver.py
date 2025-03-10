#!/usr/bin/env python3
"""
MQTT Receiver App for Amazing IoT Device

This application connects to an MQTT broker and receives messages published
by IoT devices. It processes and stores these messages for later use.
"""

import json
import logging
import os
import time
from datetime import datetime

import paho.mqtt.client as mqtt_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mqtt-receiver")

# Storage path for received messages
DATA_DIR = None


# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    """Callback for when client receives a CONNACK response from server."""
    logger = logging.getLogger("mqtt-receiver")
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {userdata['host']}:{userdata['port']}")
        # Subscribe to the topic
        client.subscribe(userdata["topic"])
        logger.info(f"Subscribed to topic: {userdata['topic']}")
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")


# Callback when a message is received from the server
def on_message(client, userdata, msg):
    """Callback when a message is received from the server."""
    logger = logging.getLogger("mqtt-receiver")
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    logger.info(f"Received message on topic {topic}: {payload}")

    try:
        # Parse the JSON payload
        data = json.loads(payload)

        # Extract device ID from the topic if available, otherwise from the data
        topic_parts = topic.split("/")
        device_id = data.get("device_id", topic_parts[-2] if len(topic_parts) > 2 else "unknown")

        # Create a timestamp if not in the data
        timestamp = data.get("timestamp", datetime.now().isoformat())

        # Store the data
        store_data(device_id, topic, timestamp, data)

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON payload: {payload}")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")


def store_data(device_id, topic, timestamp, data):
    """Store received data to disk."""
    global DATA_DIR
    # Initialize DATA_DIR if not set
    if DATA_DIR is None:
        DATA_DIR = os.environ.get("DATA_DIR", "/data")

    # Create device directory if it doesn't exist
    device_dir = os.path.join(DATA_DIR, device_id)
    os.makedirs(device_dir, exist_ok=True)

    # Format timestamp for filename
    date_str = timestamp.split("T")[0] if "T" in timestamp else timestamp.split(" ")[0]

    # Determine file path based on the topic
    topic_suffix = topic.split("/")[-1]
    file_path = os.path.join(device_dir, f"{date_str}_{topic_suffix}.jsonl")

    # Append the data as a new line in the file
    with open(file_path, "a") as f:
        f.write(json.dumps(data) + "\n")

    logger.debug(f"Stored data to {file_path}")


def main():
    """Main function to run the MQTT client."""
    logger = logging.getLogger("mqtt-receiver")

    # Load MQTT configuration from environment
    mqtt_broker_host = os.environ.get("MQTT_BROKER_HOST", "mosquitto")
    mqtt_broker_port = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
    mqtt_username = os.environ.get("MQTT_USERNAME", "")
    mqtt_password = os.environ.get("MQTT_PASSWORD", "")
    mqtt_topic = os.environ.get("MQTT_TOPIC", "iot/device/#")
    mqtt_client_id = os.environ.get("MQTT_CLIENT_ID", f"mqtt-receiver-{time.time()}")

    # Create MQTT client instance with config in userdata
    client = mqtt_client.Client(
        client_id=mqtt_client_id,
        clean_session=True,
        userdata={"host": mqtt_broker_host, "port": mqtt_broker_port, "topic": mqtt_topic},
    )

    # Set up authentication if credentials are provided
    if mqtt_username and mqtt_password:
        client.username_pw_set(mqtt_username, mqtt_password)

    # Assign callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect to MQTT broker
        logger.info(f"Connecting to MQTT broker at {mqtt_broker_host}:{mqtt_broker_port}...")
        client.connect(mqtt_broker_host, mqtt_broker_port, 60)

        # Start the network loop
        logger.info("Starting MQTT receiver service...")
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Error in MQTT receiver service: {str(e)}")
    finally:
        client.disconnect()
        logger.info("MQTT receiver service shutdown")


if __name__ == "__main__":
    main()
