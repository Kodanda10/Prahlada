import json
from typing import Dict, Any

class Gatekeeper:
    def __init__(self, max_collateral_damage: int = 0):
        self.max_collateral_damage = max_collateral_damage

    def evaluate(self, diff_report: Dict[str, Any], target_tweet_id: str) -> Dict[str, Any]:
        """
        Evaluates the Diff Report and decides whether to deploy the change.
        """
        regressed_count = diff_report.get("regressed_count", 0)
        changes = diff_report.get("changes", [])
        
        # Check if target tweet was fixed
        target_fixed = False
        for change in changes:
            if change["tweet_id"] == target_tweet_id:
                # Assuming improvement means fixed (simplified)
                # Ideally we check if new value matches human correction
                if change.get("confidence_delta", 0) > 0: 
                    target_fixed = True
                break
        
        # Decision Logic
        decision = "BLOCK"
        reason = []

        if regressed_count > self.max_collateral_damage:
            reason.append(f"Collateral damage too high: {regressed_count} regressions (Max: {self.max_collateral_damage})")
        
        if not target_fixed:
            reason.append("Target tweet was not fixed or improved")
            
        if not reason:
            decision = "AUTO_DEPLOY"
            reason.append("No regressions and target fixed")

        return {
            "decision": decision,
            "reason": "; ".join(reason),
            "metrics": {
                "regressed": regressed_count,
                "improved": diff_report.get("improved_count", 0),
                "target_fixed": target_fixed
            }
        }

if __name__ == "__main__":
    gatekeeper = Gatekeeper()
    
    # Example Report
    report = {
        "total_tested": 100,
        "changes_count": 2,
        "improved_count": 1,
        "regressed_count": 0,
        "changes": [
            {"tweet_id": "123", "field": "event_type", "old": "Other", "new": "Rally", "confidence_delta": 0.4}
        ]
    }
    
    decision = gatekeeper.evaluate(report, "123")
    print(json.dumps(decision, indent=2))
