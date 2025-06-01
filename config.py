#!/usr/bin/env python3
"""
Configuration settings for Attack Surface Scanner
"""

import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    # Scan settings
    MAX_SCAN_TIME = 1800  # 30 minutes max scan time
    CLEANUP_INTERVAL = 3600  # Clean up old scans every hour
    MAX_CONCURRENT_SCANS = 1  # Maximum concurrent scans per instance
    
    # Tool configurations
    SUBFINDER_CONFIG = {
        'timeout': 300,  # 5 minutes
        'sources': 'passive',  # Use only passive sources
        'max_subdomains': 1000  # Limit results for performance
    }
    
    NAABU_CONFIG = {
        'timeout': 600,  # 10 minutes
        'top_ports': 100,  # Scan top 100 ports
        'rate': 1000,  # Packets per second
        'retries': 1
    }
    
    NUCLEI_CONFIG = {
        'timeout': 900,  # 15 minutes
        'templates': ['cves/', 'vulnerabilities/'],
        'rate_limit': 150,  # Requests per second
        'bulk_size': 25,
        'concurrency': 25
    }
    
    # File paths
    TEMP_DIR = '/tmp/scans'
    TOOLS_PATH = {
        'subfinder': '/root/go/bin/subfinder',
        'naabu': '/root/go/bin/naabu',
        'nuclei': '/root/go/bin/nuclei'
    }

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}