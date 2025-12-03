import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Test Questions - Ultra-Stress NLQ Test Suite
STRESS_TEST_QUESTIONS = [
    # SCHEMES / PROJECTS
    {
        "id": 1,
        "category": "SCHEMES",
        "question": "भूमि सुधार योजना का लॉन्च कब हुआ था? कहाँ हुआ था और मंच पर कौन-कौन नेता मौजूद थे?"
    },
    {
        "id": 2,
        "category": "SCHEMES",
        "question": "छत्तीसगढ़ अंजोर Vision 2047 में सरकार ने अब तक कौन-कौनसे milestones घोषित किए हैं — fund, timelines और beneficiaries सहित बताओ।"
    },
    {
        "id": 3,
        "category": "SCHEMES",
        "question": "नवा रायपुर में बनने वाले Common Facility Centre की घोषणा किस दिन हुई थी और इसमें कितनी राशि और कौन-कौन facilities शामिल हैं?"
    },
    {
        "id": 4,
        "category": "SCHEMES",
        "question": "CM ने सड़क निर्माण योजना के तहत केंद्र सरकार से कितनी स्वीकृति मिलने की बात कही थी और किस जिले में इसका पहला phase शुरू हुआ?"
    },
    {
        "id": 5,
        "category": "SCHEMES",
        "question": "छत्तीसगढ़ सरकार ने हाल ही में किस योजना को India Model बताया है और इसके पीछे क्या reasoning दी है?"
    },
    
    # OP CHOUDHARY FOCUSED
    {
        "id": 6,
        "category": "OP_CHOUDHARY",
        "question": "ओपी चौधरी जी ने नवा रायपुर से जुड़ी आखिरी बड़ी घोषणा कब की थी और उसमें क्या-क्या commitments दिए थे?"
    },
    {
        "id": 7,
        "category": "OP_CHOUDHARY",
        "question": "OP Choudhary की तरफ से कितनी बार 'जनजातीय संग्रहालय' का जिक्र हुआ है और किस event में इसे प्रेरणा-स्थल कहा गया?"
    },
    {
        "id": 8,
        "category": "OP_CHOUDHARY",
        "question": "OP Choudhary ने किस कार्यक्रम में यह कहा था कि 'भूमि सुधार योजना पूरे भारत का मॉडल बनेगी' — date, venue, tweets बताओ।"
    },
    {
        "id": 9,
        "category": "OP_CHOUDHARY",
        "question": "नवा रायपुर की किन-किन परियोजनाओं में OP Choudhary और CM दोनों एक साथ मंच पर मौजूद रहे? Timeline बना कर दो।"
    },
    {
        "id": 10,
        "category": "OP_CHOUDHARY",
        "question": "OP Choudhary द्वारा की गई सबसे बड़ी रोजगार / भर्ती से जुड़ी घोषणा कौनसी है — कब, कहाँ और कितनी भर्तियाँ?"
    },
    
    # NAVA RAIPUR FOCUSED
    {
        "id": 11,
        "category": "NAVA_RAIPUR",
        "question": "What's the complete launch context of the Nava Raipur tech infrastructure upgrades announced recently?"
    },
    {
        "id": 12,
        "category": "NAVA_RAIPUR",
        "question": "नवा रायपुर में होने वाले smart mobility projects की घोषणा कब और किस कार्यक्रम में की गई थी?"
    },
    {
        "id": 13,
        "category": "NAVA_RAIPUR",
        "question": "Nava Raipur CFC में किन जिलों के स्टार्टअप्स को प्राथमिकता देने की बात की गई थी और यह किस ट्वीट में mention है?"
    },
    
    # CM + PM MODI REFERENCES
    {
        "id": 14,
        "category": "CM_PM_MODI",
        "question": "CM Vishnu Deo Sai ने किस योजना को 'game changer' कहा था और PM Modi का इसमें क्या संदर्भ दिया गया था?"
    },
    {
        "id": 15,
        "category": "CM_PM_MODI",
        "question": "PM Modi ने छत्तीसगढ़ से जुड़ी किस परियोजना की प्रशंसा की थी और किस नेता ने उस प्रशंसा को ट्वीट में quote किया?"
    },
    {
        "id": 16,
        "category": "CM_PM_MODI",
        "question": "'केंद्र और राज्य मिलकर नई सड़क क्रांति ला रहे हैं' — यह बयान किस event में दिया गया था? कब और कहाँ?"
    },
    
    # MIXED GOVERNANCE + TIMELINE
    {
        "id": 17,
        "category": "TIMELINE",
        "question": "पिछले 6 महीनों में Chhattisgarh में कौन-कौनसी बड़ी योजनाएँ लॉन्च हुई हैं — उनकी dates और key announcements सहित पूरी सूची दो।"
    },
    {
        "id": 18,
        "category": "TIMELINE",
        "question": "Give a timeline of all Nava Raipur related announcements made by the state govt in 2025 — month-by-month."
    },
    {
        "id": 19,
        "category": "TIMELINE",
        "question": "जनजातीय संग्रहालय से जुड़े सभी announcements (tweets + events) की पूरी chronology तैयार करो।"
    },
    {
        "id": 20,
        "category": "BUDGET",
        "question": "State budget announcements में Nava Raipur से जुड़ी कितनी राशि approve हुई और कौन-कौनसे projects इससे funded हुए?"
    }
]

