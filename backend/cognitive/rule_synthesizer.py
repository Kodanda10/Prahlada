import json
from typing import Dict, Any

class RuleSynthesizer:
    def __init__(self):
        pass

    def synthesize(self, proposal: Dict[str, Any]) -> str:
        """
        Converts a structured proposal into executable Python code.
        """
        fix_type = proposal.get("type")
        target_field = proposal.get("target_field")
        value = proposal.get("value")

        if not all([fix_type, target_field, value]):
            return "# Error: Incomplete proposal"

        if fix_type == "keyword_add":
            return self._generate_keyword_add(target_field, value)
        elif fix_type == "regex_update":
            return self._generate_regex_update(target_field, value)
        else:
            return f"# Error: Unknown fix type '{fix_type}'"

    def _generate_keyword_add(self, field: str, keyword: str) -> str:
        # Map field names to internal variable names if necessary
        # This is a simplified mapping
        field_map = {
            "event_type": "EVENT_KEYWORDS",
            "location": "LOCATION_KEYWORDS"
        }
        
        var_name = field_map.get(field, f"{field.upper()}_KEYWORDS")
        
        code = f"""
# Auto-generated fix for {field}
if "{keyword}" not in {var_name}:
    {var_name}.append("{keyword}")
print(f"Added '{keyword}' to {var_name}")
"""
        return code

    def _generate_regex_update(self, field: str, pattern: str) -> str:
        code = f"""
# Auto-generated regex update for {field}
import re
NEW_PATTERN_{field.upper()} = re.compile(r"{pattern}")
print(f"Updated regex for {field}")
"""
        return code

if __name__ == "__main__":
    synthesizer = RuleSynthesizer()
    
    proposal = {
        "type": "keyword_add",
        "target_field": "event_type",
        "value": "विशाल रैली"
    }
    
    print(synthesizer.synthesize(proposal))
