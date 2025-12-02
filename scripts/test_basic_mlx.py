#!/usr/bin/env python3
"""
Simple test: Can Gemma 3 generate any text at all?
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Test basic MLX-LM import and generation
from mlx_lm import load, generate

print("🔧 Testing Gemma 3 basic generation...")
print("Loading model...")

model, tokenizer = load("mlx-community/gemma-3-12b-it-qat-4bit")

print("✅ Model loaded!")

# Simple test prompt
prompt = "Hello, how are you?"
print(f"\n📝 Prompt: {prompt}")

print("Generating...")
response = generate(model, tokenizer, prompt=prompt, max_tokens=50)

print(f"\n🤖 Response:\n{response}")
print("\n✅ Basic generation works!")
