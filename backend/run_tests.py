#!/usr/bin/env python3
"""
Test runner for Kansas Claims Predictor Backend API
Runs comprehensive tests and generates detailed reports
"""

import subprocess
import sys
import os
import time
import requests
from datetime import datetime

def check_server_running():
    """Check if the backend server is running"""
    try:
        response = requests.get("http://localhost:3001/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def install_test_dependencies():
    """Install test dependencies"""
    print("Installing test dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"])
        print("SUCCESS: Test dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install test dependencies: {e}")
        return False

def run_tests():
    """Run the test suite with detailed reporting"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test command with various output formats
    cmd = [
        sys.executable, "-m", "pytest", 
        "test_backend.py",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        f"--html=test_report_{timestamp}.html",  # HTML report
        "--self-contained-html",  # Embed CSS/JS in HTML
        f"--json-report-file=test_report_{timestamp}.json",  # JSON report
        "--json-report-summary",  # Include summary in JSON
    ]
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main test execution function"""
    print("Kansas Claims Predictor Backend API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        print("WARNING: Backend server is not running!")
        print("Please start the server first:")
        print("  cd backend")
        print("  python main.py")
        print("\nWaiting 10 seconds for server to start...")
        time.sleep(10)
        
        if not check_server_running():
            print("ERROR: Server still not available. Please start the backend server manually.")
            return False
    
    print("SUCCESS: Backend server is running")
    
    # Install dependencies
    if not install_test_dependencies():
        return False
    
    # Run tests
    print("\nStarting test execution...")
    success = run_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS: ALL TESTS PASSED!")
        print("Test reports generated:")
        print("  - HTML report: test_report_*.html")
        print("  - JSON report: test_report_*.json")
    else:
        print("\n" + "=" * 60)
        print("ERROR: SOME TESTS FAILED!")
        print("Check the test reports for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)