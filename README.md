# CAQES - Centralized Automated Quarantine & Endpoint Segmentation

## Project Overview

This project aims to build a Security Orchestration, Automation, and Response (SOAR) system for quarantining suspicious or malicious IoT clients in a home environment. The system is designed to enhance the security of IoT devices by automating the quarantine process when threats are detected by an external Intrusion Detection System (IDS). CAQES only orchestrates the quarantine and integrates with existing IDS and network devices.

## Components

The project consists of three main components:

1. **Syslog-ng**: This component facilitates the transmission of alerts and incidents from the Intrusion Detection System (IDS) to CAQES. Syslog-ng automatically forwards log data to NATS, thereby initiating the core functionalities of the CAQES system.

2. **Mosquitto**: Mosquitto is an MQTT broker for real-time processing and delivery of log data, ensuring efficient communication between components. Its lightweight and high-performance nature makes it ideal for handling the rapid influx of log messages, providing quick and reliable data transfer to the core component.

3. **Core**: The core component orchestrates the network quarantine and IoT protocol quarantine. It analyzes the processed log data, identifies quarantine actions based on IDS detections, and takes appropriate actions to isolate the affected IoT clients.

## Usage

Once the system is up and running, it will continuously respond to alerts from the external IDS. When a threat is detected by the IDS, the core component will automatically quarantine the affected IoT clients to prevent further damage.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please open an issue on the GitHub repository or contact the project maintainers.
