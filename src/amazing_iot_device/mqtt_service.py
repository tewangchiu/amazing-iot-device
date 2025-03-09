"""
MQTT Service module for IoT device agent.
This module provides functionality to collect and publish hardware information to a cloud service via MQTT.
"""
import json
import threading
import time
import platform
import os
import psutil
import uuid
import socket
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from amazing_iot_device import db
from amazing_iot_device.models import Settings

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mqtt_service')

class MQTTService:
    """MQTT client service for publishing device information to a broker."""
    
    def __init__(self, app=None):
        """Initialize the MQTT service."""
        self.client = None
        # Set a default client_id that will be overridden by settings if available
        self.client_id = f"amazingiot-{uuid.uuid4().hex[:8]}"
        self.app = app
        self.thread = None
        self.is_running = False
        self.publish_interval = 60  # Default interval in seconds
        
        # Default settings - will be overridden by .env or database values
        self.broker_settings = {
            'host': os.environ.get('MQTT_BROKER_HOST', 'localhost'),
            'port': int(os.environ.get('MQTT_BROKER_PORT', '1883')),
            'username': os.environ.get('MQTT_USERNAME', ''),
            'password': os.environ.get('MQTT_PASSWORD', ''),
            'topic_prefix': os.environ.get('MQTT_TOPIC_PREFIX', 'iot/device')
        }
        
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize the service with the Flask app context."""
        self.app = app
        
        # Load settings from database
        with app.app_context():
            self._load_settings()
            
        # Setup MQTT client
        self._setup_mqtt_client()
            
    def _load_settings(self):
        """Load MQTT settings from the database."""
        settings = {s.key: s.value for s in Settings.query.filter(
            Settings.key.in_([
                'mqtt_broker_host', 
                'mqtt_broker_port',
                'mqtt_client_id',
                'mqtt_username',
                'mqtt_password',
                'mqtt_topic_prefix',
                'mqtt_publish_interval'
            ])
        ).all()}
        
        if settings.get('mqtt_broker_host'):
            self.broker_settings['host'] = settings.get('mqtt_broker_host')
        
        if settings.get('mqtt_broker_port'):
            self.broker_settings['port'] = int(settings.get('mqtt_broker_port'))
            
        if settings.get('mqtt_client_id'):
            self.client_id = settings.get('mqtt_client_id')

        if settings.get('mqtt_username'):
            self.broker_settings['username'] = settings.get('mqtt_username')
            
        if settings.get('mqtt_password'):
            self.broker_settings['password'] = settings.get('mqtt_password')
            
        if settings.get('mqtt_topic_prefix'):
            self.broker_settings['topic_prefix'] = settings.get('mqtt_topic_prefix')
            
        if settings.get('mqtt_publish_interval'):
            self.publish_interval = int(settings.get('mqtt_publish_interval'))

    def _setup_mqtt_client(self):
        """Set up the MQTT client with callbacks."""
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # Set up authentication if provided
        if self.broker_settings['username'] and self.broker_settings['password']:
            self.client.username_pw_set(
                self.broker_settings['username'], 
                self.broker_settings['password']
            )
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker_settings['host']}:{self.broker_settings['port']}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        logger.debug(f"Message {mid} published successfully")
    
    def start(self):
        """Start the MQTT service in a separate thread."""
        if self.is_running:
            logger.warning("MQTT service is already running")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("MQTT service started")
    
    def stop(self):
        """Stop the MQTT service."""
        self.is_running = False
        if self.client:
            self.client.disconnect()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("MQTT service stopped")
    
    def _run(self):
        """Run the MQTT service, collecting and publishing data periodically."""
        try:
            # Connect to the broker
            self.client.connect(
                self.broker_settings['host'],
                self.broker_settings['port']
            )
            self.client.loop_start()
            
            while self.is_running:
                # Collect and publish hardware information
                self._publish_hardware_info()
                # Sleep for the configured interval
                time.sleep(self.publish_interval)
                
        except Exception as e:
            logger.error(f"Error in MQTT service: {str(e)}")
        finally:
            if self.client:
                self.client.loop_stop()
                if self.client.is_connected():
                    self.client.disconnect()
    
    def _get_hardware_info(self):
        """Collect hardware information from the system."""
        # System information
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
        
        # Network information
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            network_info = {
                'hostname': hostname,
                'ip_address': ip_address,
            }
        except Exception as e:
            logger.error(f"Error getting network information: {str(e)}")
            network_info = {'error': str(e)}
        
        # Resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resource_usage = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_mb': memory.used / (1024 * 1024),
            'memory_total_mb': memory.total / (1024 * 1024),
            'disk_percent': disk.percent,
            'disk_used_gb': disk.used / (1024 ** 3),
            'disk_total_gb': disk.total / (1024 ** 3)
        }
        
        # Combined hardware information
        hardware_info = {
            'timestamp': datetime.now().isoformat(),
            'device_id': self.client_id,
            'system': system_info,
            'network': network_info,
            'resources': resource_usage
        }
        
        return hardware_info
    
    def _publish_hardware_info(self):
        """Publish hardware information to MQTT broker."""
        if not self.client.is_connected():
            logger.warning("Not connected to MQTT broker, attempting to reconnect...")
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect: {str(e)}")
                return
        
        hardware_info = self._get_hardware_info()
        
        # Publish to different topics
        topics = {
            'system': hardware_info['system'],
            'network': hardware_info['network'],
            'resources': hardware_info['resources'],
            'full': hardware_info
        }
        
        for topic_suffix, payload in topics.items():
            topic = f"{self.broker_settings['topic_prefix']}/{topic_suffix}"
            message_info = self.client.publish(
                topic=topic,
                payload=json.dumps(payload),
                qos=1,
                retain=False
            )
            
            if message_info.is_published():
                logger.info(f"Published to {topic}")
            else:
                logger.warning(f"Failed to publish to {topic}")

mqtt_service = MQTTService()

def init_mqtt_service(app):
    """Initialize and start the MQTT service."""
    global mqtt_service
    
    # Initialize and start the MQTT service
    mqtt_service.init_app(app)
    
    # Only start if enabled in settings
    with app.app_context():
        mqtt_enabled = Settings.query.filter_by(key='mqtt_enabled').first()
        if mqtt_enabled and mqtt_enabled.value.lower() == 'true':
            mqtt_service.start()