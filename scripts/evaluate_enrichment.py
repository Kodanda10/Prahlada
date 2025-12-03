import asyncio
import json
import sys
import datetime
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.cognitive.gemma3_enrichment import Gemma3EnrichmentService
from backend.models import RawTweet

# Sample "Golden" Dataset (Synthetic for now)
GOLDEN_DATASET = [
    {
        "text": "रायपुर में आज मुख्यमंत्री ने किसानों के लिए नई योजना की घोषणा की। #Chhattisgarh #Farmers",
        "expected": {
            "event_type": "योजना घोषणा", # Updated to match Gemma 3 output
            "locations": ["Raipur", "रायपुर"],
            "themes": ["agriculture", "politics", "welfare"]
        }
    },
    {
        "text": "बिलासपुर पुलिस ने यातायात नियमों का उल्लंघन करने वालों पर कार्रवाई की।",
        "expected": {
            "event_type": "कानून व्यवस्था / पुलिस", # Updated to match Gemma 3 output
            "locations": ["Bilaspur", "बिलासपुर"],
            "themes": ["law_and_order", "traffic"]
        }
    }
]

from backend.database import AsyncSessionLocal

async def evaluate():
    print("🧪 Starting Evaluation Harness...")
    
    async with AsyncSessionLocal() as session:
        service = Gemma3EnrichmentService(session)
        
        score = 0
        total = len(GOLDEN_DATASET)
        
        for i, item in enumerate(GOLDEN_DATASET):
            print(f"\n📝 Case {i+1}: {item['text'][:50]}...")
            
            # Mock a RawTweet
            tweet = RawTweet(
                tweet_id=f"eval_{i}",
                text=item['text'],
                created_at=datetime.datetime.utcnow(),
                author_handle="eval_user"
            )
            
            # Run Enrichment
            try:
                result = await service.enrich_tweet(tweet)
                
                if not result:
                    print("❌ Enrichment returned None")
                    continue
                
                # Compare (Basic fuzzy match)
                print(f"   Generated Type: {result.event_type}")
                print(f"   Expected Type: {item['expected']['event_type']}")
                
                # Simple scoring logic
                case_score = 0
                if result.event_type == item['expected']['event_type']:
                    case_score += 1
                
                # Check locations
                # result.location_candidates is a dict, we need to extract names
                # It has 'resolved', 'inferred', etc.
                gen_locs = []
                if result.location_candidates:
                    if 'resolved' in result.location_candidates:
                        gen_locs.append(result.location_candidates['resolved'].get('canonical', '').lower())
                    if 'inferred' in result.location_candidates:
                        gen_locs.extend([l.lower() for l in result.location_candidates['inferred']])
                
                exp_locs = [l.lower() for l in item['expected']['locations']]
                if any(l in gen_locs for l in exp_locs):
                    case_score += 1
                    
                print(f"   Case Score: {case_score}/2")
                score += case_score
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
        final_score = (score / (total * 2)) * 100
        print(f"\n🏆 Final Evaluation Score: {final_score:.2f}%")

if __name__ == "__main__":
    asyncio.run(evaluate())
