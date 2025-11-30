import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.gemini_parser_v2 import HybridLocationResolver

def debug_resolver():
    print("🚀 Initializing HybridLocationResolver...")
    resolver = HybridLocationResolver(enable_semantic=True)
    
    test_cases = ["रायपुर", "नवा रायपुर", "Raipur", "Nava Raipur"]
    
    for loc in test_cases:
        print(f"\n🔍 Testing: '{loc}'")
        
        # Test 1: Direct Hierarchy Resolution
        res = resolver.geo_resolver.resolve_hierarchy(loc)
        print(f"   👉 resolve_hierarchy('{loc}') -> {res}")
        
        # Test 2: Full Resolve
        full_res, conf, source = resolver.resolve(f"{loc} में कार्यक्रम", [])
        print(f"   👉 resolve('{loc}') -> {full_res} (Source: {source})")

if __name__ == "__main__":
    debug_resolver()
