#!/usr/bin/env python3
"""
Measure Parser V2.1 Batch 1 Impact
"""
import json
from pathlib import Path
from collections import Counter

def measure_batch1_impact():
    input_file = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
    
    tweets = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tweets.append(json.loads(line))
    
    total = len(tweets)
    
    # Metrics
    temporal_count = 0
    cultural_events = 0
    confidence_dist = {"<0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, ">0.9": 0}
    temporal_confidences = []
    
    for tweet in tweets:
        v9 = tweet.get("parsed_data_v9", {})
        location = v9.get("location", {})
        
        # Temporal inference usage
        if location.get("source") == "temporal_inference":
            temporal_count += 1
            temporal_confidences.append(v9.get("confidence", 0))
        
        # Cultural events
        if v9.get("event_type") == "धार्मिक / सांस्कृतिक कार्यक्रम":
            cultural_events += 1
        
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
    print(f"\\n{'='*60}")
    print("Parser V2.1 Batch 1 - Impact Measurement")
    print(f"{'='*60}")
    print(f"Total Tweets: {total:,}")
    print(f"\\n**Temporal Inference Usage**")
    print(f"  Count: {temporal_count} ({temporal_count/total*100:.1f}%)")
    print(f"  Target: ≤5% ({int(total*0.05)} tweets)")
    print(f"  Status: {'✅ PASS' if temporal_count/total <= 0.05 else '❌ FAIL'}")
    if temporal_confidences:
        print(f"  Avg Confidence: {sum(temporal_confidences)/len(temporal_confidences):.2f}")
    
    print(f"\\n**Cultural Event Classification**")
    print(f"  Count: {cultural_events} ({cultural_events/total*100:.1f}%)")
    
    print(f"\\n**Confidence Distribution**")
    for range_name, count in confidence_dist.items():
        print(f"  {range_name}: {count} ({count/total*100:.1f}%)")
    
    print(f"\\n{'='*60}")

if __name__ == "__main__":
    measure_batch1_impact()
