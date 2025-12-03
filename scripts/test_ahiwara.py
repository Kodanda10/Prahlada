import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.cognitive.geo_resolver import HybridLocationResolver

def test_ahiwara():
    print("🌍 Testing Ahiwara Resolution...")
    resolver = HybridLocationResolver(enable_semantic=False)
    
    # Text with both Ahiwara (explicit) and Vidhan Sabha (landmark -> Nava Raipur)
    text = "अहिवारा विधानसभा क्षेत्र के ग्रामों में जनसंपर्क किया।" 
    # "Campaigning in villages of Ahiwara assembly constituency."
    # Note: "Vidhan Sabha" usually triggers Nava Raipur if standalone, but here it's "Ahiwara Vidhan Sabha".
    
    print(f"\nInput Text: {text}")
    
    resolved, conf, source = resolver.resolve(text)
    
    if resolved:
        print(f"✅ Resolved: {resolved['canonical']}")
        print(f"   Source: {source}")
        print(f"   Details: {resolved}")
    else:
        print("❌ Failed to resolve.")

if __name__ == "__main__":
    test_ahiwara()
