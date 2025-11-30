
import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.gemini_parser_v2 import HybridLocationResolver

def verify():
    print("Initializing HybridLocationResolver...")
    resolver = HybridLocationResolver(enable_semantic=True)
    
    test_queries = [
        "Ward 5, Raipur",
        "Ward Number 10, Bilaspur",
        "वार्ड क्रमांक 4, कोण्डागांव",
        "Ward 1, Ambikapur",
        "Police Line, Raigarh" # Test static landmark too
    ]
    
    print("\n--- Starting Verification ---")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result, confidence, source = resolver.resolve(query)
        
        if result:
            print(f"✅ Resolved: {result['canonical']}")
            print(f"   Type: {result.get('location_type')}")
            print(f"   Hierarchy: {result.get('hierarchy_path')}")
            print(f"   Source: {source}")
            print(f"   Confidence: {confidence}")
            
            # Specific checks
            if "Ward" in query or "वार्ड" in query:
                if result.get('ward'):
                    print(f"   Ward Extracted: {result['ward']}")
                else:
                    print("   ⚠️ Ward NOT extracted in structured field")
        else:
            print("❌ Failed to resolve")

if __name__ == "__main__":
    verify()
