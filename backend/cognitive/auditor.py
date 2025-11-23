import json
import datetime
from typing import Dict, Any
from .ollama_client import OllamaClient

from .prompts import get_auditor_system_prompt, get_auditor_user_prompt

class Auditor:
    def __init__(self, model: Optional[str] = None):
        if model:
            self.client = OllamaClient(model=model)
        else:
            self.client = OllamaClient()

    def perform_rca(self, tweet_text: str, old_parsed_data: Dict, human_correction: Dict) -> Dict[str, Any]:
        """
        Performs Root Cause Analysis (RCA) on why the parser failed.
        """
        system_prompt = get_auditor_system_prompt()
        prompt = get_auditor_user_prompt(tweet_text, old_parsed_data, human_correction)

        print(f"Auditing correction for tweet...")
        result = self.client.generate(prompt, system_prompt=system_prompt, json_mode=True)
        
        if "error" in result:
            return {"error": result["error"]}

        try:
            analysis = json.loads(result["response"])
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "analysis": analysis,
                "meta": {
                    "model": result["model"],
                    "duration": result["duration_s"]
                }
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response as JSON", "raw_response": result["response"]}

if __name__ == "__main__":
    # Test Auditor
    auditor = Auditor()
    
    tweet = "कल रायपुर में विशाल किसान रैली का आयोजन किया गया।"
    old_data = {"event_type": "बैठक"} # Incorrect: Meeting
    correction = {"field": "event_type", "old_value": "बैठक", "new_value": "रैली"} # Correct: Rally
    
    report = auditor.perform_rca(tweet, old_data, correction)
    print(json.dumps(report, indent=2, ensure_ascii=False))
