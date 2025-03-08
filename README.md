# Amazing IoT Device

## Overview

This project is an IoT device agent with a Flask web interface. It allows users to log in and view basic information about the device, such as the operating system version, current version, and system resource usage.

## Features

- User authentication
- Dashboard with system information
- Settings management
- Resource usage monitoring

## Technology Stack

- **Backend Framework**: Flask
- **Frontend Framework**: Bootstrap
- **Database**: SQLite
- **Programming Language**: Python 3.12 and above
- **Package Management**: PDM
- **System Monitoring**: psutil

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- PDM (Python Development Master)

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

## Project Structure

- `run.py`: Entry point for the application
- `src/amazing_iot_device/`: Application source code
- `src/amazing_iot_device/static/css/`: CSS styles
- `src/amazing_iot_device/templates/`: HTML templates
- `src/amazing_iot_device/models.py`: Database models
- `src/amazing_iot_device/auth.py`: Authentication module
- `src/amazing_iot_device/dashboard.py`: Dashboard module
- `src/amazing_iot_device/settings.py`: Settings module
- `tests/`: Unit tests

## License

This project is licensed under the MIT License.