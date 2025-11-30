import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_imports")

def test_import(module_name):
    print(f"Testing import: {module_name}...", end="", flush=True)
    start = time.time()
    try:
        __import__(module_name)
        elapsed = time.time() - start
        print(f" ✅ OK ({elapsed:.3f}s)")
    except Exception as e:
        print(f" ❌ FAILED: {e}")

print("Starting import diagnostics...")

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Database
test_import("backend.database")

# 2. Models
test_import("backend.models")

# 3. Knowledge Store
test_import("backend.knowledge_store")

# 4. Phi Adapter
test_import("backend.cognitive.phi_adapter")

# 5. Gemini Parser V2 (Heavy)
test_import("scripts.gemini_parser_v2")

print("Diagnostics complete.")
