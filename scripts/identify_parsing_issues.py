#!/usr/bin/env python3
"""
Identify common parsing issues in Parser V2 output
"""
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

def identify_issues():
    input_file = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
    output_file = Path("docs/parsing_issues_report.md")
    
    tweets = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tweets.append(json.loads(line))
    
    # Issue trackers
    people_noise = []
    location_issues = []
    event_issues = []
    confidence_issues = []
    
    # Noise patterns for people extraction
    noise_patterns = [
        r'^का\s+',  # "का छत्तीसगढ़"
        r'^के\s+',  # "के रूप में", "के साथ"
        r'^में\s+', # "में भाजपा"
        r'^से\s+',  # "से लोक"
        r'^\S+\s+में$',  # "क्षेत्र में"
        r'^\S+\s+के$',  # "स्तरीय के"
        r'^उप$',  # Just "उप"
        r'^प्रत्याशी$',  # Just "प्रत्याशी"
    ]
    
    for tweet in tweets:
        v9 = tweet.get("parsed_data_v9", {})
        tweet_id = tweet.get("tweet_id")
        text = tweet.get("text", "")
        
        # 1. People Extraction Issues
        people = v9.get("people_mentioned", [])
        for person in people:
            for pattern in noise_patterns:
                if re.match(pattern, person):
                    people_noise.append({
                        "tweet_id": tweet_id,
                        "extracted": person,
                        "text_snippet": text[:100]
                    })
                    break
        
        # 2. Location Issues
        location = v9.get("location", {})
        source = location.get("source", "")
        
        # Check if temporal inference was used but explicit location exists
        if source == "temporal_inference":
            # Look for common location indicators
            location_indicators = [
                r'में\s+([^\s]+)',  # "Raipur में"
                r'([^\s]+)\s+में',  # "में Raipur"
                r'([^\s]+)\s+जिला',
                r'([^\s]+)\s+विधानसभा',
            ]
            for pattern in location_indicators:
                if re.search(pattern, text):
                    location_issues.append({
                        "tweet_id": tweet_id,
                        "issue": "temporal_inference_with_explicit_location",
                        "inferred_location": location.get("canonical"),
                        "text_snippet": text[:150]
                    })
                    break
        
        # 3. Event Classification Issues
        event_type = v9.get("event_type", "")
        
        # Check for "शहीद" context
        if "शहीद" in text:
            # If it's about historical figures, should be tribute, not security
            historical_markers = ["पुण्यतिथि", "जयंती", "स्मरण", "नमन", "श्रद्धांजलि"]
            if any(marker in text for marker in historical_markers):
                if event_type == "आंतरिक सुरक्षा / पुलिस":
                    event_issues.append({
                        "tweet_id": tweet_id,
                        "issue": "shahid_tribute_misclassified_as_security",
                        "current_event": event_type,
                        "text_snippet": text[:150]
                    })
        
        # 4. Confidence Calibration Issues
        confidence = v9.get("confidence", 0)
        
        # High confidence but temporal inference (should be lower)
        if confidence > 0.9 and source == "temporal_inference":
            confidence_issues.append({
                "tweet_id": tweet_id,
                "issue": "high_confidence_with_temporal_inference",
                "confidence": confidence,
                "location_source": source
            })
        
        # Low confidence but explicit location and event (should be higher)
        if confidence < 0.7 and source == "hierarchy_resolver" and event_type != "अन्य":
            confidence_issues.append({
                "tweet_id": tweet_id,
                "issue": "low_confidence_with_explicit_data",
                "confidence": confidence,
                "event": event_type,
                "location": location.get("canonical")
            })
    
    # Generate report
    report = f"""# Parsing Issues Report

## Summary
- **Total Tweets Analyzed**: {len(tweets):,}
- **People Extraction Noise**: {len(people_noise)} instances
- **Location Issues**: {len(location_issues)} instances
- **Event Classification Issues**: {len(event_issues)} instances
- **Confidence Calibration Issues**: {len(confidence_issues)} instances

---

## 1. People Extraction Noise ({len(people_noise)} instances)

Common noise patterns extracted as people:
"""
    
    # Count noise patterns
    noise_counter = Counter([item["extracted"] for item in people_noise])
    for noise, count in noise_counter.most_common(20):
        report += f"- **{noise}**: {count} occurrences\n"
    
    report += "\n### Sample Cases\n"
    for item in people_noise[:5]:
        report += f"- Tweet {item['tweet_id']}: Extracted `{item['extracted']}`\n"
        report += f"  - Text: {item['text_snippet']}...\n\n"
    
    report += f"\n---\n\n## 2. Location Issues ({len(location_issues)} instances)\n\n"
    report += "Tweets using temporal inference despite likely explicit location:\n\n"
    for item in location_issues[:10]:
        report += f"- Tweet {item['tweet_id']}: Inferred as `{item['inferred_location']}`\n"
        report += f"  - Text: {item['text_snippet']}...\n\n"
    
    report += f"\n---\n\n## 3. Event Classification Issues ({len(event_issues)} instances)\n\n"
    for item in event_issues[:10]:
        report += f"- Tweet {item['tweet_id']}: Classified as `{item['current_event']}`\n"
        report += f"  - Issue: {item['issue']}\n"
        report += f"  - Text: {item['text_snippet']}...\n\n"
    
    report += f"\n---\n\n## 4. Confidence Calibration Issues ({len(confidence_issues)} instances)\n\n"
    
    high_conf_temporal = [i for i in confidence_issues if i["issue"] == "high_confidence_with_temporal_inference"]
    low_conf_explicit = [i for i in confidence_issues if i["issue"] == "low_confidence_with_explicit_data"]
    
    report += f"### High Confidence with Temporal Inference ({len(high_conf_temporal)})\n"
    for item in high_conf_temporal[:5]:
        report += f"- Tweet {item['tweet_id']}: Confidence {item['confidence']:.2f}\n"
    
    report += f"\n### Low Confidence with Explicit Data ({len(low_conf_explicit)})\n"
    for item in low_conf_explicit[:5]:
        report += f"- Tweet {item['tweet_id']}: Confidence {item['confidence']:.2f}, Event: {item['event']}, Location: {item['location']}\n"
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Issues report generated: {output_file}")
    print(f"📊 Found {len(people_noise) + len(location_issues) + len(event_issues) + len(confidence_issues)} total issues")
    
    # Return issue counts for further processing
    return {
        "people_noise": people_noise,
        "location_issues": location_issues,
        "event_issues": event_issues,
        "confidence_issues": confidence_issues
    }

if __name__ == "__main__":
    identify_issues()
