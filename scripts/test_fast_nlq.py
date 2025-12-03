"""
Test Fast NLQ - 3-Tier System
Demonstrates cache → event object → LLM fallback
"""

import asyncio
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


async def test_fast_nlq():
    print("="*80)
    print("🚀 Testing Fast NLQ - 3-Tier System")
    print("="*80)
    print()
    
    from backend.services.fast_nlq_service import get_fast_nlq_service
    
    service = get_fast_nlq_service()
    
    # Test queries
    test_cases = [
        {
            "query": "भूमि सुधार योजना के बारे में बताओ",
            "expected_mode": "event_object",
            "description": "Direct event object match"
        },
        {
            "query": "नवा रायपुर Common Facility Centre की घोषणा कब हुई?",
            "expected_mode": "event_object",
            "description": "Event object with date query"
        },
        {
            "query": "छत्तीसगढ़ अंजोर Vision 2047 के milestones क्या हैं?",
            "expected_mode": "event_object",
            "description": "Timeline query from event object"
        },
        {
            "query": "भूमि सुधार योजना के बारे में बताओ",  # Same as first
            "expected_mode": "cache",
            "description": "Cache hit (repeat query)"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/4: {test['description']}")
        print(f"{'='*80}")
        print(f"❓ Query: {test['query']}")
        print()
        
        start = time.time()
        response = await service.answer_query(test['query'], use_llm_polish=False)
        elapsed_ms = (time.time() - start) * 1000
        
        # Display results
        print(f"⚡ Mode: {response.response_mode}")
        print(f"⏱️  Time: {elapsed_ms:.0f}ms")
        print(f"📊 Quality Score: {response.quality_score}/4")
        print(f"🎯 Confidence: {response.confidence}")
        print()
        print(f"💡 ANSWER:")
        print("-" * 80)
        print(response.answer[:500] + "..." if len(response.answer) > 500 else response.answer)
        print("-" * 80)
        
        # Verify expected mode
        if response.response_mode == test['expected_mode']:
            print(f"✅ Expected mode: {test['expected_mode']}")
        else:
            print(f"⚠️  Expected {test['expected_mode']}, got {response.response_mode}")
        
        results.append({
            "test": test['description'],
            "mode": response.response_mode,
            "time_ms": elapsed_ms,
            "quality": response.quality_score
        })
    
    # Summary
    print("\n" + "="*80)
    print("📊 PERFORMANCE SUMMARY")
    print("="*80)
    print()
    
    for r in results:
        print(f"{r['test']:<40} | Mode: {r['mode']:<15} | Time: {r['time_ms']:>6.0f}ms | Quality: {r['quality']}/4")
    
    print()
    avg_time = sum(r['time_ms'] for r in results) / len(results)
    print(f"⏱️  Average Response Time: {avg_time:.0f}ms")
    
    cache_hits = [r for r in results if r['mode'] == 'cache']
    event_hits = [r for r in results if r['mode'] == 'event_object']
    
    print(f"⚡ Cache Hits: {len(cache_hits)}")
    print(f"🎯 Event Object Hits: {len(event_hits)}")
    
    if cache_hits:
        print(f"   Avg Cache Time: {sum(r['time_ms'] for r in cache_hits) / len(cache_hits):.0f}ms")
    if event_hits:
        print(f"   Avg Event Time: {sum(r['time_ms'] for r in event_hits) / len(event_hits):.0f}ms")
    
    print("\n" + "="*80)
    print("✅ Test Complete!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_fast_nlq())
