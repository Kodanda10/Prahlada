import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "phi3.5", backup_model: str = "gemma2:2b"):
        self.base_url = base_url
        self.model = model
        self.backup_model = backup_model

    def generate(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False) -> Dict[str, Any]:
        """
        Generates a response from the local Ollama model with fallback support.
        """
        # Try primary model
        result = self._generate_request(self.model, prompt, system_prompt, json_mode)
        
        # If error, try backup model
        if "error" in result and self.backup_model:
            print(f"⚠️ Primary model {self.model} failed: {result['error']}. Switching to backup: {self.backup_model}")
            result = self._generate_request(self.backup_model, prompt, system_prompt, json_mode)
            
        return result

    def _generate_request(self, model: str, prompt: str, system_prompt: Optional[str], json_mode: bool) -> Dict[str, Any]:
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1, # Low temperature for logic/reasoning
                "num_ctx": 4096
            }
        }

        if system_prompt:
            payload["system"] = system_prompt
            
        if json_mode:
            payload["format"] = "json"

        try:
            start_time = time.time()
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            duration = time.time() - start_time
            
            return {
                "response": result.get("response", ""),
                "duration_s": duration,
                "model": model
            }
        except urllib.error.URLError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def check_health(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except:
            return False

if __name__ == "__main__":
    # Test client
    client = OllamaClient()
    if client.check_health():
        print("Ollama is running!")
        res = client.generate("Why is the sky blue?", system_prompt="Answer in one sentence.")
        print(res)
    else:
        print("Ollama is NOT running. Please start it with 'ollama serve'.")
