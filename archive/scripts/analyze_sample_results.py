import json
from collections import Counter

def analyze_results():
    input_path = "data/parsed_user_sample_v2.jsonl"
    output_path = "docs/user_sample_analysis_report.md"
    
    total_tweets = 0
    event_counts = Counter()
    location_counts = Counter()
    people_counts = Counter()
    confidence_scores = []
    
    results = []
    
    with open(input_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            total_tweets += 1
            v9 = data.get("parsed_data_v9", {})
            
            # Event Type
            event_type = v9.get("event_type", "Unknown")
            event_counts[event_type] += 1
            
            # Location
            loc = v9.get("location")
            loc_source = "None"
            if loc:
                loc_name = loc.get("canonical", "Unknown")
                loc_source = loc.get("source", "Unknown")
                location_counts[loc_name] += 1
            
            # People
            people = v9.get("people_mentioned", [])
            for p in people:
                people_counts[p] += 1
                
            # Confidence
            conf = v9.get("confidence", 0)
            confidence_scores.append(conf)
            
            results.append({
                "id": data.get("tweet_id"),
                "text": data.get("text"),
                "event": event_type,
                "location": loc.get("canonical") if loc else None,
                "source": loc_source,
                "people": people,
                "confidence": conf
            })

    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    # Generate Report
    report = f"""# 📊 Parsing Quality Analysis Report
**Dataset**: User Provided Sample ({total_tweets} tweets)
**Model**: Gemini Parser V2

## 1. Overall Metrics
*   **Total Tweets**: {total_tweets}
*   **Average Confidence**: {avg_confidence:.2f}
*   **Location Extraction Rate**: {sum(location_counts.values())}/{total_tweets} ({sum(location_counts.values())/total_tweets*100:.1f}%)

## 2. Event Type Distribution
"""
    for event, count in event_counts.most_common():
        report += f"*   **{event}**: {count}\n"
        
    report += "\n## 3. Top Locations Extracted\n"
    for loc, count in location_counts.most_common(10):
        report += f"*   **{loc}**: {count}\n"
        
    report += "\n## 4. Top People Mentioned\n"
    for person, count in people_counts.most_common(10):
        report += f"*   **{person}**: {count}\n"
        
    report += "\n## 5. Detailed Examples (Sample)\n"
    
    # Good Examples (High Confidence + Location)
    report += "### ✅ High Quality Parses\n"
    good_examples = [r for r in results if r['confidence'] > 0.8 and r['location']][:5]
    for r in good_examples:
        report += f"**Tweet**: \"{r['text'][:100]}...\"\n"
        report += f"*   **Event**: {r['event']}\n"
        report += f"*   **Location**: {r['location']} (Source: {r['source']})\n"
        report += f"*   **People**: {', '.join(r['people'])}\n"
        report += f"*   **Confidence**: {r['confidence']}\n\n"
        
    # Bad Examples (Low Confidence or Missed Location)
    report += "### ⚠️ Potential Issues (Low Confidence / No Location)\n"
    bad_examples = [r for r in results if r['confidence'] < 0.7][:5]
    for r in bad_examples:
        report += f"**Tweet**: \"{r['text'][:100]}...\"\n"
        report += f"*   **Event**: {r['event']}\n"
        report += f"*   **Location**: {r['location']}\n"
        report += f"*   **Confidence**: {r['confidence']}\n\n"
        
    # Temporal Inference Check
    report += "### 🕒 Temporal Inference Examples\n"
    temporal_examples = [r for r in results if r['source'] == 'temporal_inference'][:5]
    if temporal_examples:
        for r in temporal_examples:
            report += f"**Tweet**: \"{r['text'][:100]}...\"\n"
            report += f"*   **Inferred Location**: {r['location']}\n"
            report += f"*   **Reason**: No explicit location found, inferred from context.\n\n"

    with open(output_path, 'w') as f:
        f.write(report)
        
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    analyze_results()
