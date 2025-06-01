# Self-contained Dockerfile - no external file dependencies
FROM python:3.11-slim

# Install system dependencies and Flask in one layer
RUN apt-get update && \
    apt-get install -y curl && \
    pip install Flask==2.3.3 Werkzeug==2.3.7 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app /tmp/scans

# Set working directory
WORKDIR /app

# Create a simple Flask app using echo
RUN echo 'from flask import Flask, request, jsonify' > app.py && \
    echo 'import json, uuid, time, threading' >> app.py && \
    echo 'from datetime import datetime' >> app.py && \
    echo '' >> app.py && \
    echo 'app = Flask(__name__)' >> app.py && \
    echo 'scans = {}' >> app.py && \
    echo '' >> app.py && \
    echo '@app.route("/")' >> app.py && \
    echo 'def index():' >> app.py && \
    echo '    return """' >> app.py && \
    echo '<!DOCTYPE html>' >> app.py && \
    echo '<html><head><title>Attack Surface Scanner</title>' >> app.py && \
    echo '<style>' >> app.py && \
    echo 'body{font-family:Arial,sans-serif;max-width:800px;margin:50px auto;padding:20px;background:#f5f5f5}' >> app.py && \
    echo '.container{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}' >> app.py && \
    echo 'h1{color:#333;text-align:center;margin-bottom:30px}' >> app.py && \
    echo '.form-group{margin-bottom:20px}' >> app.py && \
    echo 'label{display:block;margin-bottom:5px;font-weight:bold}' >> app.py && \
    echo 'input{width:100%;padding:10px;border:1px solid #ddd;border-radius:5px;font-size:16px}' >> app.py && \
    echo 'button{background:#007bff;color:white;padding:12px 24px;border:none;border-radius:5px;cursor:pointer;font-size:16px}' >> app.py && \
    echo 'button:hover{background:#0056b3}' >> app.py && \
    echo '.progress{display:none;margin:20px 0}' >> app.py && \
    echo '.progress-bar{width:100%;height:20px;background:#e9ecef;border-radius:10px;overflow:hidden}' >> app.py && \
    echo '.progress-fill{height:100%;background:#007bff;width:0%;transition:width 0.3s}' >> app.py && \
    echo '.results{display:none;margin-top:20px}' >> app.py && \
    echo '.result-section{margin:20px 0;padding:15px;background:#f8f9fa;border-radius:5px}' >> app.py && \
    echo '.result-item{padding:5px 0;border-bottom:1px solid #eee;font-family:monospace}' >> app.py && \
    echo '</style></head><body>' >> app.py && \
    echo '<div class="container">' >> app.py && \
    echo '<h1>🔍 Attack Surface Scanner</h1>' >> app.py && \
    echo '<form id="scanForm">' >> app.py && \
    echo '<div class="form-group">' >> app.py && \
    echo '<label for="domain">Target Domain:</label>' >> app.py && \
    echo '<input type="text" id="domain" placeholder="example.com" required>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '<button type="submit">Start Scan</button>' >> app.py && \
    echo '</form>' >> app.py && \
    echo '<div class="progress" id="progress">' >> app.py && \
    echo '<div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>' >> app.py && \
    echo '<p id="progressText">Starting scan...</p>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '<div class="results" id="results">' >> app.py && \
    echo '<div class="result-section">' >> app.py && \
    echo '<h3>Subdomains (<span id="subCount">0</span>)</h3>' >> app.py && \
    echo '<div id="subList"></div>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '<div class="result-section">' >> app.py && \
    echo '<h3>Ports (<span id="portCount">0</span>)</h3>' >> app.py && \
    echo '<div id="portList"></div>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '<div class="result-section">' >> app.py && \
    echo '<h3>Vulnerabilities (<span id="vulnCount">0</span>)</h3>' >> app.py && \
    echo '<div id="vulnList"></div>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '</div>' >> app.py && \
    echo '<script>' >> app.py && \
    echo 'let scanId = null;' >> app.py && \
    echo 'document.getElementById("scanForm").onsubmit = function(e) {' >> app.py && \
    echo 'e.preventDefault();' >> app.py && \
    echo 'const domain = document.getElementById("domain").value;' >> app.py && \
    echo 'fetch("/scan", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({domain:domain})})' >> app.py && \
    echo '.then(r => r.json())' >> app.py && \
    echo '.then(data => {' >> app.py && \
    echo 'if(data.success) {' >> app.py && \
    echo 'scanId = data.scan_id;' >> app.py && \
    echo 'document.getElementById("progress").style.display = "block";' >> app.py && \
    echo 'checkProgress();' >> app.py && \
    echo '} else alert("Error: " + data.error);' >> app.py && \
    echo '});' >> app.py && \
    echo '};' >> app.py && \
    echo 'function checkProgress() {' >> app.py && \
    echo 'if(!scanId) return;' >> app.py && \
    echo 'fetch("/status/" + scanId)' >> app.py && \
    echo '.then(r => r.json())' >> app.py && \
    echo '.then(data => {' >> app.py && \
    echo 'document.getElementById("progressFill").style.width = data.progress + "%";' >> app.py && \
    echo 'document.getElementById("progressText").textContent = data.current_task;' >> app.py && \
    echo 'if(data.status === "completed") {' >> app.py && \
    echo 'showResults(data.results);' >> app.py && \
    echo '} else if(data.status !== "failed") {' >> app.py && \
    echo 'setTimeout(checkProgress, 2000);' >> app.py && \
    echo '}' >> app.py && \
    echo '});' >> app.py && \
    echo '}' >> app.py && \
    echo 'function showResults(results) {' >> app.py && \
    echo 'document.getElementById("progress").style.display = "none";' >> app.py && \
    echo 'document.getElementById("results").style.display = "block";' >> app.py && \
    echo 'document.getElementById("subCount").textContent = results.subdomains.length;' >> app.py && \
    echo 'document.getElementById("subList").innerHTML = results.subdomains.map(s => "<div class=\\"result-item\\">" + s + "</div>").join("");' >> app.py && \
    echo 'document.getElementById("portCount").textContent = results.ports.length;' >> app.py && \
    echo 'document.getElementById("portList").innerHTML = results.ports.map(p => "<div class=\\"result-item\\">" + p.host + ":" + p.port + "</div>").join("");' >> app.py && \
    echo 'document.getElementById("vulnCount").textContent = results.vulnerabilities.length;' >> app.py && \
    echo 'document.getElementById("vulnList").innerHTML = results.vulnerabilities.map(v => "<div class=\\"result-item\\">" + v.info.name + "</div>").join("");' >> app.py && \
    echo '}' >> app.py && \
    echo '</script></body></html>"""' >> app.py && \
    echo '' >> app.py

# Add the Python backend code
RUN echo 'class ScanManager:' >> app.py && \
    echo '    def __init__(self, scan_id, domain):' >> app.py && \
    echo '        self.scan_id = scan_id' >> app.py && \
    echo '        self.domain = domain' >> app.py && \
    echo '        self.status = "initializing"' >> app.py && \
    echo '        self.progress = 0' >> app.py && \
    echo '        self.current_task = "Starting scan"' >> app.py && \
    echo '        self.results = {"subdomains": [], "ports": [], "vulnerabilities": []}' >> app.py && \
    echo '' >> app.py && \
    echo 'def run_scan(scan_manager):' >> app.py && \
    echo '    scan_manager.status = "running"' >> app.py && \
    echo '    scan_manager.current_task = "Discovering subdomains"' >> app.py && \
    echo '    scan_manager.progress = 25' >> app.py && \
    echo '    time.sleep(2)' >> app.py && \
    echo '    scan_manager.results["subdomains"] = [scan_manager.domain, f"www.{scan_manager.domain}", f"api.{scan_manager.domain}"]' >> app.py && \
    echo '    scan_manager.current_task = "Scanning ports"' >> app.py && \
    echo '    scan_manager.progress = 50' >> app.py && \
    echo '    time.sleep(2)' >> app.py && \
    echo '    scan_manager.results["ports"] = [{"host": scan_manager.domain, "port": 80}, {"host": scan_manager.domain, "port": 443}]' >> app.py && \
    echo '    scan_manager.current_task = "Checking vulnerabilities"' >> app.py && \
    echo '    scan_manager.progress = 75' >> app.py && \
    echo '    time.sleep(2)' >> app.py && \
    echo '    scan_manager.results["vulnerabilities"] = [{"info": {"name": "Demo Vulnerability"}}]' >> app.py && \
    echo '    scan_manager.status = "completed"' >> app.py && \
    echo '    scan_manager.progress = 100' >> app.py && \
    echo '    scan_manager.current_task = "Scan complete"' >> app.py && \
    echo '' >> app.py && \
    echo '@app.route("/scan", methods=["POST"])' >> app.py && \
    echo 'def start_scan():' >> app.py && \
    echo '    data = request.get_json()' >> app.py && \
    echo '    domain = data.get("domain", "").strip()' >> app.py && \
    echo '    if not domain:' >> app.py && \
    echo '        return jsonify({"success": False, "error": "Domain required"})' >> app.py && \
    echo '    scan_id = str(uuid.uuid4())' >> app.py && \
    echo '    scan_manager = ScanManager(scan_id, domain)' >> app.py && \
    echo '    scans[scan_id] = scan_manager' >> app.py && \
    echo '    threading.Thread(target=run_scan, args=(scan_manager,), daemon=True).start()' >> app.py && \
    echo '    return jsonify({"success": True, "scan_id": scan_id})' >> app.py && \
    echo '' >> app.py && \
    echo '@app.route("/status/<scan_id>")' >> app.py && \
    echo 'def get_status(scan_id):' >> app.py && \
    echo '    scan = scans.get(scan_id)' >> app.py && \
    echo '    if not scan:' >> app.py && \
    echo '        return jsonify({"error": "Scan not found"}), 404' >> app.py && \
    echo '    return jsonify({' >> app.py && \
    echo '        "status": scan.status,' >> app.py && \
    echo '        "progress": scan.progress,' >> app.py && \
    echo '        "current_task": scan.current_task,' >> app.py && \
    echo '        "results": scan.results if scan.status == "completed"
#!/usr/bin/env python3
import os
import json
import uuid
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
scans = {}

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
            
            const subdomains = results.subdomains || [];
            document.getElementById('subCount').textContent = subdomains.length;
            document.getElementById('subList').innerHTML = subdomains.map(sub => 
                `<div class="result-item">${sub}</div>`
            ).join('');
            
            const ports = results