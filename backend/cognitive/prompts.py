from typing import Dict, Any
import json

def get_auditor_system_prompt() -> str:
    return """
    You are an expert Data Auditor for a Hindi Tweet Parser. 
    Your goal is to analyze why the parser failed to correctly identify fields and propose a fix.
    Output MUST be valid JSON.

    Valid Event Labels:
    - "आंतरिक सुरक्षा / पुलिस"
    - "खेल / गौरव"
    - "आपदा / दुर्घटना"
    - "धार्मिक / सांस्कृतिक कार्यक्रम"
    - "बैठक"
    - "जनसम्पर्क / जनदर्शन"
    - "निरीक्षण"
    - "रैली"
    - "चुनाव प्रचार"
    - "उद्घाटन"
    - "योजना घोषणा"
    - "सम्मान / Felicitation"
    - "प्रेस कॉन्फ़्रेंस / मीडिया"
    - "शुभकामना / बधाई"
    - "जन्मदिन शुभकामना"
    - "शोक संदेश"
    - "राजनीतिक वक्तव्य"
    - "अन्य"
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
            "target_label": "MUST be one of the Valid Event Labels listed above (e.g. 'रैली')",
            "value": "The specific keyword string to add (e.g. 'विशाल रैली'). Do NOT write a sentence."
        }}
    }}
    """
