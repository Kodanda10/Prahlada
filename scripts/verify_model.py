import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.cognitive.mlx_engine import mlx_engine

def verify_model():
    print("🚀 Starting Model Verification...")
    # Fallback to Gemma 2 9B since Gemma 3 is not accessible/found
    fallback_model = "mlx-community/gemma-2-9b-it-4bit"
    print(f"Target Model: {fallback_model} (Fallback)")
    
    # Update engine model path
    mlx_engine.model_path = fallback_model
    
    print("This may take a while if the model needs to be downloaded...")
    
    prompt = "नमस्ते, आप कौन हैं? अपना परिचय दें।"
    print(f"\n📝 Prompt: {prompt}")
    
    try:
        response = mlx_engine.generate_response(prompt, max_tokens=100)
        print(f"\n🤖 Response:\n{response}")
        print("\n✅ Verification Successful!")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")

if __name__ == "__main__":
    verify_model()
