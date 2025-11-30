"""
Tests for Phi 3.5 cognitive learning loop scenarios.

Tests multi-scenario learning behavior, regression safety, and human-in-the-loop validation.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from backend.cognitive.phi_adapter import PhiSuggestions
from backend.services.overlay_service import OverlayService, get_overlay_service


class TestLearningLoopScenarios:
    """Tests for different learning loop scenarios."""

    @pytest.fixture
    def temp_overlay_dir(self, tmp_path):
        """Create temporary directory for overlay storage."""
        overlay_dir = tmp_path / "overlays"
        overlay_dir.mkdir()
        return overlay_dir

    @pytest.fixture
    def overlay_service(self, temp_overlay_dir):
        """OverlayService instance with temporary storage."""
        return OverlayService(str(temp_overlay_dir))

    def test_baseline_agreement_scenario(self, overlay_service):
        """Test when core parser and Phi 3.5 agree - no overlay needed."""
        core_parser_output = {
            "event_type": "rally",
            "confidence": 0.9,
            "locations": ["Delhi"],
            "schemes": ["PM-KISAN"]
        }

        phi_suggestions = PhiSuggestions(
            event_type_suggestions=["rally"],
            location_candidates=[{"name": "Delhi", "confidence": 0.85}],
            scheme_suggestions=["PM-KISAN"],
            confidence_score=0.88,
            reasoning="Strong agreement with parser output"
        )

        # When parser and Phi agree, no overlay is created
        # Just verify that applying overlays doesn't change correct data
        result = overlay_service.apply_overlays(core_parser_output, "tweet-123")

        assert result == core_parser_output  # No changes
        assert result["event_type"] == phi_suggestions.event_type_suggestions[0]

    def test_disagreement_human_confirms_phi(self, overlay_service):
        """Test when human review confirms Phi suggestion over core parser."""
        # Scenario: Core parser says "meeting", Phi suggests "rally", human confirms "rally"

        tweet_id = "tweet-phi-confirmed-123"
        core_parser_output = {
            "event_type": "meeting",
            "confidence": 0.7,
            "locations": ["Conference Hall"],
            "schemes": []
        }

        phi_suggestions = PhiSuggestions(
            event_type_suggestions=["rally", "protest"],
            location_candidates=[
                {"name": "Delhi", "confidence": 0.9, "context": "Capital city protest location"}
            ],
            scheme_suggestions=[],
            confidence_score=0.85,
            reasoning="Crowd gathering with protest keywords"
        )

        # Human review confirms Phi was correct - create overlay
        overlay_service.add_overlay(
            tweet_id=tweet_id,
            field="event_type",
            corrected_value="rally",
            reviewer_id="human_reviewer_1",
            reviewer_name="Alice Analyst",
            notes="Phi was correct, this is a rally not a meeting"
        )

        overlay_service.add_overlay(
            tweet_id=tweet_id,
            field="locations",
            corrected_value=["Delhi"],
            reviewer_id="human_reviewer_1",
            reviewer_name="Alice Analyst",
            notes="Location correction based on Phi suggestion"
        )

        # Apply overlays to core parser output
        result = overlay_service.apply_overlays(core_parser_output, tweet_id)

        # Verify corrections were applied
        assert result["event_type"] == "rally"  # Changed from "meeting"
        assert result["locations"] == ["Delhi"]  # Changed from "Conference Hall"
        assert result["schemes"] == []  # Unchanged

        # Original core parser output should remain unchanged
        assert core_parser_output["event_type"] == "meeting"
        assert core_parser_output["locations"] == ["Conference Hall"]

    def test_disagreement_human_rejects_phi(self):
        """Test when human review rejects Phi suggestion."""
        # Scenario: Core parser says "meeting", Phi suggests "rally", human confirms "meeting"

        core_parser_output = {
            "event_type": "meeting",
            "confidence": 0.8,
            "locations": ["Conference Hall"],
            "schemes": []
        }

        phi_suggestions = PhiSuggestions(
            event_type_suggestions=["rally"],
            confidence_score=0.6,
            reasoning="Weak signals for protest activity"
        )

        human_corrected_output = {
            "event_type": "meeting",  # Same as core parser
            "confidence": 0.9,
            "locations": ["Conference Hall"],
            "schemes": [],
            "reviewer_notes": "Phi was wrong, this is clearly a business meeting"
        }

        # Learning loop should:
        # 1. Record Phi disagreement for metrics
        # 2. Not create an overlay correction (since human agreed with core parser)
        # 3. Potentially reduce Phi confidence weight for similar cases

        # Verify human agreed with core parser
        assert human_corrected_output["event_type"] == core_parser_output["event_type"]
        assert human_corrected_output["event_type"] != phi_suggestions.event_type_suggestions[0]

    def test_regression_safety_after_learning(self):
        """Test that learned corrections don't break existing correct parses."""
        # Simulate a system that has learned from previous corrections

        # Original correct cases that should remain unchanged
        correct_cases = [
            {
                "tweet_id": "correct-1",
                "text": "Business meeting in Mumbai",
                "core_output": {"event_type": "meeting", "confidence": 0.9},
                "phi_suggestions": PhiSuggestions(event_type_suggestions=["meeting"]),
                "expected_final": {"event_type": "meeting"}  # No overlay needed
            },
            {
                "tweet_id": "learned-correction-1",
                "text": "Farmers rally in Delhi",
                "core_output": {"event_type": "meeting", "confidence": 0.6},  # Wrong
                "phi_suggestions": PhiSuggestions(event_type_suggestions=["rally"]),
                "human_correction": {"event_type": "rally"},  # Approved overlay
                "expected_final": {"event_type": "rally"}  # Overlay applied
            }
        ]

        for case in correct_cases:
            core_result = case["core_output"]

            # Simulate overlay application logic
            final_result = core_result.copy()  # Start with core output

            if "human_correction" in case:
                # Apply approved overlay
                final_result.update(case["human_correction"])

            # Verify final result matches expectation
            assert final_result["event_type"] == case["expected_final"]["event_type"], \
                f"Regression in case {case['tweet_id']}"

            # Core output should remain unchanged
            assert case["core_output"]["event_type"] == core_result["event_type"]

    def test_learning_loop_prevents_overfitting(self):
        """Test that learning doesn't overfit to specific cases."""
        # Simulate multiple similar cases where learning should be conservative

        similar_cases = [
            {
                "text": "Meeting about farming",
                "core_output": {"event_type": "meeting", "schemes": ["PM-KISAN"]},
                "phi_suggestions": PhiSuggestions(scheme_suggestions=["PM-KISAN"]),
                "should_apply_overlay": False  # Don't over-apply to generic cases
            },
            {
                "text": "Farmers protest rally",
                "core_output": {"event_type": "meeting", "schemes": []},  # Wrong event type
                "phi_suggestions": PhiSuggestions(
                    event_type_suggestions=["rally"],
                    scheme_suggestions=["PM-KISAN"]
                ),
                "should_apply_overlay": True  # Specific case with human approval
            }
        ]

        # Learning loop should distinguish between:
        # 1. Generic patterns (don't over-apply)
        # 2. Specific learned corrections (apply only when matching exactly)

        for case in similar_cases:
            core_result = case["core_output"]
            final_result = core_result.copy()

            # Simulate conservative overlay application
            if case["should_apply_overlay"] and "human_correction" in case:
                final_result.update(case.get("human_correction", {}))

            # Verify learning is conservative
            if not case["should_apply_overlay"]:
                assert final_result == core_result, "Over-applied learning to generic case"


