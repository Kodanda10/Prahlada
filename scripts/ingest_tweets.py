import json
import os
import sys
import time

INPUT_FILE = os.path.join(os.path.dirname(__file__), '../data/parsed_tweets_v8.jsonl')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '../data/ingested_tweets.json')

def ingest():
    print(f"🚀 Starting ingestion from {INPUT_FILE}")
    start_time = time.time()
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        sys.exit(1)

    ingested_tweets = []
    count = 0
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    raw_tweet = json.loads(line)
                    # Add HITL fields
                    raw_tweet['approved_by_human'] = False
                    raw_tweet['corrected_fields'] = {}
                    raw_tweet['feedback_log'] = []
                    
                    ingested_tweets.append(raw_tweet)
                    count += 1
                    
                    if count % 500 == 0:
                        print(f"Processed {count} tweets...", end='\r', flush=True)
                        
                except json.JSONDecodeError:
                    continue
                    
        print(f"\n✅ Processed {count} tweets. Writing to {OUTPUT_FILE}...")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(ingested_tweets, f, indent=2, ensure_ascii=False)
            
        print(f"🎉 Success! Wrote {len(ingested_tweets)} tweets.")
        print(f"⏱️ Time taken: {time.time() - start_time:.2f}s")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ingest()
