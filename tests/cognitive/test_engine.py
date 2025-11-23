import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
import json

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.append(str(SCRIPTS_DIR))

from cognitive.engine import CognitiveEngine
from cognitive.auditor import Auditor
from cognitive.sandbox import Sandbox

class TestCognitiveEngine(unittest.TestCase):
    @patch('cognitive.engine.Sandbox')
    @patch('cognitive.engine.Auditor')
    def setUp(self, MockAuditor, MockSandbox):
        # Setup mocks
        self.mock_auditor_instance = MockAuditor.return_value
        self.mock_sandbox_instance = MockSandbox.return_value
        
        self.mock_auditor_instance.perform_rca.return_value = {
            "analysis": {
                "root_cause": "Missing keyword",
                "missed_features": ["विशाल रैली"],
                "proposed_fix": {
                    "type": "keyword_add",
                    "target_field": "event_type",
                    "value": "विशाल रैली"
                }
            }
        }
        
        self.mock_sandbox_instance.simulate.return_value = {
            "total_tested": 100,
            "changes_count": 1,
            "improved_count": 1,
            "regressed_count": 0,
            "changes": [
                {"tweet_id": "123", "field": "event_type", "old": "Other", "new": "Rally", "confidence_delta": 0.4}
            ]
        }

        self.engine = CognitiveEngine()

    def test_process_correction(self):
        tweet_id = "123"
        text = "Test tweet"
        old_data = {"event_type": "Other"}
        correction = {"field": "event_type", "old_value": "Other", "new_value": "Rally"}

        result = self.engine.process_correction(tweet_id, text, old_data, correction)
        
        # Verify Auditor called
        self.mock_auditor_instance.perform_rca.assert_called_once()
        
        # Verify Sandbox called
        self.mock_sandbox_instance.simulate.assert_called_once()
        
        # Verify Decision
        self.assertEqual(result["decision"]["decision"], "AUTO_DEPLOY")
        self.assertEqual(result["decision"]["metrics"]["regressed"], 0)

if __name__ == "__main__":
    unittest.main()
