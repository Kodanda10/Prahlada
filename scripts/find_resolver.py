import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    import backend.cognitive.location_resolver as lr
    print(f"✅ Found module: {lr}")
    print(f"📂 File path: {lr.__file__}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    # Try to find where it might be
    import backend
    print(f"Backend path: {backend.__path__}")
