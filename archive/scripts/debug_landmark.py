import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append("/Users/abhijita/Documents/Project-Prahlada")
from scripts.gemini_parser_v2 import GeminiParserV2

parser = GeminiParserV2()
tweet = {
    "tweet_id": "1890582740170391875",
    "author_handle": "test",
    "text": "अंबिकापुर में आयोजित कार्यक्रम...", # Placeholder text, need actual text
    "created_at": "2025-11-10T08:15:11.402Z"
}
# I need the actual text. I'll read it from the CSV or just use a simple string that SHOULD work.
tweet = {
    "tweet_id": "1890582740170391875",
    "author_handle": "test",
    "text": "आज अंबिकापुर में...", 
    "created_at": "2025-11-10T08:15:11.402Z"
}

result = parser.parse_tweet(tweet)
print(json.dumps(result, indent=2, ensure_ascii=False))
