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
        target_label = proposal.get("target_label")

        if not all([fix_type, target_field, value]):
            return "# Error: Incomplete proposal"

        if fix_type in ["keyword_add", "keyword_addition"]:
            return self._generate_keyword_add(target_field, value, target_label)
        elif fix_type == "regex_update":
            return self._generate_regex_update(target_field, value)
        else:
            return f"# Error: Unknown fix type '{fix_type}'"

    def _generate_keyword_add(self, field: str, keyword: str, label: str = None) -> str:
        if field == "event_type" or field == "description":
            if not label:
                return "# Error: Target label required for event keyword addition"
                
            code = f"""
# Auto-generated fix for {field} (Label: {label})
target_label = "{label}"
keyword = "{keyword}"
found = False

for i, rule in enumerate(EVENT_SCORING_RULES):
    keywords, rule_label, score = rule
    if rule_label == target_label:
        if keyword not in keywords:
            keywords.append(keyword)
            print(f"Added '{{keyword}}' to '{{target_label}}'")
        else:
            print(f"Keyword '{{keyword}}' already exists in '{{target_label}}'")
        found = True
        break

if not found:
    print(f"Warning: Label '{{target_label}}' not found in scoring rules")
"""
            return code
            
        # Fallback for other fields (e.g. location) - simplified
        return f"# Error: Field '{field}' not supported for auto-fix yet"

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
