"""
Direct test of Fast NLQ - No Auth Needed
Tests the service layer directly
"""

import asyncio
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


async def main():
    print("="*80)
    print("🚀 TESTING FAST NLQ - DIRECT SERVICE TEST")
    print("="*80)
    print()
    
    from backend.services.fast_nlq_service import get_fast_nlq_service
    
    service = get_fast_nlq_service()
    
    # Test cases with timing
    tests = [
        ("भूमि सुधार योजना के बारे में बताओ", "Event Object"),
        ("नवा रायपुर CFC की घोषणा कब हुई?", "Event Object"),
        ("Vision 2047 के milestones क्या हैं?", "Event Object + Timeline"),
        ("भूमि सुधार योजना के बारे में बताओ", "Cache Hit (Repeat)")
    ]
    
    results = []
    
    for i, (query, description) in enumerate(tests, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {description}")
        print(f"{'='*80}")
        print(f"❓ {query}")
        print()
        
        start = time.time()
        response = await service.answer_query(query, use_llm_polish=False)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"⚡ Mode: {response.response_mode}")
        print(f"⏱️  Time: {elapsed_ms:.1f}ms")
        print(f"📊 Quality: {response.quality_score}/4")
        print(f"🎯 Confidence: {response.confidence}")
        print()
        print("💡 ANSWER:")
        print("-" * 80)
        # Show first 500 chars
        answer_preview = response.answer[:500] + "..." if len(response.answer) > 500 else response.answer
        print(answer_preview)
        print("-" * 80)
        
        results.append({
            "test": description,
            "mode": response.response_mode,
            "time_ms": elapsed_ms,
            "quality": response.quality_score
        })
    
    # Summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    print()
    
    for r in results:
        print(f"{r['test']:<35} | {r['mode']:<15} | {r['time_ms']:>8.1f}ms | Q: {r['quality']}/4")
    
    print()
    avg_time = sum(r['time_ms'] for r in results) / len(results)
    print(f"⏱️  Average Response Time: {avg_time:.1f}ms")
    
    # Calculate speedup
    old_avg = 63150  # ms from stress test
    speedup = old_avg / avg_time if avg_time > 0 else float('inf')
    print(f"🚀 Speedup vs Old System: {speedup:.0f}x FASTER!")
    print()
    print("="*80)
    print("✅ ALL TESTS COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
