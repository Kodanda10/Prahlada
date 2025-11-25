import json
import csv
import sys
from pathlib import Path

def generate_csv():
    input_path = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
    output_path = Path("data/gold_standard_tweets.csv")
    
    print(f"Reading from {input_path}")
    
    rows = []
    with open(input_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                v9 = data.get("parsed_data_v9", {})
                geo = v9.get("geo_hierarchy") or {}
                loc = v9.get("location") or {}
                
                # Prepare row
                row = {
                    "tweet_id": data.get("tweet_id", ""),
                    "raw_text": data.get("text", "").replace("\n", " "),
                    "expected_event_type": v9.get("event_type", "अन्य"),
                    "expected_event_date": v9.get("event_date", ""),
                    "expected_location_raw": loc.get("canonical", "") if loc else "",
                    "expected_location_type": loc.get("location_type", "") if loc else "",
                    "expected_state": geo.get("state", "Chhattisgarh") if geo else "Chhattisgarh",
                    "expected_district": geo.get("district", "") if geo else "",
                    "expected_assembly_constituency": geo.get("assembly_constituency", "") if geo else "",
                    "expected_block": "", # Parser doesn't extract block yet
                    "expected_gp_or_ward": "",
                    "expected_ulb_name": geo.get("ulb_name", "") if geo else "",
                    "expected_people_handles": [], # Parser mixes handles in people_mentioned
                    "expected_people_names": v9.get("people_mentioned", []),
                    "expected_schemes": v9.get("schemes_mentioned", []),
                    "expected_hashtags": [],
                    "expected_target_groups": v9.get("target_groups", []),
                    "expected_communities": v9.get("communities", []),
                    "expected_organizations": v9.get("organizations", []),
                    "expected_security_type": "",
                    "expected_sentiment_political": "",
                    "notes": f"Auto-generated from Parser V2 (Confidence: {v9.get('confidence', 0)})"
                }
                rows.append(row)
            except Exception as e:
                print(f"Error processing line: {e}")
                continue

    # Write CSV
    fieldnames = [
        "tweet_id", "raw_text", "expected_event_type", "expected_event_date", 
        "expected_location_raw", "expected_location_type", "expected_state", 
        "expected_district", "expected_assembly_constituency", "expected_block", 
        "expected_gp_or_ward", "expected_ulb_name", "expected_people_handles", 
        "expected_people_names", "expected_schemes", "expected_hashtags", 
        "expected_target_groups", "expected_communities", "expected_organizations", 
        "expected_security_type", "expected_sentiment_political", "notes"
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Convert lists to string representation
            for k, v in row.items():
                if isinstance(v, list):
                    row[k] = json.dumps(v, ensure_ascii=False)
            writer.writerow(row)
            
    print(f"✅ Generated {len(rows)} rows in {output_path}")

if __name__ == "__main__":
    generate_csv()
