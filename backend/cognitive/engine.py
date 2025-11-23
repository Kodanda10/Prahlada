import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any

# Add scripts directory to path (for Sandbox to find parser if needed)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.append(str(SCRIPTS_DIR))

from .auditor import Auditor
from .rule_synthesizer import RuleSynthesizer
from .sandbox import Sandbox
from .gatekeeper import Gatekeeper

class CognitiveEngine:
    def __init__(self):
        self.auditor = Auditor()
        self.synthesizer = RuleSynthesizer()
        self.sandbox = Sandbox(PROJECT_ROOT / "data" / "parsed_tweets_v8.jsonl")
        self.gatekeeper = Gatekeeper(max_collateral_damage=0)
        self.log_file = PROJECT_ROOT / "data" / "reasoning_logs.jsonl"

    def process_correction(self, tweet_id: str, tweet_text: str, old_data: Dict, correction: Dict) -> Dict[str, Any]:
        """
        Full pipeline: Correction -> RCA -> Code -> Sim -> Decision
        """
        print(f"\n🧠 Cognitive Engine Triggered for Tweet {tweet_id}")
        
        # 1. RCA
        print("   1. Running Auditor (RCA)...")
        audit_report = self.auditor.perform_rca(tweet_text, old_data, correction)
        if "error" in audit_report:
            return {"status": "error", "stage": "auditor", "details": audit_report}
        
        analysis = audit_report.get("analysis", {})
        proposal = analysis.get("proposed_fix")
        print(f"      Root Cause: {analysis.get('root_cause')}")
        print(f"      Proposal: {proposal}")

        if not proposal:
            return {"status": "skipped", "reason": "No fix proposed"}

        # 2. Synthesis
        print("   2. Synthesizing Logic...")
        code_snippet = self.synthesizer.synthesize(proposal)
        print(f"      Generated Code:\n{code_snippet}")

        # 3. Simulation
        print("   3. Running Sandbox Simulation...")
        diff_report = self.sandbox.simulate(code_snippet)
        if "error" in diff_report:
             return {"status": "error", "stage": "sandbox", "details": diff_report}
        
        print(f"      Results: {diff_report['improved_count']} improved, {diff_report['regressed_count']} regressed")

        # 4. Gatekeeping
        print("   4. Gatekeeper Decision...")
        decision = self.gatekeeper.evaluate(diff_report, tweet_id)
        print(f"      Decision: {decision['decision']} ({decision['reason']})")

        # 5. Logging
        log_entry = {
            "id": f"log_{int(datetime.datetime.now().timestamp())}",
            "timestamp": datetime.datetime.now().isoformat(),
            "tweet_id": tweet_id,
            "correction": correction,
            "analysis": analysis,
            "proposal": proposal,
            "code_snippet": code_snippet,
            "simulation": diff_report,
            "decision": decision
        }
        
        self._log_result(log_entry)
        
        return log_entry

    def _log_result(self, entry: Dict):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    engine = CognitiveEngine()
    
    # Simulated Correction Event
    tweet_id = "1893895288290500981"
    text = "कल रायपुर में विशाल किसान रैली का आयोजन किया गया।"
    old_data = {"event_type": "बैठक", "confidence": 0.6}
    correction = {"field": "event_type", "old_value": "बैठक", "new_value": "रैली"}
    
    result = engine.process_correction(tweet_id, text, old_data, correction)
    print("\nFinal Result:", json.dumps(result['decision'], indent=2))
