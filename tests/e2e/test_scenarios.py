import requests
import json
import time

BASE_URL = "http://localhost:8000"

def get_auth_token():
    print("Logging in...")
    auth_payload = {"username": "admin", "password": "SuperSecurePassword123!"}
    try:
        auth_response = requests.post(f"{BASE_URL}/api/auth/login", json=auth_payload)
        if auth_response.status_code != 200:
            print(f"❌ Login failed: {auth_response.text}")
            return None
        return auth_response.json()["token"]
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def run_scenario(token, name, tweet_text, old_data, correction):
    print(f"\n--- Running Scenario: {name} ---")
    url = f"{BASE_URL}/api/cognitive/correct"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "tweet_id": f"test_scenario_{int(time.time())}",
        "text": tweet_text,
        "old_data": old_data,
        "correction": correction
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success ({duration:.2f}s)")
            print(f"Decision: {data.get('decision', {}).get('decision')}")
            # print(json.dumps(data.get('decision'), indent=2))
        else:
            print(f"❌ Failed ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_scenarios():
    token = get_auth_token()
    if not token:
        return

    # Scenario 1: Event Type Correction (Meeting -> Rally)
    run_scenario(token, "Event Type Fix", 
        "कल रायपुर में विशाल किसान रैली का आयोजन किया गया।",
        {"event_type": "बैठक"},
        {"field": "event_type", "old_value": "बैठक", "new_value": "रैली"}
    )

    # Scenario 2: Location Hierarchy Fix (Village -> City)
    run_scenario(token, "Location Hierarchy Fix",
        "माना में नया स्वास्थ्य केंद्र खुला।",
        {"location": {"village": "माना", "district": "Unknown"}},
        {"field": "location", "old_value": "village:माना", "new_value": "ulb:माना, district:रायपुर"}
    )

    # Scenario 3: Ambiguous Location (Raipur Village vs Raipur City)
    run_scenario(token, "Ambiguous Location Resolution",
        "रायपुर ग्राम पंचायत में बैठक हुई।",
        {"location": {"ulb": "रायपुर"}},
        {"field": "location", "old_value": "ulb:रायपुर", "new_value": "village:रायपुर, block:पाली"}
    )

    # Scenario 4: Missing Scheme Tag
    run_scenario(token, "Missing Scheme Tag",
        "पीएम आवास योजना के तहत घर मिले।",
        {"schemes_mentioned": []},
        {"field": "schemes_mentioned", "old_value": [], "new_value": ["PMAY"]}
    )

    # Scenario 5: Person Extraction (Incorrect Name)
    run_scenario(token, "Person Extraction Fix",
        "विधायक बृजमोहन अग्रवाल ने उद्घाटन किया।",
        {"people_canonical": ["बृजमोहन"]},
        {"field": "people_canonical", "old_value": ["बृजमोहन"], "new_value": ["Brijmohan Agrawal"]}
    )

    # Scenario 6: False Positive Event
    run_scenario(token, "False Positive Event",
        "कल बारिश होने की संभावना है।",
        {"event_type": "Other"},
        {"field": "event_type", "old_value": "Other", "new_value": "None"}
    )

    # Scenario 7: Multiple Locations (Primary vs Secondary)
    run_scenario(token, "Primary Location Selection",
        "बिलासपुर से चलकर रैली रायपुर पहुंची।",
        {"location": {"ulb": "बिलासपुर"}},
        {"field": "location", "old_value": "ulb:बिलासपुर", "new_value": "ulb:रायपुर"}
    )

    # Scenario 8: Community Tagging
    run_scenario(token, "Community Tagging",
        "गोंड समाज का सम्मेलन संपन्न।",
        {"communities": []},
        {"field": "communities", "old_value": [], "new_value": ["Gond"]}
    )

    # Scenario 9: Date Extraction Fix
    run_scenario(token, "Date Extraction Fix",
        "अगले सोमवार को शिविर लगेगा।",
        {"event_date": "Unknown"},
        {"field": "event_date", "old_value": "Unknown", "new_value": "Next Monday"}
    )

    # Scenario 10: Sentiment Correction
    run_scenario(token, "Sentiment Correction",
        "सड़क की हालत बहुत खराब है।",
        {"sentiment": "Neutral"},
        {"field": "sentiment", "old_value": "Neutral", "new_value": "Negative"}
    )

if __name__ == "__main__":
    test_scenarios()