def run_stress_test():
    print("="*100)
    print("🔥 NLQ ENGINE STRESS TEST - 20 ULTRA-HARD QUESTIONS")
    print("="*100)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize telemetry
    telemetry = {
        "start_time": datetime.now().isoformat(),
        "total_questions": len(STRESS_TEST_QUESTIONS),
        "results": [],
        "summary": {
            "total_time": 0,
            "successful": 0,
            "failed": 0,
            "avg_response_time": 0,
            "fastest_query": None,
            "slowest_query": None,
            "category_stats": {}
        }
    }
    
    try:
        from backend.cognitive.nlq_engine import get_nlq_engine
        engine = get_nlq_engine()
        print("✅ NLQ Engine initialized\n")
        
        for test_case in STRESS_TEST_QUESTIONS:
            q_id = test_case["id"]
            category = test_case["category"]
            question = test_case["question"]
            
            print(f"\n{'='*100}")
            print(f"📋 TEST {q_id}/20 [{category}]")
            print(f"{'='*100}")
            print(f"❓ QUESTION: {question}\n")
            
            # Start timer
            start_time = time.time()
            
            try:
                result = engine.answer_query(question)
                end_time = time.time()
                response_time = end_time - start_time
                
                # Record successful result
                test_result = {
                    "id": q_id,
                    "category": category,
                    "question": question,
                    "status": "SUCCESS",
                    "response_time_seconds": round(response_time, 2),
                    "answer_length": len(result['answer']),
                    "sources_used": len(result['sources']),
                    "event_objects_count": result.get('event_objects_count', 0),
                    "answer_preview": result['answer'][:200] + "..." if len(result['answer']) > 200 else result['answer']
                }
                
                telemetry["results"].append(test_result)
                telemetry["summary"]["successful"] += 1
                
                print(f"✅ SUCCESS ({response_time:.2f}s)")
                print(f"📊 Sources: {len(result['sources'])} tweets | Event Objects: {result.get('event_objects_count', 0)}")
                print(f"\n💡 ANSWER PREVIEW:\n{result['answer'][:500]}...\n")
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Record failed result
                test_result = {
                    "id": q_id,
                    "category": category,
                    "question": question,
                    "status": "FAILED",
                    "response_time_seconds": round(response_time, 2),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                telemetry["results"].append(test_result)
                telemetry["summary"]["failed"] += 1
                
                print(f"❌ FAILED ({response_time:.2f}s)")
                print(f"Error: {str(e)}\n")
        
        # Calculate summary statistics
        telemetry["end_time"] = datetime.now().isoformat()
        
        if telemetry["summary"]["successful"] > 0:
            response_times = [r["response_time_seconds"] for r in telemetry["results"] if r["status"] == "SUCCESS"]
            telemetry["summary"]["total_time"] = round(sum(response_times), 2)
            telemetry["summary"]["avg_response_time"] = round(sum(response_times) / len(response_times), 2)
            
            fastest = min(telemetry["results"], key=lambda x: x.get("response_time_seconds", float('inf')))
            slowest = max(telemetry["results"], key=lambda x: x.get("response_time_seconds", 0))
            
            telemetry["summary"]["fastest_query"] = {
                "id": fastest["id"],
                "time": fastest["response_time_seconds"]
            }
            telemetry["summary"]["slowest_query"] = {
                "id": slowest["id"],
                "time": slowest["response_time_seconds"]
            }
            
            # Category-wise stats
            for category in set(tc["category"] for tc in STRESS_TEST_QUESTIONS):
                category_results = [r for r in telemetry["results"] if r["category"] == category]
                successful = [r for r in category_results if r["status"] == "SUCCESS"]
                
                telemetry["summary"]["category_stats"][category] = {
                    "total": len(category_results),
                    "successful": len(successful),
                    "failed": len(category_results) - len(successful),
                    "avg_time": round(sum(r["response_time_seconds"] for r in successful) / len(successful), 2) if successful else 0
                }
        
        # Print summary
        print("\n" + "="*100)
        print("📊 STRESS TEST SUMMARY")
        print("="*100)
        print(f"\n✅ Successful: {telemetry['summary']['successful']}/{telemetry['total_questions']}")
        print(f"❌ Failed: {telemetry['summary']['failed']}/{telemetry['total_questions']}")
        print(f"⏱️  Total Time: {telemetry['summary']['total_time']}s")
        print(f"📈 Avg Response Time: {telemetry['summary']['avg_response_time']}s")
        
        if telemetry['summary'].get('fastest_query'):
            print(f"🏃 Fastest Query: #{telemetry['summary']['fastest_query']['id']} ({telemetry['summary']['fastest_query']['time']}s)")
            print(f"🐌 Slowest Query: #{telemetry['summary']['slowest_query']['id']} ({telemetry['summary']['slowest_query']['time']}s)")
        
        print("\n📂 CATEGORY-WISE BREAKDOWN:")
        for category, stats in telemetry['summary']['category_stats'].items():
            print(f"\n  {category}:")
            print(f"    ✅ Success: {stats['successful']}/{stats['total']}")
            print(f"    ⏱️  Avg Time: {stats['avg_time']}s")
        
        # Save telemetry to file
        log_file = PROJECT_ROOT / "data" / f"nlq_stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(telemetry, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Full telemetry saved to: {log_file}")
        print("="*100)
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_stress_test()
