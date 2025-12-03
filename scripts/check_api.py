import sys
print("Script starting...")
try:
    import requests
    import os
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

load_dotenv()

def check_api():
    print("Checking API...")
    # Try to login first to get token
    login_payload = {"username": "admin", "password": "admin123"}
    try:
        auth_resp = requests.post("http://localhost:8000/api/auth/login", json=login_payload)
        print(f"Login Status: {auth_resp.status_code}")
        if auth_resp.status_code != 200:
            print(f"Login Failed: {auth_resp.text}")
            return

        token = auth_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get events
        resp = requests.get("http://localhost:8000/api/events", headers=headers)
        print(f"Events Status: {resp.status_code}")
        if resp.status_code == 200:
            events = resp.json()
            print(f"Events Count: {len(events)}")
            if len(events) > 0:
                print(f"First Event ID: {events[0]['tweet_id']}")
                print(f"First Event Status: {events[0].get('review_status')}")
        else:
            print(f"Events Error: {resp.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
