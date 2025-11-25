#!/usr/bin/env python3
"""
Detailed Golden Standard Failure Analysis
"""
import csv
import json
from pathlib import Path
from scripts.gemini_parser_v2 import GeminiParserV2

def analyze_failures():
    golden_file = Path("data/gold_standard_tweets.csv")
    parser = GeminiParserV2()
    
    failures = []
    
    with open(golden_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweet_id = row["tweet_id"]
            text = row["text"]
            expected_ulb = row["expected_ulb"]
            expected_event = row["expected_event"]
            expected_people = row["expected_people"]
            
            # Parse
            record = {"tweet_id": tweet_id, "text": text, "created_at": "2025-01-01"}
            result = parser.parse_tweet(record)
            parsed = result["parsed_data_v9"]
            
            # Check failures
            actual_geo = parsed.get("location", {})
            actual_ulb = actual_geo.get("ulb_name") or actual_geo.get("ulb")
            actual_event = parsed.get("event_type", "")
            actual_people = set(parsed.get("people_mentioned", []))
            
            expected_people_set = set([p.strip() for p in expected_people.split("|") if p.strip()]) if expected_people else set()
            
            issues = []
            
            # ULB mismatch
            if expected_ulb and actual_ulb != expected_ulb:
                issues.append(f"ULB: Expected '{expected_ulb}', Got '{actual_ulb}'")
            
            # Event mismatch
            if expected_event and actual_event != expected_event:
                issues.append(f"Event: Expected '{expected_event}', Got '{actual_event}'")
            
            # People mismatch
            missing_people = expected_people_set - actual_people
            extra_people = actual_people - expected_people_set
            if missing_people:
                issues.append(f"Missing People: {missing_people}")
            if extra_people:
                issues.append(f"Extra People: {extra_people}")
            
            if issues:
                failures.append({
                    "tweet_id": tweet_id,
                    "text": text[:100],
                    "issues": issues,
                    "expected_people": expected_people_set,
                    "actual_people": actual_people
                })
    
    # Report
    print(f"\n{'='*80}")
    print(f"Golden Standard Failure Analysis - {len(failures)} Failures")
    print(f"{'='*80}\n")
    
    # Group by issue type
    ulb_failures = [f for f in failures if any("ULB:" in i for i in f["issues"])]
    event_failures = [f for f in failures if any("Event:" in i for i in f["issues"])]
    people_failures = [f for f in failures if any("People:" in i for i in f["issues"])]
    
    print(f"**Issue Breakdown:**")
    print(f"  ULB Mismatches: {len(ulb_failures)}")
    print(f"  Event Mismatches: {len(event_failures)}")
    print(f"  People Mismatches: {len(people_failures)}\n")
    
    print(f"**Detailed Failures:**\n")
    for i, failure in enumerate(failures[:20], 1):
        print(f"{i}. Tweet {failure['tweet_id']}")
        print(f"   Text: {failure['text']}...")
        for issue in failure['issues']:
            print(f"   ❌ {issue}")
        print()

if __name__ == "__main__":
    analyze_failures()
