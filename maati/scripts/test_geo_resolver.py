import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.cognitive.geo_resolver import HybridLocationResolver

def test_resolver():
    print("🌍 Testing HybridLocationResolver...")
    resolver = HybridLocationResolver(enable_semantic=False)
    
    text = "आज ग्राम कुकुर्दा में जनसंपर्क किया।"
    print(f"\nInput Text: {text}")
    
    resolved, conf, source = resolver.resolve(text)
    
    if resolved:
        print(f"✅ Resolved: {resolved['canonical']}")
        print(f"   Hierarchy: {resolved['hierarchy_path']}")
        print(f"   Source: {source}")
        print(f"   Details: {resolved}")
    else:
        print("❌ Failed to resolve.")

if __name__ == "__main__":
    test_resolver()
