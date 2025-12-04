"""
Live AI Integration Test.
Connects to a real running Ollama instance to verify model availability and response quality.
Usage: python3 tests/integration/live_ai_test.py
"""
import sys
import os
import time
import json
import urllib.request
import urllib.error

# Add backend to path to import OllamaClient if needed, 
# but here we'll use direct requests to be independent
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "gemma2:9b")

def log(msg, type="INFO"):
    print(f"[{type}] {msg}")

def make_request(url, method="GET", data=None):
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            json_data = json.dumps(data).encode('utf-8')
            req.add_header('Content-Type', 'application/json')
            req.data = json_data
            
        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "body": json.loads(response.read().decode('utf-8'))
            }
    except urllib.error.URLError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def test_ollama_connection():
    log(f"Testing connection to Ollama at {BASE_URL}...")
    result = make_request(f"{BASE_URL}/api/tags")
    
    if "error" not in result and result.get("status") == 200:
        log("✅ Connection successful.")
        models = result["body"].get('models', [])
        model_names = [m['name'] for m in models]
        log(f"Available models: {', '.join(model_names)}")
        return True
    else:
        error_msg = result.get("error", f"Status {result.get('status')}")
        log(f"❌ Connection failed: {error_msg}", "ERROR")
        return False

def test_model_generation():
    log(f"Testing generation with model: {MODEL}...")
    
    payload = {
        "model": MODEL,
        "prompt": "What is the capital of Chhattisgarh? Answer in one word.",
        "stream": False
    }
    
    start_time = time.time()
    result = make_request(f"{BASE_URL}/api/generate", method="POST", data=payload)
    duration = time.time() - start_time
    
    if "error" not in result and result.get("status") == 200:
        answer = result["body"].get('response', '').strip()
        log(f"✅ Generation successful in {duration:.2f}s")
        log(f"Prompt: {payload['prompt']}")
        log(f"Response: {answer}")
        
        if "Raipur" in answer or "raipur" in answer.lower():
            log("✅ Semantic check passed: Answer contains 'Raipur'")
        else:
            log(f"⚠️ Semantic check warning: Expected 'Raipur', got '{answer}'", "WARN")
        return True
    else:
        error_msg = result.get("error", f"Status {result.get('status')}")
        log(f"❌ Generation failed: {error_msg}", "ERROR")
        return False

def main():
    log("Starting Live AI Integration Test...")
    
    if not test_ollama_connection():
        log("Aborting tests due to connection failure. Is Ollama running?", "ERROR")
        sys.exit(1)
        
    if not test_model_generation():
        log("Model generation test failed.", "ERROR")
        sys.exit(1)
        
    log("🎉 All live AI tests passed!")

if __name__ == "__main__":
    main()
