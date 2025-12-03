import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.cognitive.ollama_client import OllamaClient

async def test_model(model_name):
    client = OllamaClient(model=model_name)
    print(f"\n{'='*20} Testing Model: {model_name} {'='*20}")
    
    # Test Tweet
    text = "मुख्यमंत्री ने रायपुर में नए अस्पताल का उद्घाटन किया। यह स्वास्थ्य सेवाओं को बेहतर बनाएगा।"
    event_type = "उद्घाटन"
    locations = "['रायपुर']"
    
    prompt = f"""You are a precise data extraction AI. Output ONLY valid JSON.

TWEET: "{text}"
CONTEXT: Event={event_type}, Loc={locations}

INSTRUCTIONS:
1. Identify 1-3 semantic themes (e.g., Health, Infrastructure).
2. Verify location and event.

OUTPUT JSON:
{{
  "contextual_summary": "Brief summary",
  "semantic_word_buckets": ["Theme1", "Theme2"],
  "location_analysis": {{ "is_correct": true, "corrected_name": null, "confidence": 1.0 }},
  "event_classification": {{ "is_accurate": true, "suggested_category": null, "confidence": 1.0 }}
}}"""

    try:
        start = time.time()
        response = await client.generate(prompt, json_mode=True)
        duration = time.time() - start
        
        if isinstance(response, dict) and 'response' in response:
            print(f"⏱️ Time: {duration:.2f}s")
            try:
                data = json.loads(response['response'])
                print("✅ Valid JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return True
            except:
                print(f"❌ Invalid JSON: {response['response'][:200]}...")
                return False
        else:
            print(f"❌ Error: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def main():
    print("🚀 Starting Model Comparison...")
    phi_result = await test_model("phi3.5")
    gemma_result = await test_model("gemma2:2b")
    
    print(f"\n🏆 Summary:")
    print(f"Phi 3.5: {'✅ PASS' if phi_result else '❌ FAIL'}")
    print(f"Gemma 2: {'✅ PASS' if gemma_result else '❌ FAIL'}")

if __name__ == "__main__":
    asyncio.run(main())
