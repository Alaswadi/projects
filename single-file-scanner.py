#!/usr/bin/env python3
"""
Attack Surface Scanner - Single File Version
No external dependencies except Flask

To run:
1. pip install Flask
2. python single-file-scanner.py
3. Open http://localhost:5000
"""

import os
import json
import uuid
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'

# Global storage for scans
scans = {}

# Embedded HTML template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attack Surface Scanner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .progress-section {
            display: none;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e1e8ed;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 15px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
        }
        .progress-text {
            text-align: center;
            font-weight: 600;
            color: #2c3e50;
        }
        .results-section { display: none; margin-top: 20px; }
        .result-card {
            background: #f8f9fa;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
        }
        .result-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .result-card .count {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .result-list { max-height: 200px; overflow-y: auto; }
        .result-item {
            padding: 8px 0;
            border-bottom: 1px solid #f1f3f4;
            font-family: monospace;
            font-size: 0.9em;
        }
        .vulnerability {
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            padding: 10px;
            margin: 5px 0;
            border-radius: 0 5px 5px 0;
        }
        .error { background: #fed7d7; color: #c53030; padding: 15px; border-radius: 8px; margin: 20px 0; display: none; }
        .success { background: #c6f6d5; color: #2f855a; padding: 15px; border-radius: 8px; margin: 20px 0; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Attack Surface Scanner</h1>
            <p>Comprehensive security reconnaissance and vulnerability assessment</p>
        </div>
        
        <div class="content">
            <form id="scanForm">
                <div class="form-group">
                    <label for="domain">Target Domain</label>
                    <input type="text" id="domain" name="domain" placeholder="example.com" required>
                </div>
                <button type="submit" class="btn" id="startBtn">Start Scan</button>
            </form>
            
            <div class="error" id="error"></div>
            <div class="success" id="success"></div>
            
            <div class="progress-section" id="progress">
                <h3>Scan Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">Initializing...</div>
            </div>
            
            <div class="results-section" id="results">
                <h3>Scan Results</h3>
                
                <div class="result-card">
                    <h3>🌐 Subdomains <span class="count" id="subCount">0</span></h3>
                    <div class="result-list" id="subList"></div>
                </div>
                
                <div class="result-card">
                    <h3>🔌 Open Ports <span class="count" id="portCount">0</span></h3>
                    <div class="result-list" id="portList"></div>
                </div>
                
                <div class="result-card">
                    <h3>⚠️ Vulnerabilities <span class="count" id="vulnCount">0</span></h3>
                    <div class="result-list" id="vulnList"></div>
                </div>
                
                <button class="btn" onclick="downloadReport()">📄 Download Report</button>
            </div>
        </div>
    </div>

    <script>
        let currentScanId = null;
        let scanInterval = null;

        document.getElementById('scanForm').addEventListener('submit', function(e) {
            e.preventDefault();
            startScan();
        });

        function startScan() {
            const domain = document.getElementById('domain').value.trim();
            if (!domain) {
                showError('Please enter a domain');
                return;
            }

            hideMessages();
            document.getElementById('results').style.display = 'none';
            document.getElementById('progress').style.display = 'block';
            document.getElementById('startBtn').disabled = true;
            
            fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ domain: domain })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentScanId = data.scan_id;
                    showSuccess('Scan started successfully!');
                    startProgressTracking();
                } else {
                    showError(data.error || 'Failed to start scan');
                    resetUI();
                }
            })
            .catch(error => {
                showError('Network error: ' + error.message);
                resetUI();
            });
        }

        function startProgressTracking() {
            scanInterval = setInterval(checkProgress, 2000);
        }

        function checkProgress() {
            if (!currentScanId) return;

            fetch(`/status/${currentScanId}`)
            .then(response => response.json())
            .then(data => {
                updateProgress(data.progress, data.current_task);
                
                if (data.status === 'completed') {
                    clearInterval(scanInterval);
                    showResults(data.results);
                    resetUI();
                } else if (data.status === 'failed') {
                    clearInterval(scanInterval);
                    showError('Scan failed');
                    resetUI();
                }
            })
            .catch(error => console.error('Progress check error:', error));
        }

        function updateProgress(progress, task) {
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = task || 'Processing...';
        }

        function showResults(results) {
            document.getElementById('progress').style.display = 'none';
            document.getElementById('results').style.display = 'block';
            
            // Subdomains
            const subdomains = results.subdomains || [];
            document.getElementById('subCount').textContent = subdomains.length;
            document.getElementById('subList').innerHTML = subdomains.map(sub => 
                `<div class="result-item">${sub}</div>`
            ).join('');
            
            // Ports
            const ports = results.ports || [];
            document.getElementById('portCount').textContent = ports.length;
            document.getElementById('portList').innerHTML = ports.map(port => 
                `<div class="result-item">${port.host}:${port.port}</div>`
            ).join('');
            
            // Vulnerabilities
            const vulns = results.vulnerabilities || [];
            document.getElementById('vulnCount').textContent = vulns.length;
            document.getElementById('vulnList').innerHTML = vulns.map(vuln => 
                `<div class="vulnerability">${vuln.info?.name || 'Unknown vulnerability'}</div>`
            ).join('');
        }

        function resetUI() {
            document.getElementById('startBtn').disabled = false;
            currentScanId = null;
        }

        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }

        function showSuccess(message) {
            const successDiv = document.getElementById('success');
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        }

        function hideMessages() {
            document.getElementById('error').style.display = 'none';
            document.getElementById('success').style.display = 'none';
        }

        function downloadReport() {
            if (currentScanId) {
                window.open(`/report/${currentScanId}`, '_blank');
            }
        }
    </script>
