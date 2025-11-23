from typing import Dict, Any
import json

def get_auditor_system_prompt() -> str:
    return """
    You are an expert Data Auditor for a Hindi Tweet Parser. 
    Your goal is to analyze why the parser failed to correctly identify fields and propose a fix.
    Output MUST be valid JSON.
    """

def get_auditor_user_prompt(tweet_text: str, old_parsed_data: Dict, human_correction: Dict) -> str:
    return f"""
    Original Tweet: "{tweet_text}"
    
    Parser Output: {json.dumps(old_parsed_data, ensure_ascii=False)}
    
    Human Correction: {json.dumps(human_correction, ensure_ascii=False)}
    
    Task:
    1. Analyze why the parser output differed from the human correction.
    2. Identify the missing keyword, pattern, or logic gap.
    3. Propose a specific fix (e.g., add keyword "X" to category "Y").
    
    Response Format (JSON):
    {{
        "root_cause": "Brief explanation of failure",
        "missed_features": ["list", "of", "keywords/patterns"],
        "proposed_fix": {{
            "type": "keyword_add" | "regex_update",
            "target_field": "{human_correction.get('field', 'unknown')}",
            "value": "value to add/change"
        }}
    }}
    """
