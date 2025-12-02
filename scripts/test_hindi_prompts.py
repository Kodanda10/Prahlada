#!/usr/bin/env python3
"""
Test: Hindi prompt generation
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from mlx_lm import load, generate

print("🇮🇳 Testing Gemma 3 with Hindi prompts...")
print("Loading model...")

model, tokenizer = load("mlx-community/gemma-3-12b-it-qat-4bit")
print("✅ Model loaded!\n")

# Test 1: Simple Hindi conversation
prompt1 = "नमस्ते, आप कौन हैं?"
print(f"📝 Test 1 - Simple Hindi:\nPrompt: {prompt1}")
response1 = generate(model, tokenizer, prompt=prompt1, max_tokens=100)
print(f"Response:\n{response1}\n")
print("-" * 80)

# Test 2: Political analysis (basic)
prompt2 = """यह ट्वीट है: "माओवाद के खिलाफ आदरणीय प्रधानमंत्री श्री नरेंद्र मोदी जी व माननीय गृह मंत्री श्री अमित शाह जी के संकल्प एवं ग्रामीणों का साहस-एकजुटता दर्शाता है कि लाल आतंक के गिने-चुने दिन बचे हैं।"

इस ट्वीट का मुख्य विषय क्या है? एक वाक्य में जवाब दें।"""

print(f"\n📝 Test 2 - Political content:\nPrompt: {prompt2}")
response2 = generate(model, tokenizer, prompt=prompt2, max_tokens=150)
print(f"Response:\n{response2}\n")
print("-" * 80)

print("\n✅ Hindi prompts work!")
