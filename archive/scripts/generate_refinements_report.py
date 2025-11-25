#!/usr/bin/env python3
"""
Generate comprehensive analysis report for Parser V2 refinements
"""
import json
from pathlib import Path
from collections import defaultdict, Counter

def analyze_parsed_output():
    input_file = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
    output_file = Path("docs/parser_v2_refinements_report.md")
    
    tweets = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tweets.append(json.loads(line))
    
    # Statistics
    total = len(tweets)
    location_sources = Counter()
    event_types = Counter()
    confidence_scores = []
    
    # Examples for each refinement
    patna_examples = []
    nava_raipur_examples = []
    sports_examples = []
    security_examples = []
    people_extraction_examples = []
    
    for tweet in tweets:
        v9 = tweet.get("parsed_data_v9", {})
        location = v9.get("location", {})
        
        # Collect stats
        location_sources[location.get("source", "unknown")] += 1
        event_types[v9.get("event_type", "unknown")] += 1
        confidence_scores.append(v9.get("confidence", 0))
        
        # Collect examples
        canonical = location.get("canonical", "")
        event_type = v9.get("event_type", "")
        
        if canonical == "Patna" and len(patna_examples) < 3:
            patna_examples.append(tweet)
        
        if canonical == "नवा रायपुर" and location.get("landmark_trigger") and len(nava_raipur_examples) < 3:
            nava_raipur_examples.append(tweet)
        
        if "खेल" in event_type and len(sports_examples) < 3:
            sports_examples.append(tweet)
        
        if "सुरक्षा" in event_type and len(security_examples) < 3:
            security_examples.append(tweet)
        
        people = v9.get("people_mentioned", [])
        if people and len(people) >= 3 and len(people_extraction_examples) < 3:
            people_extraction_examples.append(tweet)
    
    # Generate report
    report = f"""# Parser V2 Refinements - Analysis Report

## Overview
- **Total Tweets Parsed**: {total:,}
- **Average Confidence**: {sum(confidence_scores)/len(confidence_scores):.2%}
- **High Confidence (>0.9)**: {sum(1 for c in confidence_scores if c > 0.9):,} ({sum(1 for c in confidence_scores if c > 0.9)/total:.1%})

## Location Resolution Statistics
"""
    
    for source, count in location_sources.most_common():
        report += f"- **{source}**: {count:,} ({count/total:.1%})\n"
    
    report += f"\n## Event Classification Statistics\n"
    for event, count in event_types.most_common(10):
        report += f"- **{event}**: {count:,} ({count/total:.1%})\n"
    
    # Add examples
    report += "\n---\n\n# Refinement Examples\n\n"
    
    if patna_examples:
        report += "## 1. Patna/Bankipur Resolution\n\n"
        report += "**Before**: Patna tweets were incorrectly inferred as Bilaspur via temporal inference.\n\n"
        report += "**After**: Explicit detection via Static Landmarks.\n\n"
        for i, tweet in enumerate(patna_examples[:2], 1):
            report += f"### Example {i}\n```json\n{json.dumps(tweet, ensure_ascii=False, indent=2)}\n```\n\n"
    
    if nava_raipur_examples:
        report += "## 2. Nava Raipur Landmark Detection\n\n"
        report += "**Before**: 'Vidhan Sabha' resolved to generic 'Raipur'.\n\n"
        report += "**After**: Landmark triggers resolve to specific 'Nava Raipur'.\n\n"
        for i, tweet in enumerate(nava_raipur_examples[:2], 1):
            report += f"### Example {i}\n```json\n{json.dumps(tweet, ensure_ascii=False, indent=2)}\n```\n\n"
    
    if sports_examples:
        report += "## 3. Sports Event Classification\n\n"
        report += "**New Keywords**: मैच, जीत, पदक, खिलाड़ी, ओलंपिक, match, jeet, medal, won, winner\n\n"
        for i, tweet in enumerate(sports_examples[:2], 1):
            report += f"### Example {i}\n```json\n{json.dumps(tweet, ensure_ascii=False, indent=2)}\n```\n\n"
    
    if security_examples:
        report += "## 4. Security Event Classification\n\n"
        report += "**New Keywords**: नक्सल, माओवाद, शहीद, जवान, encounter, naxal, maowad, shahid\n\n"
        for i, tweet in enumerate(security_examples[:2], 1):
            report += f"### Example {i}\n```json\n{json.dumps(tweet, ensure_ascii=False, indent=2)}\n```\n\n"
    
    if people_extraction_examples:
        report += "## 5. Improved People Extraction\n\n"
        report += "**Improvements**:\n"
        report += "- Chained honorifics (e.g., 'Mananiya Mukhyamantri Shri')\n"
        report += "- Added 'महोदया', 'महोदय' to prevent extraction of 'Mahodaya ka Chhattisgarh'\n"
        report += "- Handles excluded from people_mentioned (used only for inference)\n\n"
        for i, tweet in enumerate(people_extraction_examples[:2], 1):
            report += f"### Example {i}\n```json\n{json.dumps(tweet, ensure_ascii=False, indent=2)}\n```\n\n"
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated: {output_file}")
    print(f"📊 Analyzed {total:,} tweets")

if __name__ == "__main__":
    analyze_parsed_output()
