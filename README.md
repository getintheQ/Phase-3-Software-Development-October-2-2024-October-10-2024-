# Machine Control System

A desktop application for controlling and monitoring a machine process system, optimized for Raspberry Pi 7-inch touchscreen display.

## Features

- Real-time process monitoring and control
- Temperature control system (40-60°C range)
- Patient information management
- Progress tracking with visual indicators
- Emergency stop functionality
- Process status monitoring
- Touch-optimized interface

## System Requirements

- Windows/Linux operating system
- Node.js (v16.0.0 or higher)
- Electron
- Display resolution: 800x480 (optimized for Raspberry Pi 7-inch touchscreen)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd machine-control-app
```

2. Install dependencies:
```bash
npm install
```

3. Run the application in development mode:
```bash
npm start
```

4. Build the executable:
```bash
npm run build
```

## Project Structure

```
machine-control-app/
├── src/
│   ├── index.html          # Main application interface
│   └── assets/             # Application assets
├── main.js                 # Electron main process
├── preload.js             # Preload script for security
├── package.json           # Project configuration
└── README.md             # Project documentation
```

## Usage

### Patient Information Entry
1. Enter Patient ID
2. Enter Patient Name
3. Specify Required Powder Mass (g)
4. Input Water Volume (ml)
5. Click "Start Process"

### Process Monitoring
- Monitor water level and powder level
- Track temperature within 40-60°C range
- View system pressure
- Track process progress
- Monitor system status

### Emergency Controls
- Emergency Stop button available during processing
- Automatic system reset after emergency stop
- Temperature alerts for out-of-range conditions

## Development

### Starting Development Server
```bash
npm start
```

### Building for Production
```bash
npm run build
```

The executable will be created in the `dist` directory.

## Technical Specifications

- Screen Dimensions: 194mm x 110mm x 20mm
- Display Resolution: 800x480 pixels
- Temperature Range: 40-60°C
- Update Interval: 500ms
- Process Steps:
  1. Initialization
  2. Water System Preparation
  3. Powder Addition
  4. Mixing
  5. Finalization
  6. Completion

## Safety Features

- Real-time temperature monitoring
- Visual alerts for temperature violations
- Emergency stop functionality
- System status indicators
- Process validation checks

## Troubleshooting

### Common Issues

1. Temperature Alert
   - Check if temperature is within 40-60°C range
   - Verify temperature sensor connections

2. Process Not Starting
   - Ensure all form fields are filled
   - Check system status indicator

3. Display Issues
   - Verify screen resolution settings
   - Check display connections

### Error Messages

- "Please fill in all fields": Complete all required information
- "Temperature Low/High": Temperature outside acceptable range
- "Emergency Stop Activated": System stopped by emergency control

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Support

For support, please contact [your-contact-information]

## Version History

- 1.0.0
  - Initial Release
  - Basic process control functionality
  - Temperature monitoring system
  - Emergency stop implementation

## Acknowledgments

- Electron.js team
- Node.js community
- Raspberry Pi foundation

## Future Enhancements

- Data logging system
- Remote monitoring capabilities
- Multi-language support
- Process automation features
- Database integration

