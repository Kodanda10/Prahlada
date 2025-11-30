import urllib.request
import json
import time

def test_ollama():
    url = "http://localhost:11434/api/tags"
    print(f"Testing connection to {url}...")
    
    start = time.time()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"✅ Success! Response time: {time.time() - start:.2f}s")
            print(f"Models: {[m['name'] for m in data.get('models', [])]}")
            return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_generate():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3.5",
        "prompt": "Say hello",
        "stream": False
    }
    print(f"\nTesting generation with {payload['model']}...")
    
    start = time.time()
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Success! Response time: {time.time() - start:.2f}s")
            print(f"Response: {result.get('response')}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    if test_ollama():
        test_generate()
