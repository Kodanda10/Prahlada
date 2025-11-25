import sys
import json
import random
import copy
from pathlib import Path
from typing import List, Dict, Any

# Add scripts directory to path to import parser
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.append(str(SCRIPTS_DIR))

try:
    import gemini_parser_v2
    from gemini_parser_v2 import GeminiParserV2
except ImportError:
    print("Error: Could not import gemini_parser_v2. Make sure it is in scripts/")
    sys.exit(1)

class Sandbox:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.sample_data = self._load_sample_data()
        self.parser = GeminiParserV2(enable_semantic=False) # Faster for sandbox

    def _load_sample_data(self, sample_size: int = 100) -> List[Dict]:
        """Load a random sample of tweets + Golden Set (if available)"""
        tweets = []
        if not self.data_path.exists():
            return []
            
        with open(self.data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    tweets.append(json.loads(line))
        
        # If dataset is small, take all. Else take sample.
        if len(tweets) <= sample_size:
            return tweets
        return random.sample(tweets, sample_size)

    def simulate(self, code_snippet: str) -> Dict[str, Any]:
        """
        Runs the proposed logic change in a sandbox environment.
        """
        print(f"🧪 Starting Simulation...")
        
        # 1. Baseline Run (Before Fix)
        baseline_results = self._run_parser(self.sample_data)
        
        # 2. Apply Fix (Dynamic Code Execution)
        # We modify the module-level variables in gemini_parser_v2
        try:
            # Create a context with the module
            exec_context = {
                "EVENT_SCORING_RULES": gemini_parser_v2.EVENT_SCORING_RULES,
                "SCHEME_PATTERNS": gemini_parser_v2.SCHEME_PATTERNS,
                "re": gemini_parser_v2.re
            }
            
            # Execute the snippet
            exec(code_snippet, exec_context)
            
            # Update the module with modified structures
            # Note: In Python, list mutations in exec_context reflect in the module if they point to same object
            # But if snippet reassigns variable, we need to update module explicitly
            # For now, assuming snippet does append/update in place
            
        except Exception as e:
            return {"error": f"Code execution failed: {str(e)}"}

        # 3. Test Run (After Fix)
        # Re-initialize parser to pick up any deep copies if they existed (though V1 uses global constants directly)
        # Actually, V1 uses global constants in methods, so mutation works.
        test_results = self._run_parser(self.sample_data)
        
        # 4. Generate Diff Report
        report = self._generate_diff_report(baseline_results, test_results)
        return report

    def _run_parser(self, data: List[Dict]) -> Dict[str, Dict]:
        results = {}
        for record in data:
            # Create a deep copy to avoid mutation side effects between runs
            rec_copy = copy.deepcopy(record)
            # Strip previous parsed data to force re-parse
            if "parsed_data_v8" in rec_copy:
                del rec_copy["parsed_data_v8"]
                
            parsed = self.parser.parse_tweet(rec_copy)
            results[parsed['tweet_id']] = parsed
        return results

    def _generate_diff_report(self, baseline: Dict, test: Dict) -> Dict[str, Any]:
        changes = []
        improved = 0
        regressed = 0
        neutral = 0
        
        for tweet_id, base_res in baseline.items():
            test_res = test.get(tweet_id)
            if not test_res: continue
            
            # Check for changes in key fields
            if 'event_type' not in base_res:
                print(f"DEBUG: Missing event_type in base_res for {tweet_id}. Keys: {list(base_res.keys())}")
                continue
                
            if base_res['event_type'] != test_res['event_type']:
                change = {
                    "tweet_id": tweet_id,
                    "field": "event_type",
                    "old": base_res['event_type'],
                    "new": test_res['event_type'],
                    "confidence_delta": test_res['confidence'] - base_res['confidence']
                }
                changes.append(change)
                
                # Heuristic for improvement/regression
                # In a real system, we'd compare against Ground Truth.
                # Here, we assume if confidence increased, it's an improvement (naive).
                if test_res['confidence'] > base_res['confidence']:
                    improved += 1
                elif test_res['confidence'] < base_res['confidence']:
                    regressed += 1
                else:
                    neutral += 1

        return {
            "total_tested": len(baseline),
            "changes_count": len(changes),
            "improved_count": improved,
            "regressed_count": regressed,
            "changes": changes
        }

if __name__ == "__main__":
    # Test Sandbox
    data_file = PROJECT_ROOT / "data" / "parsed_tweets_v8.jsonl"
    sandbox = Sandbox(data_file)
    
    # Example Fix: Add "विशाल रैली" to Rally keywords
    # Note: We need to match the variable name in gemini_parser_v1
    fix_code = """
# Auto-generated fix
found = False
for i, (keywords, label) in enumerate(EVENT_KEYWORD_CLUSTERS):
    if label == "रैली":
        if "विशाल रैली" not in keywords:
            keywords.append("विशाल रैली")
        found = True
        break
if not found:
    print("Warning: Could not find Rally cluster")
"""
    
    report = sandbox.simulate(fix_code)
    print(json.dumps(report, indent=2, ensure_ascii=False))
