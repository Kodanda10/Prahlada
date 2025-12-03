import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Add api path
sys.path.append(str(PROJECT_ROOT / 'api'))

from api.src.parsing.semantic_location_linker import MultilingualFAISSLocationLinker

def test_semantic():
    print("🧠 Testing Semantic Linker...")
    linker = MultilingualFAISSLocationLinker()
    linker.load_multilingual_data()
    
    queries = [
        "कुकुर्दा",
        "ग्राम कुकुर्दा",
        "Kukurda",
        "Gram Kukurda"
    ]
    
    for q in queries:
        print(f"\n🔍 Query: '{q}'")
        matches = linker.find_semantic_matches(q, limit=3, min_score=0.6)
        for m in matches:
            print(f"   ✅ Match: {m['name']} (Score: {m['similarity_score']:.4f})")
            
if __name__ == "__main__":
    test_semantic()
