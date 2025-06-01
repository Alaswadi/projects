#!/usr/bin/env python3
"""
Simple test script to verify the Flask app works
"""

import requests
import time
import sys

def test_app(base_url="http://localhost:5000"):
    """Test the Flask application"""
    
    print(f"Testing Flask app at {base_url}")
    
    try:
        # Test 1: Check if app is running
        print("1. Testing if app is accessible...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ App is accessible")
        else:
            print(f"❌ App returned status code: {response.status_code}")
            return False
            
        # Test 2: Check if we can start a scan
        print("2. Testing scan initiation...")
        scan_data = {"domain": "example.com"}
        response = requests.post(f"{base_url}/scan", json=scan_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            scan_id = result.get('scan_id')
            print(f"✅ Scan started with ID: {scan_id}")
            
            # Test 3: Check scan status
            print("3. Testing scan status...")
            time.sleep(2)  # Wait a bit
            response = requests.get(f"{base_url}/status/{scan_id}", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Scan status: {status.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        else:
            print(f"❌ Scan initiation failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the app. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print("Attack Surface Scanner - Test Script")
    print("=" * 40)
    
    success = test_app(base_url)
    
    if success:
        print("\n🎉 All tests passed! The app is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the app logs.")
        sys.exit(1)