import requests
import json
import time

def test_cognitive_engine_e2e():
    base_url = "http://localhost:8000"
    
    # 1. Login
    print("Logging in...")
    auth_payload = {"username": "admin", "password": "SuperSecurePassword123!"} # Credentials from .env
    try:
        auth_response = requests.post(f"{base_url}/api/auth/login", json=auth_payload)
        if auth_response.status_code != 200:
            print(f"❌ Login failed: {auth_response.text}")
            return
        
        token = auth_response.json()["token"]
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return

    # 2. Trigger Cognitive Engine
    url = f"{base_url}/api/cognitive/correct"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "tweet_id": "test_e2e_001",
        "text": "कल रायपुर में विशाल किसान रैली का आयोजन किया गया।",
        "old_data": {
            "event_type": "बैठक",
            "confidence": 0.6
        },
        "correction": {
            "field": "event_type",
            "old_value": "बैठक",
            "new_value": "रैली"
        }
    }
    
    print(f"Sending request to {url}...")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        duration = time.time() - start_time
        
        print(f"Response Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print("Response Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Assertions
            assert data["status"] == "success"
            assert "decision" in data
            assert "details" in data
            print("✅ E2E Test Passed!")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on port 8000?")

if __name__ == "__main__":
    test_cognitive_engine_e2e()
