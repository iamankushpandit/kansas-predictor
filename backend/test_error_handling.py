import pytest
import requests
import time

# Configuration
BASE_URL = "http://localhost:3001"
TIMEOUT = 30

class TestErrorHandling:
    """Isolated tests for error handling scenarios"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        print("Setting up error handling tests...")
        cls.wait_for_server()
        
    @classmethod
    def wait_for_server(cls, max_attempts=5):
        """Wait for server to be available"""
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    print("Server is ready!")
                    return
            except requests.exceptions.RequestException:
                pass
            print(f"Waiting for server... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
        raise Exception("Server not available after maximum attempts")

    def test_invalid_county(self):
        """Test handling of invalid county"""
        payload = {
            "county": "InvalidCounty",
            "claim_type": "emergency",
            "target_date": "2025-01-15"
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        print(f"Invalid county response: {response.status_code}")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
        
        # Invalid inputs may return 404 (not found) or 500 (server error)
        assert response.status_code in [404, 500]

    def test_invalid_claim_type(self):
        """Test handling of invalid claim type"""
        payload = {
            "county": "Johnson",
            "claim_type": "invalid_type",
            "target_date": "2025-01-15"
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        print(f"Invalid claim type response: {response.status_code}")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
        
        # Invalid inputs may return 404 (not found) or 500 (server error)
        assert response.status_code in [404, 500]

    def test_invalid_date_format(self):
        """Test handling of invalid date format"""
        payload = {
            "county": "Johnson",
            "claim_type": "emergency",
            "target_date": "invalid-date"
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        print(f"Invalid date response: {response.status_code}")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
        
        assert response.status_code in [400, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])