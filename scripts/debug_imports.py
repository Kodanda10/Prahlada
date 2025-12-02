import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print(f"Python executable: {sys.executable}")
print(f"System path: {sys.path}")

try:
    from backend.cognitive.enrichment_engine import PhiEnrichmentEngine
    import backend.cognitive.enrichment_engine as module
    
    print(f"\nModule file: {module.__file__}")
    
    engine = PhiEnrichmentEngine()
    print(f"Has _build_reasoning_prompt? {hasattr(engine, '_build_reasoning_prompt')}")
    
    if hasattr(engine, '_build_reasoning_prompt'):
        print("✅ Method exists!")
    else:
        print("❌ Method MISSING!")
        print(f"Dir: {dir(engine)}")

except Exception as e:
    print(f"Error: {e}")