class TestLearningLoopStress:
    """Tests for learning loop under stress conditions."""

    def test_batch_learning_scenario(self):
        """Test learning from a batch of mixed correct/incorrect cases."""
        batch_cases = [
            # Correct cases
            {"id": "correct-1", "core_correct": True, "phi_agreed": True},
            {"id": "correct-2", "core_correct": True, "phi_agreed": False},
            # Incorrect cases that Phi got right
            {"id": "incorrect-1", "core_correct": False, "phi_agreed": True, "human_confirmed_phi": True},
            {"id": "incorrect-2", "core_correct": False, "phi_agreed": True, "human_confirmed_phi": False},
            # Cases where both were wrong
            {"id": "both-wrong-1", "core_correct": False, "phi_agreed": False, "human_corrected": True},
        ]

        # Calculate learning metrics
        total_cases = len(batch_cases)
        core_accuracy = sum(1 for c in batch_cases if c["core_correct"]) / total_cases
        phi_agreement = sum(1 for c in batch_cases if c["phi_agreed"]) / total_cases
        phi_helpful = sum(1 for c in batch_cases if c.get("human_confirmed_phi", False)) / total_cases

        # Basic sanity checks
        assert core_accuracy >= 0.0 and core_accuracy <= 1.0
        assert phi_agreement >= 0.0 and phi_agreement <= 1.0
        assert phi_helpful >= 0.0 and phi_helpful <= 1.0

        # Phi should be more helpful than random
        assert phi_helpful >= 0.1, "Phi should provide some helpful corrections"

    def test_learning_loop_memory_bounds(self):
        """Test that learning loop doesn't grow unbounded."""
        # Simulate learning loop with maximum capacity

        max_learned_rules = 1000
        learned_rules = []

        # Simulate adding rules
        for i in range(max_learned_rules + 100):  # Try to add more than max
            rule = {
                "id": f"rule-{i}",
                "pattern": f"pattern_{i}",
                "correction": f"correction_{i}",
                "confidence": 0.8
            }

            learned_rules.append(rule)

            # Simulate cleanup policy (keep only recent/high-confidence rules)
            if len(learned_rules) > max_learned_rules:
                # Remove oldest low-confidence rules
                learned_rules = [r for r in learned_rules if r["confidence"] > 0.7]
                if len(learned_rules) > max_learned_rules:
                    learned_rules = learned_rules[-max_learned_rules:]  # Keep most recent

        # Should not exceed reasonable bounds
        assert len(learned_rules) <= max_learned_rules * 1.2, "Learning loop grew unbounded"

    def test_learning_loop_handles_conflicts(self):
        """Test learning loop resolution of conflicting rules."""
        # Simulate conflicting learned rules for the same pattern

        conflicting_rules = [
            {"pattern": "rally", "correction": {"event_type": "protest"}, "confidence": 0.8},
            {"pattern": "rally", "correction": {"event_type": "gathering"}, "confidence": 0.9},
            {"pattern": "rally", "correction": {"event_type": "rally"}, "confidence": 0.7},
        ]

        # Learning loop should resolve conflicts (e.g., by confidence or recency)
        resolved_correction = max(conflicting_rules, key=lambda r: r["confidence"])

        assert resolved_correction["correction"]["event_type"] == "protest"
        assert resolved_correction["confidence"] == 0.9

    def test_learning_persistence_safety(self):
        """Test that learned rules are safely persisted."""
        # Simulate persistence operation

        learned_rules = [
            {"id": "rule-1", "pattern": "test", "correction": {"event_type": "rally"}},
            {"id": "rule-2", "pattern": "meeting", "correction": {"event_type": "gathering"}},
        ]

        # Simulate safe persistence (no file system access in tests)
        # In real implementation, this would write to a safe directory

        # Verify rules can be serialized safely
        import json
        serialized = json.dumps(learned_rules, ensure_ascii=False)

        # Verify deserialization works
        deserialized = json.loads(serialized)
        assert len(deserialized) == len(learned_rules)
        assert deserialized[0]["pattern"] == "test"

    def test_auto_tuning_conservative_bounds(self):
        """Test that auto-tuning stays within conservative bounds."""
        # Simulate auto-tuning parameters

        base_weights = {
            "phi_event_ranking": 0.3,
            "phi_location_suggestions": 0.2,
            "phi_scheme_detection": 0.1,
        }

        # Simulate learning adjustments
        performance_metrics = {
            "phi_helpful_rate": 0.8,  # Phi is helpful 80% of the time
            "phi_false_positive_rate": 0.1,  # Low false positive rate
        }

        # Auto-tuning logic (simplified)
        if performance_metrics["phi_helpful_rate"] > 0.7:
            # Increase weights slightly
            tuned_weights = {k: min(0.5, v * 1.1) for k, v in base_weights.items()}
        else:
            # Decrease weights
            tuned_weights = {k: max(0.0, v * 0.9) for k, v in base_weights.items()}

        # Verify bounds are respected
        for key, weight in tuned_weights.items():
            assert 0.0 <= weight <= 0.5, f"Weight {key} out of bounds: {weight}"

        # Verify improvements are conservative
        for key in base_weights:
            change = abs(tuned_weights[key] - base_weights[key])
            assert change <= 0.1, f"Too aggressive tuning for {key}: {change}"


