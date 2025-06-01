#!/usr/bin/env python3
"""
Attack Surface Discovery SaaS Prototype
Flask Backend Application
"""

import os
import json
import subprocess
import threading
import time
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import re
import tempfile
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global variables for scan management
active_scans = {}
scan_results = {}

class ScanManager:
    def __init__(self, scan_id, domain):
        self.scan_id = scan_id
        self.domain = domain
        self.status = "initializing"
        self.progress = 0
        self.current_task = "Preparing scan"
        self.results = {
            'subdomains': [],
            'ports': [],
            'vulnerabilities': []
        }
        self.temp_dir = tempfile.mkdtemp(prefix=f"scan_{scan_id}_")
        
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp directory: {e}")

def validate_domain(domain):
    """Validate domain format"""
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return re.match(pattern, domain) is not None

def run_subfinder(scan_manager):
    """Run Subfinder for subdomain enumeration"""
    try:
        scan_manager.status = "running"
        scan_manager.current_task = "Discovering subdomains"
        scan_manager.progress = 10
        
        output_file = os.path.join(scan_manager.temp_dir, "subdomains.txt")
        
        # Run Subfinder command
        cmd = [
            "subfinder",
            "-d", scan_manager.domain,
            "-o", output_file,
            "-silent"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            scan_manager.results['subdomains'] = subdomains
            scan_manager.progress = 30
            return True
        else:
            # Fallback: use the main domain if subfinder fails
            scan_manager.results['subdomains'] = [scan_manager.domain]
            scan_manager.progress = 30
            return True
            
    except subprocess.TimeoutExpired:
        scan_manager.results['subdomains'] = [scan_manager.domain]
        scan_manager.progress = 30
        return True
    except Exception as e:
        print(f"Subfinder error: {e}")
        scan_manager.results['subdomains'] = [scan_manager.domain]
        scan_manager.progress = 30
        return True

def run_naabu(scan_manager):
    """Run Naabu for port scanning"""
    try:
        scan_manager.current_task = "Scanning ports"
        scan_manager.progress = 40
        
        output_file = os.path.join(scan_manager.temp_dir, "ports.json")
        
        # Create targets file
        targets_file = os.path.join(scan_manager.temp_dir, "targets.txt")
        with open(targets_file, 'w') as f:
            for subdomain in scan_manager.results['subdomains']:
                f.write(f"{subdomain}\n")
        
        # Run Naabu command (scan common ports for speed)
        cmd = [
            "naabu",
            "-list", targets_file,
            "-top-ports", "100",
            "-json",
            "-o", output_file,
            "-silent"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        ports_data = []
        if result.returncode == 0 and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            port_info = json.loads(line.strip())
                            ports_data.append(port_info)
                        except json.JSONDecodeError:
                            continue
        
        scan_manager.results['ports'] = ports_data
        scan_manager.progress = 60
        return True
        
    except subprocess.TimeoutExpired:
        scan_manager.progress = 60
        return True
    except Exception as e:
        print(f"Naabu error: {e}")
        scan_manager.progress = 60
        return True

def run_nuclei(scan_manager):
    """Run Nuclei for vulnerability scanning"""
    try:
        scan_manager.current_task = "Scanning for vulnerabilities"
        scan_manager.progress = 70
        
        output_file = os.path.join(scan_manager.temp_dir, "vulnerabilities.json")
        
        # Create targets file
        targets_file = os.path.join(scan_manager.temp_dir, "targets.txt")
        with open(targets_file, 'w') as f:
            for subdomain in scan_manager.results['subdomains']:
                f.write(f"http://{subdomain}\n")
                f.write(f"https://{subdomain}\n")
        
        # Run Nuclei command (basic templates for speed)
        cmd = [
            "nuclei",
            "-list", targets_file,
            "-t", "cves/",
            "-t", "vulnerabilities/",
            "-json",
            "-o", output_file,
            "-silent"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        vulns_data = []
        if result.returncode == 0 and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            vuln_info = json.loads(line.strip())
                            vulns_data.append(vuln_info)
                        except json.JSONDecodeError:
                            continue
        
        scan_manager.results['vulnerabilities'] = vulns_data
        scan_manager.progress = 90
        return True
        
    except subprocess.TimeoutExpired:
        scan_manager.progress = 90
        return True
    except Exception as e:
        print(f"Nuclei error: {e}")
        scan_manager.progress = 90
        return True

def generate_report(scan_manager):
    """Generate HTML report"""
    try:
        scan_manager.current_task = "Generating report"
        scan_manager.progress = 95
        
        # Generate report content
        report_data = {
            'domain': scan_manager.domain,
            'scan_id': scan_manager.scan_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'subdomains': scan_manager.results['subdomains'],
            'ports': scan_manager.results['ports'],
            'vulnerabilities': scan_manager.results['vulnerabilities'],
            'summary': {
                'total_subdomains': len(scan_manager.results['subdomains']),
                'total_ports': len(scan_manager.results['ports']),
                'total_vulnerabilities': len(scan_manager.results['vulnerabilities'])
            }
        }
        
        # Save report data
        report_file = os.path.join(scan_manager.temp_dir, "report.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        scan_manager.progress = 100
        scan_manager.status = "completed"
        scan_manager.current_task = "Scan completed"
        
        return True
        
    except Exception as e:
        print(f"Report generation error: {e}")
        scan_manager.status = "error"
        return False

def run_scan(scan_id, domain):
    """Main scan function that runs all tools"""
    scan_manager = active_scans[scan_id]
    
    try:
        # Run scanning tools in sequence
        if not run_subfinder(scan_manager):
            scan_manager.status = "error"
            return
            
        if not run_naabu(scan_manager):
            scan_manager.status = "error"
            return
            
        if not run_nuclei(scan_manager):
            scan_manager.status = "error"
            return
            
        if not generate_report(scan_manager):
            scan_manager.status = "error"
            return
            
        # Store results for later retrieval
        scan_results[scan_id] = scan_manager
        
    except Exception as e:
        print(f"Scan error: {e}")
        scan_manager.status = "error"
        scan_manager.current_task = f"Error: {str(e)}"

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start a new scan"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip().lower()
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
            
        if not validate_domain(domain):
            return jsonify({'error': 'Invalid domain format'}), 400
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Create scan manager
        scan_manager = ScanManager(scan_id, domain)
        active_scans[scan_id] = scan_manager
        
        # Start scan in background thread
        scan_thread = threading.Thread(target=run_scan, args=(scan_id, domain))
        scan_thread.daemon = True
        scan_thread.start()
        
        return jsonify({
            'scan_id': scan_id,
            'status': 'started',
            'message': 'Scan initiated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/status')
def get_scan_status(scan_id):
    """Get scan status"""
    try:
        if scan_id not in active_scans:
            return jsonify({'error': 'Scan not found'}), 404
            
        scan_manager = active_scans[scan_id]
        
        return jsonify({
            'scan_id': scan_id,
            'status': scan_manager.status,
            'progress': scan_manager.progress,
            'current_task': scan_manager.current_task,
            'domain': scan_manager.domain
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/report')
def download_report(scan_id):
    """Download scan report"""
    try:
        if scan_id not in scan_results:
            return jsonify({'error': 'Report not found'}), 404
            
        scan_manager = scan_results[scan_id]
        report_file = os.path.join(scan_manager.temp_dir, "report.json")
        
        if not os.path.exists(report_file):
            return jsonify({'error': 'Report file not found'}), 404
            
        return send_file(
            report_file,
            as_attachment=True,
            download_name=f"attack_surface_report_{scan_manager.domain}_{scan_id[:8]}.json",
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/cancel', methods=['POST'])
def cancel_scan(scan_id):
    """Cancel an active scan"""
    try:
        if scan_id in active_scans:
            scan_manager = active_scans[scan_id]
            scan_manager.status = "cancelled"
            scan_manager.current_task = "Scan cancelled"
            scan_manager.cleanup()
            del active_scans[scan_id]
            
        return jsonify({'message': 'Scan cancelled successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)