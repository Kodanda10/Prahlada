#!/usr/bin/env python3
"""
Golden Standard Regression Test for Gemini Parser V2
"""
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import ast

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.gemini_parser_v2 import GeminiParserV2

def parse_list_string(s: str) -> List[str]:
    """Parse string representation of list from CSV"""
    if not s or s.strip() == "":
        return []
    try:
        # Handle simple comma separated if not bracketed
        if not s.strip().startswith("["):
            return [x.strip() for x in s.split(",") if x.strip()]
        return ast.literal_eval(s)
    except:
        return []

def normalize_text(s: str) -> str:
    """Normalize text for comparison"""
    if not s: return ""
    return s.strip().lower()

def run_regression_test(csv_path: Path):
    print(f"🚀 Starting Golden Standard Regression Test")
    print(f"📂 Loading Gold Standard: {csv_path}")
    
    parser = GeminiParserV2()
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results["total"] += 1
            tweet_id = row["tweet_id"]
            raw_text = row["raw_text"]
            
            print(f"\nProcessing Tweet {tweet_id}...")
            
            # Run Parser
            # Mocking a tweet object structure expected by parser
            tweet_input = {
                "tweet_id": tweet_id,
                "text": raw_text,
                "created_at": "2025-11-20T10:00:00Z", # Default if not provided
                "author_handle": "unknown"
            }
            
            parsed_output = parser.parse_tweet(tweet_input)
            v9 = parsed_output.get("parsed_data_v9", {})
            
            # Extract actual values
            actual_event = v9.get("event_type")
            actual_location = v9.get("location", {}) or {}
            actual_geo = v9.get("geo_hierarchy", {}) or {} # Future proofing if we update parser
            
            # If geo_hierarchy not present, try to map from location object
            if not actual_geo and actual_location:
                actual_geo = {
                    "district": actual_location.get("district"),
                    "ulb_name": actual_location.get("ulb"),
                    "canonical": actual_location.get("canonical")
                }
            
            actual_people = set(v9.get("people_mentioned", []))
            actual_schemes = set(v9.get("schemes_mentioned", []))
            
            # Extract expected values
            expected_event = row["expected_event_type"]
            expected_district = row["expected_district"]
            expected_ulb = row["expected_ulb_name"]
            expected_people = set(parse_list_string(row["expected_people_names"]))
            expected_schemes = set(parse_list_string(row["expected_schemes"]))
            
            # Compare
            failures = []
            
            # 1. Event Type
            if normalize_text(actual_event) != normalize_text(expected_event):
                failures.append(f"Event Mismatch: Expected '{expected_event}', Got '{actual_event}'")
            
            # 2. District (if expected)
            if expected_district:
                # Handle list of districts in expected (e.g. ["Prayagraj", "Mirzapur"])
                if expected_district.startswith("["):
                    exp_dists = set(parse_list_string(expected_district))
                    # Logic for multi-district support in parser needed, for now check if primary matches any
                    act_dist = actual_geo.get("district")
                    if act_dist not in exp_dists:
                         failures.append(f"District Mismatch: Expected one of {exp_dists}, Got '{act_dist}'")
                else:
                    if normalize_text(actual_geo.get("district")) != normalize_text(expected_district):
                        failures.append(f"District Mismatch: Expected '{expected_district}', Got '{actual_geo.get('district')}'")

            # 3. ULB (if expected)
            if expected_ulb:
                 actual_ulb = actual_geo.get("ulb_name") or actual_geo.get("ulb")
                 if normalize_text(actual_ulb) != normalize_text(expected_ulb):
                        failures.append(f"ULB Mismatch: Expected '{expected_ulb}', Got '{actual_ulb}'")
            
            # 4. People (Subset check)
            # Check if expected people are in actual people
            missing_people = expected_people - actual_people
            if missing_people:
                failures.append(f"Missing People: {missing_people}")
                
            # 5. Schemes (Subset check)
            missing_schemes = expected_schemes - actual_schemes
            if missing_schemes:
                failures.append(f"Missing Schemes: {missing_schemes}")
            
            if not failures:
                print(f"✅ PASS")
                results["passed"] += 1
            else:
                print(f"❌ FAIL")
                for fail in failures:
                    print(f"  - {fail}")
                results["failed"] += 1
                results["details"].append({
                    "tweet_id": tweet_id,
                    "failures": failures
                })

    print("\n" + "="*50)
    print(f"TEST RESULTS Summary")
    print("="*50)
    print(f"Total: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    accuracy = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
    print(f"Accuracy: {accuracy:.2f}%")
    print("="*50)

if __name__ == "__main__":
    csv_file = PROJECT_ROOT / "data" / "gold_standard_tweets.csv"
    if not csv_file.exists():
        print(f"Error: {csv_file} not found.")
        sys.exit(1)
    
    run_regression_test(csv_file)
