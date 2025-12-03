import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

def test_single_query():
    print("🧪 Testing Single NLQ Query...\n")
    
    # Simple, focused test question
    question = "नवा रायपुर में क्या कार्यक्रम हुआ?"
    
    try:
        from backend.cognitive.nlq_engine import get_nlq_engine
        engine = get_nlq_engine()
        
        print(f"❓ QUESTION: {question}\n")
        print("⏳ Generating answer...\n")
        
        result = engine.answer_query(question)
        
        print("="*80)
        print("💡 ANSWER:")
        print("="*80)
        print(result['answer'])
        print("\n" + "="*80)
        print(f"\n📊 Used {result.get('event_objects_count', 0)} event objects from {len(result['sources'])} tweets")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_query()
