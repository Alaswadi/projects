# Attack Surface Discovery SaaS Prototype

A lightweight SaaS prototype that allows users to input a domain name via a web interface, run attack surface discovery scans using industry-standard security tools, and generate comprehensive reports.

## Features

- **Web Interface**: Simple, responsive web interface for domain input and scan management
- **Subdomain Enumeration**: Uses Subfinder to discover subdomains
- **Port Scanning**: Uses Naabu to scan for open ports
- **Vulnerability Scanning**: Uses Nuclei to identify security vulnerabilities
- **Report Generation**: Generates downloadable JSON reports with detailed findings
- **Real-time Progress**: Live status updates during scanning process
- **Containerized**: Fully containerized with Docker for easy deployment

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **Security Tools**: 
  - [Subfinder](https://github.com/projectdiscovery/subfinder) - Subdomain enumeration
  - [Naabu](https://github.com/projectdiscovery/naabu) - Port scanning
  - [Nuclei](https://github.com/projectdiscovery/nuclei) - Vulnerability scanning
- **Containerization**: Docker

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Internet connection (for tool updates and passive reconnaissance)

### Option 1: Minimal Version (Recommended for Coolify)

For quick deployment and testing:

```bash
docker build -f Dockerfile.minimal -t scanner-minimal .
docker run -p 5000:5000 scanner-minimal
```

Access at `http://localhost:5000`

### Option 2: Using Docker Compose

1. Clone or download the project files
2. Navigate to the project directory
3. Build and run the container:

```bash
docker-compose up --build
```

4. Access the application at `http://localhost:5000`

### Option 3: Using Docker directly (Full Version)

1. Build the Docker image:

```bash
docker build -t attack-surface-scanner .
```

2. Run the container:

```bash
docker run -p 5000:5000 -v /tmp/scans:/tmp/scans attack-surface-scanner
```

3. Access the application at `http://localhost:5000`

### Option 4: Coolify Deployment

For Coolify deployment, use the minimal configuration:

1. **Dockerfile**: Use `Dockerfile.minimal`
2. **Docker Compose**: Use `docker-compose.coolify.yml`
3. **Environment Variables** in Coolify:
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=0`
   - `PYTHONUNBUFFERED=1`

See `COOLIFY_DEPLOYMENT.md` for detailed Coolify deployment instructions.

### Testing the Deployment

Use the test script to verify everything works:

```bash
python3 test_app.py http://your-domain:5000
```

## Usage

1. **Enter Domain**: Input the target domain (e.g., `example.com`) in the web interface
2. **Configure Scan**: Select scan options:
   - Scan subdomains (Subfinder)
   - Scan ports (Naabu)
   - Vulnerability check (Nuclei)
   - Deep scan mode (extended scanning)
3. **Start Scan**: Click "Start Scan" to begin the attack surface discovery
4. **Monitor Progress**: Watch real-time progress updates and current task status
5. **Download Report**: Once complete, download the comprehensive JSON report

## Scan Process

The scanning process follows these steps:

1. **Subdomain Enumeration**: Discovers subdomains using passive reconnaissance
2. **Port Scanning**: Scans discovered subdomains for open ports
3. **Vulnerability Assessment**: Tests for known vulnerabilities using Nuclei templates
4. **Report Generation**: Aggregates all findings into a structured report

## Report Format

The generated report includes:

- **Domain Information**: Target domain and scan timestamp
- **Subdomains**: List of discovered subdomains
- **Open Ports**: Detailed port information per subdomain
- **Vulnerabilities**: Security issues with severity levels
- **Summary Statistics**: Overview of findings

## Configuration

### Tool Configuration

The security tools are configured for optimal performance in a containerized environment:

- **Subfinder**: Uses passive sources only for speed and stealth
- **Naabu**: Scans top 100 ports by default (configurable)
- **Nuclei**: Uses CVE and vulnerability templates

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_DEBUG`: Set to `0` for production

## Security Considerations

- **Input Validation**: All domain inputs are validated and sanitized
- **Scope Limitation**: Scans are restricted to user-provided domains
- **Temporary Storage**: Scan results are stored temporarily and cleaned up
- **Resource Management**: Single scan per session to prevent resource exhaustion

## Limitations

- **Single User**: Designed for single-user testing (not multi-tenant)
- **No Persistence**: No database storage (results are temporary)
- **Resource Dependent**: Scan performance depends on host resources
- **Network Dependent**: Requires internet access for passive reconnaissance

## Development

### Local Development

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install security tools manually or use the Docker environment

3. Run the Flask application:

```bash
python app.py
```

### Project Structure

```
attack-surface-scanner/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Web interface
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main web interface
- `POST /api/scan` - Start a new scan
- `GET /api/scan/<scan_id>/status` - Get scan status
- `GET /api/scan/<scan_id>/report` - Download scan report
- `POST /api/scan/<scan_id>/cancel` - Cancel active scan

## Troubleshooting

### Common Issues

1. **Tools not found**: Ensure the Docker image built successfully with all tools
2. **Permission errors**: Check volume mount permissions for `/tmp/scans`
3. **Network issues**: Ensure internet connectivity for tool updates and passive recon
4. **Resource constraints**: Increase Docker memory/CPU limits if scans fail

### Logs

View container logs:

```bash
docker-compose logs -f
```

## Future Enhancements

- User authentication and multi-tenant support
- Persistent database storage
- Advanced report formats (PDF, HTML)
- Scan scheduling and automation
- API rate limiting and quotas
- Cloud deployment configurations

## License

This project is for educational and testing purposes. Ensure you have permission to scan target domains.

## Disclaimer

This tool is intended for authorized security testing only. Users are responsible for ensuring they have proper authorization before scanning any domains or systems.