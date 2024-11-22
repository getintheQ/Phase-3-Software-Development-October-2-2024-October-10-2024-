# Coffee Machine Control System

An automated control system for a professional coffee machine using Raspberry Pi. The system controls water temperature, flow rate, powder dispensing, and provides real-time monitoring with safety features.

## Table of Contents
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Safety Features](#safety-features)

## Features

### Core Functionality
- Temperature control (45-60°C range)
- Automated water circulation
- Powder dispensing control
- Real-time monitoring
- Touch screen interface

### Safety Features
- Water level monitoring (alarm at <10%)
- Powder level monitoring (alarm at <20%)
- Temperature range protection
- Emergency stop system
- Error logging

### Monitoring & Control
- Real-time temperature display
- Resource level monitoring
- Process status indicators
- Automated circulation control

## Hardware Requirements

### Main Components
- Raspberry Pi 4 (2GB+ RAM)
- 7" Touch Screen Display
- MAX31855 Thermocouple Amplifiers (x2)
- L298N Motor Drivers (x2)
- 25A/240V Solid State Relay
- Ultrasonic Water Level Sensor
- Load Cell for Powder Level
- Peristaltic Pump
- Powder Dispensing Motor
- Circulation Valve

### Pin Assignments
```python
GPIO Assignments:
- SPI0_MOSI (GPIO 10): Temperature sensors data
- SPI0_MISO (GPIO 9): Temperature reading
- SPI0_SCLK (GPIO 11): SPI clock
- PWM0 (GPIO 18): Pump control
- PWM1 (GPIO 19): Powder motor control
- GPIO 12: Heater SSR control
- GPIO 16: Water level trigger
- GPIO 17: Water level echo
- GPIO 22: Circulation valve
- GPIO 23/24: Pump direction control
- GPIO 25/26: Powder motor direction control
```

## Software Requirements

### Operating System
- Raspberry Pi OS (64-bit recommended)
- Python 3.7+

### Python Packages
```bash
pip install -r requirements.txt
```
Required packages:
- RPi.GPIO
- spidev
- tkinter
- logging
- pytest (for testing)

## Installation

1. System Preparation
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade

# Install required system packages
sudo apt-get install python3-pip python3-tk python3-dev

# Enable SPI interface
sudo raspi-config
# Navigate to Interface Options -> SPI -> Enable
```

2. Download and Install
```bash
# Clone repository
git clone https://github.com/your-repo/coffee-machine.git
cd coffee-machine

# Install Python dependencies
pip3 install -r requirements.txt

# Set permissions
chmod +x run.sh
chmod +x hardware_tests.py
```

## Configuration

1. Edit configuration file:
```bash
nano config.json
```

2. Configure parameters:
```json
{
    "temperature": {
        "min": 45.0,
        "max": 60.0,
        "initial_power": 70
    },
    "flow": {
        "initial_rate": 50
    },
    "alarms": {
        "water_level_min": 10,
        "powder_level_min": 20
    }
}
```

## Usage

1. Start the System
```bash
./run.sh
```

2. GUI Operation
- Press "Start" to begin process
- Monitor temperature and levels
- Use "Stop" for normal shutdown
- Use "Emergency Stop" for immediate shutdown

3. Normal Operation Sequence
   - System performs initial checks
   - Heater starts with 70% power
   - Temperature stabilizes in 45-60°C range
   - Process runs with automatic adjustments
   - Monitors water and powder levels
   - Activates circulation if needed

## Testing

1. Run Hardware Tests
```bash
python3 hardware_tests.py
```

2. Run System Tests
```bash
python3 -m pytest system_tests.py
```

3. Test Coverage
```bash
python3 -m pytest --cov=. tests/
```

## Maintenance

### Daily Checks
- Water level
- Powder level
- Temperature sensor readings
- Motor operation
- Valve operation

### Weekly Maintenance
- Clean sensors
- Check all connections
- Verify temperature calibration
- Test emergency stop
- Check log files

### Log Files
Located in `/var/log/coffee_machine/`:
- `system.log`: System operations
- `errors.log`: Error messages
- `maintenance.log`: Maintenance records

## Troubleshooting

### Common Issues

1. Temperature Out of Range
- Check thermocouple connections
- Verify heater operation
- Check circulation valve
- Verify water flow

2. Motor Issues
- Check power connections
- Verify PWM signals
- Check direction controls
- Inspect mechanical parts

3. Sensor Problems
- Clean sensors
- Check wiring
- Verify power supply
- Test signal connections

## Safety Features

### Emergency Procedures
1. Emergency Stop Button
   - Immediately stops all operations
   - Cuts power to heater
   - Stops all motors
   - Activates alarm

2. Automatic Shutoff Conditions
   - Water level < 5%
   - Powder level < 10%
   - Temperature > 60°C
   - Temperature < 45°C for extended period

3. Alarm Conditions
   - Water level < 10%
   - Powder level < 20%
   - Temperature out of range
   - System errors

## Support

For technical support:
- Email: support@your-company.com
- Phone: +1-234-567-8900
- Documentation: https://your-company.com/docs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Lead Developer: [Your Name]
- Hardware Design: [Hardware Engineer]
- Testing: [QA Engineer]
- Documentation: [Technical Writer]

## Version History

- v1.0.0 (2024-03-23)
  - Initial release
  - Basic temperature control
  - Safety features implemented

- v1.1.0 (2024-03-24)
  - Added circulation control
  - Improved error handling
  - Enhanced GUI
