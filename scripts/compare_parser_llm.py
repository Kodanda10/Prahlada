#!/usr/bin/env python3
import sys
import os
import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import Parsers
from scripts.gemini_parser_v2 import GeminiParserV2
from backend.cognitive.phi_adapter import PhiAdapter, set_phi_adapter_config

def main():
    print("🚀 Starting Parser Comparison: Rule-Based V2 vs. Hybrid V3 (Phi 3.5)")
    
    # 1. Load Gold Standard Data
    csv_path = PROJECT_ROOT / "data" / "gold_standard_tweets.csv"
    if not csv_path.exists():
        print(f"❌ Error: Gold standard file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    # Take a sample of 10 tweets for analysis
    sample_df = df.head(10)
    
    # 2. Initialize Parsers
    print("Initializing Parsers...")
    
    # Enable Phi Adapter globally for V3
    set_phi_adapter_config(enabled=True)
    
    # V2: Cognitive Disabled
    print("Initializing V2 (Rule-Based)...")
    parser_v2 = GeminiParserV2(enable_semantic=False)
    parser_v2.enable_cognitive = False
    
    # V3: Cognitive Enabled
    print("Initializing V3 (Hybrid)...")
    parser_v3 = GeminiParserV2(enable_semantic=False)
    parser_v3.enable_cognitive = True
    
    # Check if Phi is available
    if not parser_v3.phi_adapter.check_health():
        print("⚠️ Warning: Phi 3.5 service is NOT available. V3 will degrade to V2 behavior.")
    else:
        print("✅ Phi 3.5 Service is ONLINE.")

    results = []

    print(f"\nProcessing {len(sample_df)} tweets...")
    
    for index, row in sample_df.iterrows():
        tweet_id = str(row.get('tweet_id', index))
        raw_text = row.get('raw_text', '')
        expected_event = row.get('expected_event_type', 'Unknown')
        expected_location = row.get('expected_location_raw', 'Unknown')
        
        print(f"[{index+1}/{len(sample_df)}] Processing Tweet {tweet_id}...")
        
        # Mock record structure
        record = {
            "tweet_id": tweet_id,
            "raw_text": raw_text,
            "created_at": "2025-11-20T10:00:00"
        }
        
        # A. Run V2
        v2_result = parser_v2.parse_tweet(record)
        v2_data = v2_result.get('parsed_data_v9', {})
        
        # B. Run V3
        v3_result = parser_v3.parse_tweet(record)
        v3_data = v3_result.get('parsed_data_v9', {})
        
        # Format Semantic Buckets
        sem_buckets = v3_data.get('semantic_buckets', [])
        sem_buckets_str = "<br>".join([f"{b['word']} ({b['type']})" for b in sem_buckets])

        # Format Cognitive View
        cog_view = v3_data.get('cognitive_view', {})
        themes = f"**Primary:** {cog_view.get('primary_theme', 'N/A')}<br>**Tags:** {', '.join(cog_view.get('sector_tags', []))}"
        
        stakeholders = cog_view.get('stakeholders', {})
        if isinstance(stakeholders, list):
            # Fallback if Phi returns a list
            people = "N/A (List Format)"
            orgs = "N/A (List Format)"
        else:
            people = ", ".join([p.get('name', 'Unknown') for p in stakeholders.get('people', [])])
            orgs = ", ".join([o.get('name', 'Unknown') for o in stakeholders.get('organizations', [])])
            
        stakeholders_str = f"**People:** {people}<br>**Orgs:** {orgs}"

        # C. Compare
        results.append({
            "tweet_id": tweet_id,
            "text_snippet": raw_text[:50] + "...",
            "v3_event": v3_data.get('event_type'),
            "v3_sub_event": v3_data.get('sub_event_type'),
            "v3_location": v3_data.get('location', {}).get('canonical', 'None') if v3_data.get('location') else "None",
            "v3_themes": themes,
            "v3_stakeholders": stakeholders_str,
            "v3_reasoning": v3_data.get('reasoning_trace', '')
        })

    # 3. Generate Report
    report_path = PROJECT_ROOT / "comparison_report_v5.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Parser Comparison Report: V5.0 (Cognitive Knowledge Engine)\n\n")
        f.write(f"**Date:** {pd.Timestamp.now()}\n")
        f.write(f"**Sample Size:** {len(sample_df)}\n\n")
        
        f.write("## Detailed Comparison\n\n")
        f.write("| Tweet ID | Text | Event (Sub-Event) | Location | Cognitive Themes | Stakeholders | Reasoning |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        
        for r in results:
            v3_event_display = f"**{r['v3_event']}**"
            if r['v3_sub_event']:
                v3_event_display += f"<br>({r['v3_sub_event']})"
            
            f.write(f"| {r['tweet_id']} | {r['text_snippet']} | {v3_event_display} | **{r['v3_location']}** | {r['v3_themes']} | {r['v3_stakeholders']} | {r['v3_reasoning']} |\n")
            
        f.write("\n## Analysis Summary\n")
        f.write("Check if V5.0 correctly extracts rich Cognitive Views (Themes, Stakeholders).\n")

    print(f"\n✅ Comparison Complete. Report generated at: {report_path}")

if __name__ == "__main__":
    main()
