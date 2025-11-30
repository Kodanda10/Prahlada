
import sys
from pathlib import Path
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "api"))

from api.src.parsing.semantic_location_linker import MultilingualFAISSLocationLinker

def debug():
    print("Initializing Linker...")
    linker = MultilingualFAISSLocationLinker()
    linker.load_multilingual_data()
    
    print(f"Loaded {len(linker.locations)} locations.")
    
    queries = [
        "Ward 5, Raipur",
        "Ward Number 5",
        "Raipur",
        "Mahamaya Ward", # From the excel file inspection
        "महामाया वार्ड"
    ]
    
    print("\n--- Debugging Search ---")
    for q in queries:
        print(f"\nQuery: '{q}'")
        # Search with very low threshold and high limit
        matches = linker.find_semantic_matches(q, limit=5, min_score=0.1)
        for m in matches:
            print(f"  - {m['name']} (Score: {m['similarity_score']:.4f})")

if __name__ == "__main__":
    debug()
