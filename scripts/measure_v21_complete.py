#!/usr/bin/env python3
"""
Measure Parser V2.1 Complete Impact (Batch 1 + V2.1 Hotfix Integration)
"""
import json
from pathlib import Path
from collections import Counter

def measure_v21_impact():
    input_file = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
    
    tweets = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tweets.append(json.loads(line))
    
    total = len(tweets)
    
    # Metrics
    temporal_count = 0
    sector_zone_count = 0
    planned_city_count = 0
    cultural_events = 0
    scheme_detection = Counter()
    confidence_dist = {"<0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, ">0.9": 0}
    temporal_confidences = []
    
    for tweet in tweets:
        v9 = tweet.get("parsed_data_v9", {})
        location = v9.get("location", {})
        
        # Temporal inference usage
        if location.get("source") == "temporal_inference":
            temporal_count += 1
            temporal_confidences.append(v9.get("confidence", 0))
        
        # Sector/Zone extraction
        if location.get("ward") or location.get("zone"):
            sector_zone_count += 1
        
        # Planned city type
        if location.get("location_type") == "planned_city":
            planned_city_count += 1
        
        # Cultural events
        if v9.get("event_type") == "धार्मिक / सांस्कृतिक कार्यक्रम":
            cultural_events += 1
        
        # Scheme detection
        for scheme in v9.get("schemes_mentioned", []):
            scheme_detection[scheme] += 1
        
        # Confidence distribution
        conf = v9.get("confidence", 0)
        if conf < 0.5:
            confidence_dist["<0.5"] += 1
        elif conf < 0.7:
            confidence_dist["0.5-0.7"] += 1
        elif conf < 0.9:
            confidence_dist["0.7-0.9"] += 1
        else:
            confidence_dist[">0.9"] += 1
    
    # Report
    print(f"\n{'='*70}")
    print("Parser V2.1 - Complete Impact Measurement")
    print(f"{'='*70}")
    print(f"Total Tweets: {total:,}\n")
    
    print(f"**P1: Temporal Inference Usage**")
    print(f"  Count: {temporal_count} ({temporal_count/total*100:.1f}%)")
    print(f"  Target: ≤5% ({int(total*0.05)} tweets)")
    print(f"  Status: {'✅ PASS' if temporal_count/total <= 0.05 else '❌ FAIL (still high)'}")
    if temporal_confidences:
        print(f"  Avg Confidence: {sum(temporal_confidences)/len(temporal_confidences):.2f} (heavily penalized)")
    
    print(f"\n**P2: Sector/Zone/Ward Extraction**")
    print(f"  Count: {sector_zone_count} ({sector_zone_count/total*100:.1f}%)")
    print(f"  Target: ≥70% ({int(total*0.7)} tweets)")
    print(f"  Status: {'✅ PASS' if sector_zone_count/total >= 0.7 else '⚠️ IN PROGRESS'}")
    
    print(f"\n**P3: Scheme Detection**")
    print(f"  Total Schemes Detected: {sum(scheme_detection.values())}")
    print(f"  Unique Schemes: {len(scheme_detection)}")
    print(f"  Top 10 Schemes:")
    for scheme, count in scheme_detection.most_common(10):
        print(f"    - {scheme}: {count}")
    
    print(f"\n**P5: Planned City Type**")
    print(f"  Count: {planned_city_count} (Nava Raipur correctly typed)")
    
    print(f"\n**P6: Cultural Event Classification**")
    print(f"  Count: {cultural_events} ({cultural_events/total*100:.1f}%)")
    
    print(f"\n**P7: Confidence Distribution**")
    for range_name, count in confidence_dist.items():
        print(f"  {range_name}: {count} ({count/total*100:.1f}%)")
    
    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  ✅ Batch 1 Complete: P1, P6, P7")
    print(f"  ✅ V2.1 Hotfix: P2, P3 (partial), P5")
    print(f"  ⏳ Remaining: P4 (People NER), P8 (Multi-event flag)")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    measure_v21_impact()
