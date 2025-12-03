import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import os
print(f"DEBUG: FAISS_INDEX_PATH = {os.getenv('FAISS_INDEX_PATH')}")

def test_nlq_5w1h():
    print("🧪 Testing Event-Grade 5W1H NLQ Engine...\n")
    
    # Define comprehensive test questions
    questions = [
        "भूमि सुधार योजना के बारे में पूरी जानकारी दो - कब, कहाँ, किसने लॉन्च किया, कितनी राशि की घोषणा हुई?",
        "नवा रायपुर कॉमन फैसिलिटी सेंटर का उद्घाटन किसने किया? कब और कहाँ?",
        "छत्तीसगढ़ में कौन सी नई योजनाएं शुरू हुई हैं? हर योजना के लॉन्च की तारीख, स्थान, और घोषित राशि बताओ।",
        "सड़क निर्माण योजना की पूरी timeline क्या है? कब घोषणा हुई, कितना बजट, और कौन-कौन मंच पर मौजूद थे?"
    ]
    
    try:
        from backend.cognitive.nlq_engine import get_nlq_engine
        engine = get_nlq_engine()
        
        for i, q in enumerate(questions, 1):
            print(f"\n{'='*80}")
            print(f"❓ TEST {i}: {q}")
            print(f"{'='*80}\n")
            
            result = engine.answer_query(q)
            
            print(f"💡 ANSWER:\n{result['answer']}\n")
            print(f"📊 METADATA:")
            print(f"   • Event Objects Used: {result.get('event_objects_count', 0)}")
            print(f"   • Sources: {len(result['sources'])} tweets")
            print(f"\n{'='*80}\n")
            
    except ImportError:
        print("⚠️ Could not import backend modules. Make sure you are in the project root.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nlq_5w1h()
