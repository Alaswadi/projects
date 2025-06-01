#!/usr/bin/env python3
"""
Test script to verify security tools installation
"""

import subprocess
import sys

def test_tool(tool_name, command):
    """Test if a security tool is installed and working"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or "usage" in result.stderr.lower() or "help" in result.stderr.lower():
            print(f"✅ {tool_name}: OK")
            return True
        else:
            print(f"❌ {tool_name}: Failed (return code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {tool_name}: Timeout")
        return False
    except FileNotFoundError:
        print(f"❌ {tool_name}: Not found")
        return False
    except Exception as e:
        print(f"❌ {tool_name}: Error - {e}")
        return False

def main():
    print("🔧 Testing Security Tools Installation")
    print("=====================================")
    
    tools = [
        ("Subfinder", ["subfinder", "-h"]),
        ("Naabu", ["naabu", "-h"]),
        ("Nuclei", ["nuclei", "-h"]),
        ("Python", ["python3", "--version"]),
        ("Curl", ["curl", "--version"])
    ]
    
    results = []
    for tool_name, command in tools:
        results.append(test_tool(tool_name, command))
    
    print("\n📊 Test Results:")
    print("================")
    
    if all(results):
        print("✅ All tools are installed and working correctly!")
        return 0
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count} tool(s) failed the test.")
        return 1

if __name__ == "__main__":
    sys.exit(main())