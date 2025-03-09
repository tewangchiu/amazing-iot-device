#!/usr/bin/env python3
"""
MQTT Receiver App for Amazing IoT Device

This application connects to an MQTT broker and receives messages published
by IoT devices. It processes and stores these messages for later use.
"""
import os
import json
import time
import logging
from datetime import datetime
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mqtt-receiver')

# MQTT Configuration - read from environment variables with defaults
MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'mosquitto')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', '1883'))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_TOPIC = os.environ.get('MQTT_TOPIC', 'iot/device/#')
MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', f'receiver-app-{time.time()}')

# Storage path for received messages
DATA_DIR = os.environ.get('DATA_DIR', '/data')
os.makedirs(DATA_DIR, exist_ok=True)

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        # Subscribe to the topic
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")

# Callback when a message is received from the server
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    logger.info(f"Received message on topic {topic}")
    
    try:
        # Parse the JSON payload
        data = json.loads(payload)
        
        # Extract device ID from the topic if available, otherwise from the data
        topic_parts = topic.split('/')
        device_id = data.get('device_id', topic_parts[-2] if len(topic_parts) > 2 else 'unknown')
        
        # Create a timestamp if not in the data
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Store the data
        store_data(device_id, topic, timestamp, data)
        
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON payload: {payload}")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

def store_data(device_id, topic, timestamp, data):
    """Store received data to disk."""
    # Create device directory if it doesn't exist
    device_dir = os.path.join(DATA_DIR, device_id)
    os.makedirs(device_dir, exist_ok=True)
    
    # Format timestamp for filename
    date_str = timestamp.split('T')[0] if 'T' in timestamp else timestamp.split(' ')[0]
    
    # Determine file path based on the topic
    topic_suffix = topic.split('/')[-1]
    file_path = os.path.join(device_dir, f"{date_str}_{topic_suffix}.jsonl")
    
    # Append the data as a new line in the file
    with open(file_path, 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    logger.debug(f"Stored data to {file_path}")

def main():
    """Main function to run the MQTT client."""
    # Create MQTT client instance
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
    
    # Set up authentication if credentials are provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Assign callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to MQTT broker
        logger.info(f"Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        
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