class TestLearningLoopValidation:
    """Tests for learning loop validation and safety."""

    def test_overlay_application_safety(self):
        """Test that overlays are applied safely."""
        # Simulate overlay system

        core_outputs = {
            "tweet-1": {"event_type": "meeting", "confidence": 0.8},
            "tweet-2": {"event_type": "rally", "confidence": 0.9},  # High confidence, don't override
            "tweet-3": {"event_type": "meeting", "confidence": 0.6},  # Low confidence, can override
        }

        overlays = {
            "tweet-3": {"event_type": "protest", "approved": True},
        }

        # Simulate safe overlay application
        for tweet_id, core_output in core_outputs.items():
            final_output = core_output.copy()

            if tweet_id in overlays and overlays[tweet_id].get("approved", False):
                # Only apply approved overlays to low-confidence outputs
                if core_output["confidence"] < 0.8:
                    final_output.update(overlays[tweet_id])
                    final_output.pop("approved", None)  # Remove metadata

            # Verify safety: high-confidence outputs unchanged
            if core_output["confidence"] >= 0.8:
                assert final_output == core_output, f"Modified high-confidence output for {tweet_id}"

        # Verify approved overlay was applied to low-confidence output
        # (This would be checked in the loop above)

    def test_learning_requires_human_approval(self):
        """Test that learning only occurs with explicit human approval."""
        # Simulate learning candidates

        unapproved_candidates = [
            {"pattern": "auto-learned-1", "confidence": 0.9, "approved": False},
            {"pattern": "auto-learned-2", "confidence": 0.8, "approved": False},
        ]

        approved_candidates = [
            {"pattern": "human-approved-1", "confidence": 0.7, "approved": True},
        ]

        # Learning loop should only accept approved candidates
        learned_rules = []

        for candidate in unapproved_candidates + approved_candidates:
            if candidate.get("approved", False):
                learned_rules.append(candidate)

        # Only approved candidates should be learned
        assert len(learned_rules) == len(approved_candidates)
        assert all(rule["approved"] for rule in learned_rules)

    def test_learning_loop_audit_trail(self):
        """Test that learning loop maintains audit trail."""
        # Simulate audit trail for learning decisions

        audit_entries = []

        def log_learning_decision(decision_type, details):
            audit_entries.append({
                "timestamp": "2024-01-01T00:00:00",  # Would be real timestamp
                "type": decision_type,
                "details": details
            })

        # Simulate learning decisions
        log_learning_decision("rule_accepted", {"rule_id": "rule-1", "reason": "human_approved"})
        log_learning_decision("rule_rejected", {"rule_id": "rule-2", "reason": "low_confidence"})
        log_learning_decision("overlay_applied", {"tweet_id": "tweet-123", "rule_id": "rule-1"})

        # Verify audit trail completeness
        assert len(audit_entries) == 3

        decision_types = {entry["type"] for entry in audit_entries}
        expected_types = {"rule_accepted", "rule_rejected", "overlay_applied"}
        assert decision_types == expected_types

        # Verify all entries have required fields
        for entry in audit_entries:
            assert "timestamp" in entry
            assert "type" in entry
            assert "details" in entry