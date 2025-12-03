
import sys
import os
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.gemini_parser_v2 import EntityExtractorV2

def test_extraction():
    extractor = EntityExtractorV2()
    
    test_cases = [
        {
            "text": "आज केंद्रीय राज्य मंत्री श्री तोखन साहू जी से मुलाकात हुई।",
            "expected": ["तोखन साहू"]
        },
        {
            "text": "महामहिम राज्यपाल श्री रमेन डेका जी का छत्तीसगढ़ आगमन।",
            "expected": ["रमेन डेका"]
        },
        {
            "text": "माननीय मुख्यमंत्री श्री विष्णु देव साय जी के साथ।",
            "expected": ["विष्णु देव साय"]
        },
        {
            "text": "पूर्व मुख्यमंत्री भूपेश बघेल ने बयान दिया।",
            "expected": ["भूपेश बघेल"]
        }
    ]
    
    print("Running People Extraction Debug...")
    print("-" * 50)
    
    failures = 0
    for case in test_cases:
        text = case["text"]
        expected = set(case["expected"])
        extracted = set(extractor.extract_people(text))
        
        missing = expected - extracted
        extra = extracted - expected
        
        if missing:
            print(f"❌ FAILED: {text}")
            print(f"   Expected: {expected}")
            print(f"   Got:      {extracted}")
            print(f"   Missing:  {missing}")
            failures += 1
        else:
            print(f"✅ PASSED: {text}")
            print(f"   Got: {extracted}")
            
    print("-" * 50)
    if failures == 0:
        print("🎉 All debug cases passed!")
    else:
        print(f"⚠️ {failures} cases failed.")

if __name__ == "__main__":
    test_extraction()
