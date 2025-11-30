import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.gemini_parser_v2 import GeminiParserV2
from backend.cognitive.phi_adapter import set_phi_adapter_config

async def verify_feedback_loop():
    print("🔄 Verifying Feedback Loop...")
    
    # 1. Enable Phi Adapter
    set_phi_adapter_config(enabled=True)
    
    # 2. Initialize Parser
    parser = GeminiParserV2(enable_semantic=True)
    parser.enable_cognitive = True
    
    # 3. Mock Vector Store Search to return a known example
    mock_example = {
        "metadata": {
            "text": "Previous tweet about textile park in Raipur",
            "event_type": "Industrial Launch",
            "themes": "Economic Development"
        },
        "distance": 0.2
    }
    
    # We need to patch the vector_store instance on the parser
    if parser.vector_store:
        parser.vector_store.search = MagicMock(return_value=[mock_example])
        print("✅ Mocked Vector Store search")
    else:
        print("❌ Vector Store not initialized on parser!")
        return

    # 4. Mock Phi Adapter to capture the prompt
    original_get_suggestions = parser.phi_adapter.get_suggestions
    
    def captured_get_suggestions(tweet_id, raw_tweet, current_parsed, context_examples=None):
        print(f"\n📥 Captured Context Examples passed to Phi:")
        if context_examples:
            for i, ex in enumerate(context_examples):
                print(f"   Example {i+1}: {ex}")
        else:
            print("   None")
            
        # Call original to generate the prompt string (we want to see the prompt)
        # But we don't actually need to call the LLM for this test if we just want to verify injection
        # However, let's call the internal _build_correction_prompt to see the final text
        prompt = parser.phi_adapter._build_correction_prompt(raw_tweet, current_parsed, context_examples)
        print(f"\n📝 Generated Prompt Snippet:\n{'-'*40}")
        print(prompt[:500] + "...\n[truncated]\n" + prompt[-200:])
        print(f"{'-'*40}")
        
        # Return a dummy suggestion to allow parser to continue
        from backend.cognitive.phi_adapter import PhiSuggestions
        return PhiSuggestions(confidence_score=0.9, reasoning="Feedback loop test")

    parser.phi_adapter.get_suggestions = captured_get_suggestions

    # 5. Process a test tweet
    test_tweet = {
        "tweet_id": "test_123",
        "text": "New textile park opening in Nava Raipur today."
    }
    
    print(f"\n🚀 Processing Tweet: {test_tweet['text']}")
    parser.parse_tweet(test_tweet)

if __name__ == "__main__":
    asyncio.run(verify_feedback_loop())
