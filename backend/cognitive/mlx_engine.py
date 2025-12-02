import mlx.core as mx
from mlx_lm import load, generate
from typing import Optional, Dict, Any, List
import os
import json

class MLXEngine:
    """
    Singleton engine for running Gemma 3 QAT 12B via MLX.
    Designed to respect the 16GB RAM limit of the M4 Mac mini.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MLXEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_path: str = "mlx-community/gemma-3-12b-it-qat-4bit"):
        # Ensure __init__ is only run once
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        print(f"Initializing MLXEngine with model: {model_path}")
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.initialized = True

    def load_model(self):
        """
        Loads the model into memory.
        """
        if self.model is not None:
            return

        print(f"Loading model from {self.model_path}...")
        try:
            # Load model and tokenizer
            # trust_remote_code=True might be needed for some models, but usually not for standard Gemma
            self.model, self.tokenizer = load(self.model_path)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to load MLX model: {e}")
            raise e

    def generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Generates a response for the given prompt.
        """
        if self.model is None:
            self.load_model()

        print("Generating response...")
        try:
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            print(f"Error during generation: {e}")
            return ""

    def generate_json(self, prompt: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generates a JSON response. 
        If schema is provided, we can try to enforce it (via prompt engineering for now).
        """
        json_prompt = prompt + "\n\nIMPORTANT: Output ONLY valid JSON."
        if schema:
            json_prompt += f"\nSchema: {json.dumps(schema)}"
        
        response_text = self.generate_response(json_prompt)
        
        # Basic cleanup to extract JSON
        try:
            # Find first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                print("No JSON found in response.")
                return {"error": "No JSON found", "raw_text": response_text}
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return {"error": "Invalid JSON", "raw_text": response_text}

    def unload_model(self):
        """
        Unloads the model to free up memory.
        """
        self.model = None
        self.tokenizer = None
        # Force garbage collection if needed, though Python/MLX handles it mostly
        import gc
        gc.collect()
        print("Model unloaded.")

# Global instance
mlx_engine = MLXEngine()
