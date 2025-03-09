# Amazing IoT Device

## Overview

This project is an IoT device agent with a Flask web interface. It allows users to log in and view basic information about the device, such as the operating system version, current version, and system resource usage. The device can also publish data to a cloud service using the MQTT protocol.

## Features

- User authentication
- Dashboard with system information
- Settings management
- Resource usage monitoring
- MQTT data publishing to cloud services
- Remote device monitoring via MQTT

## Technology Stack

- **Backend Framework**: Flask
- **Frontend Framework**: Bootstrap
- **Database**: SQLite
- **Programming Language**: Python 3.12 and above
- **Package Management**: PDM
- **System Monitoring**: psutil
- **MQTT Client**: paho-mqtt
- **Message Format**: JSON

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- PDM (Python Development Master)
- Eclipse Mosquitto (optional for local MQTT broker)

### Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd amazing-iot-device
    ```

2. Install dependencies:

    ```bash
    pdm install
    ```

3. Initialize the database:

    ```bash
    pdm run python run.py
    ```

### Running the Application

1. Start the application:

    ```bash
    pdm run start
    ```

2. Open your web browser and navigate to `http://localhost:5050`

### MQTT Configuration

1. Access the MQTT settings page after logging in by navigating to Settings > MQTT Settings.

2. Configure the following parameters:
   - Enable MQTT Service: Toggle to enable/disable the MQTT service
   - Broker Host: Address of the MQTT broker (e.g., localhost or cloud broker URL)
   - Broker Port: Port number for the MQTT broker (default: 1883)
   - Username and Password: Credentials for the MQTT broker
   - Topic Prefix: Topic structure for publishing data (e.g., iot/device)
   - Publish Interval: How often to publish data (in seconds)
   - Client ID: Optional unique identifier for the device

3. Click "Test Connection" to verify your broker settings.

4. The device will automatically publish data on the following topics:
   - `{prefix}/system`: System information (OS, version, etc.)
   - `{prefix}/network`: Network information (hostname, IP)
   - `{prefix}/resources`: Resource usage (CPU, memory, disk)
   - `{prefix}/full`: Complete device state

### Cloud Service Setup

The project includes a cloud service component for receiving and storing MQTT data:

1. Navigate to the cloud service directory:

    ```bash
    cd src/cloud-service
    ```

2. Start the MQTT broker and receiver service:

    ```bash
    docker-compose up -d
    ```

3. The cloud service includes:
   - Eclipse Mosquitto MQTT broker
   - MQTT data receiver service
   - Authentication setup for secure connections

## Project Structure

- `run.py`: Entry point for the application
- `src/amazing_iot_device/`: Application source code
- `src/amazing_iot_device/static/css/`: CSS styles
- `src/amazing_iot_device/templates/`: HTML templates
- `src/amazing_iot_device/models.py`: Database models
- `src/amazing_iot_device/auth.py`: Authentication module
- `src/amazing_iot_device/dashboard.py`: Dashboard module
- `src/amazing_iot_device/settings.py`: Settings module
- `src/amazing_iot_device/mqtt_service.py`: MQTT service module
- `src/cloud-service/`: Cloud service components
  - `docker-compose.yaml`: Docker configuration for services
  - `mosquitto/`: Mosquitto MQTT broker configuration
  - `mqtt-receiver/`: Service to receive and store MQTT data
- `tests/`: Unit tests

## License

This project is licensed under the MIT License.