</body>
</html>'''

class ScanManager:
    def __init__(self, scan_id, domain):
        self.scan_id = scan_id
        self.domain = domain
        self.status = "initializing"
        self.progress = 0
        self.current_task = "Initializing scan"
        self.results = {
            'subdomains': [],
            'ports': [],
            'vulnerabilities': []
        }
        self.start_time = datetime.now()
        self.end_time = None

def run_scan(scan_manager):
    """Run a mock scan with realistic timing"""
    try:
        # Subdomain Discovery
        scan_manager.status = "running"
        scan_manager.current_task = "Discovering subdomains"
        scan_manager.progress = 10
        time.sleep(2)
        
        scan_manager.results['subdomains'] = [
            scan_manager.domain,
            f"www.{scan_manager.domain}",
            f"api.{scan_manager.domain}",
            f"mail.{scan_manager.domain}",
            f"admin.{scan_manager.domain}",
            f"blog.{scan_manager.domain}"
        ]
        scan_manager.progress = 30
        
        # Port Scanning
        scan_manager.current_task = "Scanning ports"
        scan_manager.progress = 40
        time.sleep(3)
        
        mock_ports = []
        for subdomain in scan_manager.results['subdomains'][:4]:
            mock_ports.extend([
                {"host": subdomain, "port": 80, "protocol": "tcp"},
                {"host": subdomain, "port": 443, "protocol": "tcp"}
            ])
        if len(scan_manager.results['subdomains']) > 2:
            mock_ports.append({"host": scan_manager.results['subdomains'][2], "port": 22, "protocol": "tcp"})
        
        scan_manager.results['ports'] = mock_ports
        scan_manager.progress = 60
        
        # Vulnerability Scanning
        scan_manager.current_task = "Scanning for vulnerabilities"
        scan_manager.progress = 70
        time.sleep(3)
        
        mock_vulns = [
            {
                "template": "http-missing-security-headers",
                "info": {"name": "Missing Security Headers", "severity": "info"},
                "host": f"http://{scan_manager.domain}"
            },
            {
                "template": "ssl-weak-cipher",
                "info": {"name": "Weak SSL Cipher", "severity": "medium"},
                "host": f"https://{scan_manager.domain}"
            }
        ]
        
        # Add more vulnerabilities for demonstration
        if "admin" in str(scan_manager.results['subdomains']):
            mock_vulns.append({
                "template": "admin-panel-exposed",
                "info": {"name": "Admin Panel Exposed", "severity": "high"},
                "host": f"http://admin.{scan_manager.domain}"
            })
        
        scan_manager.results['vulnerabilities'] = mock_vulns
        scan_manager.progress = 90
        
        # Finalize
        scan_manager.current_task = "Generating report"
        scan_manager.progress = 95
        time.sleep(1)
        
        scan_manager.status = "completed"
        scan_manager.progress = 100
        scan_manager.current_task = "Scan completed successfully"
        scan_manager.end_time = datetime.now()
        
    except Exception as e:
        scan_manager.status = "failed"
        scan_manager.current_task = f"Scan failed: {str(e)}"
        scan_manager.end_time = datetime.now()

@app.route('/')
def index():
    """Main page"""
    return HTML_TEMPLATE

@app.route('/scan', methods=['POST'])
def start_scan():
    """Start a new scan"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'})
        
        # Basic domain validation
        if not domain.replace('.', '').replace('-', '').replace('_', '').isalnum():
            return jsonify({'success': False, 'error': 'Invalid domain format'})
        
        # Create new scan
        scan_id = str(uuid.uuid4())
        scan_manager = ScanManager(scan_id, domain)
        scans[scan_id] = scan_manager
        
        # Start scan in background thread
        thread = threading.Thread(target=run_scan, args=(scan_manager,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'scan_id': scan_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status/<scan_id>')
def get_status(scan_id):
    """Get scan status"""
    scan = scans.get(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({
        'scan_id': scan_id,
        'status': scan.status,
        'progress': scan.progress,
        'current_task': scan.current_task,
        'results': scan.results if scan.status == 'completed' else {}
    })

@app.route('/report/<scan_id>')
def download_report(scan_id):
    """Download scan report"""
    scan = scans.get(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    
    if scan.status != 'completed':
        return jsonify({'error': 'Scan not completed'}), 400
    
    # Generate report
    report = {
        'scan_id': scan_id,
        'domain': scan.domain,
        'start_time': scan.start_time.isoformat(),
        'end_time': scan.end_time.isoformat() if scan.end_time else None,
        'results': scan.results,
        'summary': {
            'subdomains_found': len(scan.results['subdomains']),
            'ports_found': len(scan.results['ports']),
            'vulnerabilities_found': len(scan.results['vulnerabilities'])
        }
    }
    
    response = app.response_class(
        response=json.dumps(report, indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = f'attachment; filename=scan_report_{scan_id}.json'
    return response

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Attack Surface Scanner - Single File Version")
    print("📍 Access the application at: http://localhost:5000")
    print("🔍 This version uses mock data for demonstration")
    print("💡 To deploy: Just copy this file and run with Flask installed")
    
    app.run(host='0.0.0.0', port=5000, debug=False)