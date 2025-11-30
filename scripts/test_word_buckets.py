import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.cognitive.word_bucket_extractor import get_word_bucket_extractor

def test_extractor():
    print("🚀 Initializing WordBucketExtractor...")
    extractor = get_word_bucket_extractor()
    
    if extractor.use_faiss:
        print("✅ ML Components (SentenceTransformer + FAISS) Loaded Successfully")
    else:
        print("⚠️ ML Components NOT Loaded (Fallback Mode)")
        
    text = "नवा रायपुर में जीएसटी कार्यालय का उद्घाटन किया गया। यह एक महत्वपूर्ण योजना है।"
    tweet_id = "test_123"
    metadata = {
        "event_type": "उद्घाटन",
        "location": "नवा रायपुर"
    }
    
    print(f"\nProcessing Text: {text}")
    buckets = extractor.process_tweet(tweet_id, text, metadata)
    
    print("\nExtracted Buckets:")
    for b in buckets:
        print(f" - {b['word']} (Norm: {b['normalized']}) [Type: {b['type']}] [Cluster: {b['cluster_id']}]")

if __name__ == "__main__":
    test_extractor()
