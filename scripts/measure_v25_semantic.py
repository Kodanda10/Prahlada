#!/usr/bin/env python3
"""
Measure Parser V2.5 Semantic Richness Impact
"""
import json
from pathlib import Path
from collections import Counter

def measure_semantic_richness():
    input_file = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
    
    tweets = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tweets.append(json.loads(line))
    
    total = len(tweets)
    
    # Semantic richness metrics
    people_filled = 0
    schemes_filled = 0
    target_groups_filled = 0
    communities_filled = 0
    orgs_filled = 0
    
    people_count = Counter()
    scheme_count = Counter()
    target_group_count = Counter()
    community_count = Counter()
    org_count = Counter()
    
    for tweet in tweets:
        v9 = tweet.get("parsed_data_v9", {})
        
        # People
        people = [p for p in v9.get("people_mentioned", []) if not p.startswith("@")]
        if people:
            people_filled += 1
            for p in people:
                people_count[p] += 1
        
        # Schemes
        schemes = v9.get("schemes_mentioned", [])
        if schemes:
            schemes_filled += 1
            for s in schemes:
                scheme_count[s] += 1
        
        # Target Groups
        target_groups = v9.get("target_groups", [])
        if target_groups:
            target_groups_filled += 1
            for tg in target_groups:
                target_group_count[tg] += 1
        
        # Communities
        communities = v9.get("communities", [])
        if communities:
            communities_filled += 1
            for c in communities:
                community_count[c] += 1
        
        # Organizations
        orgs = v9.get("organizations", [])
        if orgs:
            orgs_filled += 1
            for o in orgs:
                org_count[o] += 1
    
    # Calculate overall semantic richness
    overall_richness = (people_filled + schemes_filled + target_groups_filled + communities_filled + orgs_filled) / (total * 5) * 100
    
    # Report
    print(f"\n{'='*80}")
    print("Parser V2.5 - Semantic Richness Measurement")
    print(f"{'='*80}")
    print(f"Total Tweets: {total:,}\n")
    
    print(f"**Semantic Fill Rates:**")
    print(f"  People:        {people_filled:,} ({people_filled/total*100:.1f}%)")
    print(f"  Schemes:       {schemes_filled:,} ({schemes_filled/total*100:.1f}%)")
    print(f"  Target Groups: {target_groups_filled:,} ({target_groups_filled/total*100:.1f}%)")
    print(f"  Communities:   {communities_filled:,} ({communities_filled/total*100:.1f}%)")
    print(f"  Organizations: {orgs_filled:,} ({orgs_filled/total*100:.1f}%)")
    print(f"\n  **Overall Semantic Richness: {overall_richness:.1f}%**\n")
    
    print(f"**Top 10 People:**")
    for person, count in people_count.most_common(10):
        print(f"  - {person}: {count}")
    
    print(f"\n**Top 10 Schemes:**")
    for scheme, count in scheme_count.most_common(10):
        print(f"  - {scheme}: {count}")
    
    print(f"\n**Top Target Groups:**")
    for tg, count in target_group_count.most_common():
        print(f"  - {tg}: {count}")
    
    print(f"\n**Top Communities:**")
    for comm, count in community_count.most_common():
        print(f"  - {comm}: {count}")
    
    print(f"\n**Top Organizations:**")
    for org, count in org_count.most_common():
        print(f"  - {org}: {count}")
    
    print(f"\n{'='*80}")
    print(f"V2.5 Semantic Richness: {overall_richness:.1f}%")
    print(f"Target: 94%+")
    print(f"Status: {'✅ SUCCESS' if overall_richness >= 94 else '⚠️ NEEDS IMPROVEMENT'}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    measure_semantic_richness()
