import json
from collections import defaultdict
from typing import List, Dict

def analyze_parsed_tweets(file_path: str = 'parsed_tweets_output.json'):
    """
    Analyzes the parsed tweets data and prints statistical insights.
    """
    parsed_tweets_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            parsed_tweets_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. Is it valid JSON?")
        return

    total_tweets = len(parsed_tweets_data)
    if total_tweets == 0:
        print("No tweets found in the file to analyze.")
        return

    # --- Initialize counters ---
    total_confidence = 0.0
    event_type_counts = defaultdict(int)
    location_counts = defaultdict(int)
    district_counts = defaultdict(int)
    assembly_counts = defaultdict(int)
    block_counts = defaultdict(int)
    ulb_counts = defaultdict(int)
    specific_location_tweets = 0 # Tweets with district, assembly, block, or ulb filled
    
    people_mentioned_counts = defaultdict(int)
    organizations_counts = defaultdict(int)
    word_buckets_counts = defaultdict(int)
    target_groups_counts = defaultdict(int)
    communities_counts = defaultdict(int)
    schemes_mentioned_counts = defaultdict(int)
    
    review_status_counts = defaultdict(int)

    # --- Aggregate data ---
    for tweet in parsed_tweets_data:
        parsed_data = tweet.get('parsed_data_v2', {})
        
        # Confidence
        confidence = parsed_data.get('confidence', 0.0)
        total_confidence += confidence

        # Event Type
        event_type_counts[parsed_data.get('event_type', 'N/A')] += 1

        # Location
        location = parsed_data.get('location', {})
        if location.get('canonical_key') and location['canonical_key'] != 'CG':
            specific_location_tweets += 1
            if location.get('district'):
                district_counts[location['district']] += 1
            if location.get('assembly'):
                assembly_counts[location['assembly']] += 1
            if location.get('block'):
                block_counts[location['block']] += 1
            if location.get('ulb'):
                ulb_counts[location['ulb']] += 1
        elif location.get('canonical_key') == 'CG':
            location_counts['Chhattisgarh (Default)'] += 1
        else:
            location_counts['No Location Key'] += 1
            
        # People Mentioned (from old_parsed_data for now, as people_canonical is empty)
        for person in tweet.get('old_parsed_data', {}).get('people_mentioned', []):
            people_mentioned_counts[person] += 1

        # Organizations
        for org in parsed_data.get('organizations', []):
            organizations_counts[org] += 1

        # Word Buckets
        for bucket in parsed_data.get('word_buckets', []):
            word_buckets_counts[bucket] += 1
            
        # Target Groups
        for group in parsed_data.get('target_groups', []):
            target_groups_counts[group] += 1
            
        # Communities
        for community in parsed_data.get('communities', []):
            communities_counts[community] += 1
            
        # Schemes Mentioned
        for scheme in parsed_data.get('schemes_mentioned', []):
            schemes_mentioned_counts[scheme] += 1

        # Review Status
        review_status_counts[parsed_data.get('review_status', 'N/A')] += 1

    # --- Print Analysis ---
    print("\n--- Parsing Analysis ---")
    print(f"Total Tweets Parsed: {total_tweets}")
    print(f"Average Confidence Score: {total_confidence / total_tweets:.2f}")

    print("\n--- Event Type Distribution (Top 5) ---")
    for et, count in sorted(event_type_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {et}: {count}")

    print("\n--- Location Analysis ---")
    print(f"Tweets with Specific Locations (District, Assembly, Block, ULB): {specific_location_tweets}")
    print(f"Tweets defaulted to Chhattisgarh: {location_counts.get('Chhattisgarh (Default)', 0)}")
    print(f"Tweets with no canonical key: {location_counts.get('No Location Key', 0)}")

    print("\n--- Top Districts (Top 5) ---")
    for dist, count in sorted(district_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {dist}: {count}")

    print("\n--- Top Assembly Constituencies (Top 5) ---")
    for ac, count in sorted(assembly_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {ac}: {count}")

    print("\n--- Top Blocks (Top 5) ---")
    for block, count in sorted(block_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {block}: {count}")

    print("\n--- Top Urban Local Bodies (ULB) (Top 5) ---")
    for ulb, count in sorted(ulb_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {ulb}: {count}")

    print("\n--- Top People Mentioned (Top 5) ---")
    for person, count in sorted(people_mentioned_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {person}: {count}")

    print("\n--- Top Organizations (Top 5) ---")
    for org, count in sorted(organizations_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {org}: {count}")

    print("\n--- Word Buckets Distribution (Top 5) ---")
    for bucket, count in sorted(word_buckets_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {bucket}: {count}")

    print("\n--- Target Groups Distribution (Top 5) ---")
    for group, count in sorted(target_groups_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {group}: {count}")

    print("\n--- Communities Distribution (Top 5) ---")
    for community, count in sorted(communities_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {community}: {count}")

    print("\n--- Schemes Mentioned Distribution (Top 5) ---")
    for scheme, count in sorted(schemes_mentioned_counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"- {scheme}: {count}")

    print("\n--- Review Status Distribution ---")
    for status, count in review_status_counts.items():
        print(f"- {status}: {count}")

if __name__ == '__main__':
    analyze_parsed_tweets()
