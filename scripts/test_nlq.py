import requests
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import os
print(f"DEBUG: FAISS_INDEX_PATH = {os.getenv('FAISS_INDEX_PATH')}")

def test_nlq():
    print("🧪 Testing NLQ Engine...")
    
    # 1. Define Questions
    questions = [
        "छत्तीसगढ़ में कौन सी नई योजनाएं शुरू हुई हैं?",
        "रायपुर में क्या कार्यक्रम हुआ?",
        "किसानों के लिए क्या घोषणाएं हैं?"
    ]
    
    # 2. Call API (assuming server is running, but we can also import engine directly for unit test)
    # For this script, let's import engine directly to avoid needing running server
    try:
        from backend.cognitive.nlq_engine import get_nlq_engine
        engine = get_nlq_engine()
        
        for q in questions:
            print(f"\n❓ Question: {q}")
            result = engine.answer_query(q)
            print(f"💡 Answer: {result['answer']}")
            print(f"📚 Sources: {len(result['sources'])} tweets used.")
            
    except ImportError:
        print("⚠️ Could not import backend modules. Make sure you are in the project root.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_nlq()
