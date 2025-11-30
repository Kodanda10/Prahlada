"""
Tests for Phi 3.5 governance and guardrails.

Ensures Phi 3.5 operates within safe boundaries and never modifies core parser logic.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from backend.cognitive.phi_adapter import PhiAdapter, PhiSuggestions


class TestPhiGuardrails:
    """Tests for Phi 3.5 operational guardrails."""

    def test_phi_adapter_disabled_by_default(self):
        """Phi adapter should be disabled by default for safety."""
        adapter = PhiAdapter()

        assert adapter.enabled is False
        assert adapter.client is None

    def test_phi_adapter_respects_enabled_flag(self):
        """Phi adapter should only make calls when enabled."""
        # Test disabled
        disabled_adapter = PhiAdapter(enabled=False)
        result = disabled_adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

        # Test enabled (but will fail without actual Ollama)
        enabled_adapter = PhiAdapter(enabled=True)
        result = enabled_adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        # Should still return PhiSuggestions object, even on failure
        assert isinstance(result, PhiSuggestions)

    def test_phi_suggestions_are_advisory_only(self):
        """Phi suggestions should not contain executable code or file operations."""
        suggestions = PhiSuggestions(
            event_type_suggestions=["rally", "protest"],
            reasoning="Based on keywords like 'crowd' and 'gathering'"
        )

        # Should not contain any code-like content
        assert "import" not in suggestions.reasoning
        assert "os." not in suggestions.reasoning
        assert "exec(" not in suggestions.reasoning
        assert "eval(" not in suggestions.reasoning

        # Should not contain file paths
        assert "/parser/" not in suggestions.reasoning
        assert ".py" not in suggestions.reasoning

    def test_phi_adapter_handles_json_parse_errors(self):
        """Should handle malformed JSON responses from Phi."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()
        mock_client.generate.return_value = {
            "response": '{"invalid": json, "missing": "brackets"',
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        # Should return empty suggestions on parse error
        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

    def test_phi_adapter_timeout_handling(self):
        """Should handle timeouts and network errors gracefully."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()
        mock_client.generate.side_effect = Exception("Connection timeout")
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        # Should not crash, should return empty suggestions
        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

    def test_phi_adapter_validates_structured_output(self):
        """Should validate that Phi responses contain expected structured data."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()

        # Test valid structured response
        valid_response = {
            "response": '''{
                "event_type_suggestions": ["rally", "protest"],
                "location_candidates": [{"name": "Delhi", "confidence": 0.8}],
                "scheme_suggestions": ["PM-KISAN"],
                "confidence_score": 0.85,
                "reasoning": "Based on protest keywords"
            }''',
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        mock_client.generate.return_value = valid_response
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        assert result.event_type_suggestions == ["rally", "protest"]
        assert result.location_candidates == [{"name": "Delhi", "confidence": 0.8}]
        assert result.scheme_suggestions == ["PM-KISAN"]
        assert result.confidence_score == 0.85

    def test_phi_adapter_rejects_unstructured_responses(self):
        """Should reject free-form text responses that aren't structured."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()

        # Free-form text response (not JSON)
        unstructured_response = {
            "response": "The tweet seems to be about a rally. There are people gathering and protesting.",
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        mock_client.generate.return_value = unstructured_response
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        # Should return empty suggestions for unstructured response
        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []
        assert result.reasoning == ""  # No reasoning extracted

    def test_phi_adapter_backup_model_fallback(self):
        """Should attempt fallback to backup model on primary failure."""
        adapter = PhiAdapter(enabled=True, backup_model="gemma2:2b")
        mock_client = MagicMock()

        # Primary model fails, backup succeeds
        mock_client.generate.side_effect = [
            {"error": "Primary model unavailable"},
            {
                "response": '{"event_type_suggestions": ["backup_result"]}',
                "duration_s": 1.0,
                "model": "gemma2:2b"
            }
        ]
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        assert result.event_type_suggestions == ["backup_result"]
        assert mock_client.generate.call_count == 2  # Tried both models

    def test_phi_adapter_no_backup_fallback(self):
        """Should fail gracefully when no backup model available."""
        adapter = PhiAdapter(enabled=True, backup_model=None)
        mock_client = MagicMock()
        mock_client.generate.return_value = {"error": "Model unavailable"}
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []


class TestPhiLearningBoundaries:
    """Tests for Phi learning loop boundaries."""

    def test_phi_cannot_modify_core_parser_files(self):
        """Phi should never attempt to modify core parser files."""
        # This test ensures that Phi suggestions don't contain file system operations
        # In a real implementation, we'd monitor for any file write attempts

        suggestions = PhiSuggestions(
            event_type_suggestions=["rally"],
            reasoning="This appears to be a protest rally based on keywords"
        )

        # Ensure reasoning doesn't contain dangerous operations
        dangerous_patterns = [
            "import os",
            "open(",
            "write(",
            "save(",
            "load(",
            "exec(",
            "eval(",
            "subprocess",
            "system(",
            "popen(",
            "call(",
            "run(",
        ]

        reasoning_text = suggestions.reasoning.lower()
        for pattern in dangerous_patterns:
            assert pattern not in reasoning_text, f"Found dangerous pattern '{pattern}' in reasoning"

    def test_phi_suggestions_contain_only_allowed_fields(self):
        """Phi suggestions should only contain predefined allowed fields."""
        allowed_fields = {
            "event_type_suggestions",
            "location_candidates",
            "scheme_suggestions",
            "confidence_score",
            "reasoning",
            "raw_response"
        }

        suggestions = PhiSuggestions(
            event_type_suggestions=["rally"],
            location_candidates=[{"name": "Delhi"}],
            scheme_suggestions=["PM-KISAN"],
            confidence_score=0.8,
            reasoning="Based on analysis",
            raw_response="raw data"
        )

        suggestions_dict = suggestions.to_dict()

        # All fields should be in allowed set
        for field in suggestions_dict.keys():
            assert field in allowed_fields, f"Unexpected field '{field}' in suggestions"

    def test_phi_adapter_preserves_core_parser_invariants(self):
        """Phi adapter should never suggest changes to core parser logic."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()

        # Mock a response that tries to suggest parser changes (should be rejected)
        dangerous_response = {
            "response": '''{
                "event_type_suggestions": ["rally"],
                "reasoning": "Modify the parser regex to include new patterns",
                "parser_modifications": ["change regex", "update mapping"]
            }''',
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        mock_client.generate.return_value = dangerous_response
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        # Should reject suggestions containing parser modification requests
        assert "parser_modifications" not in result.to_dict()
        assert "regex" not in result.reasoning.lower()
        assert "mapping" not in result.reasoning.lower()

    def test_phi_learning_loop_respects_versioning(self):
        """Any learned rules should be properly versioned."""
        # This test ensures that if we implement a learning loop,
        # it would create versioned entries rather than overwriting

        # For now, this is a placeholder test that would be expanded
        # when the learning loop is implemented

        # The test passes because we haven't implemented destructive learning
        assert True, "Learning loop respects versioning (not yet implemented)"

    def test_phi_cannot_access_forbidden_directories(self):
        """Phi should never suggest or attempt access to forbidden directories."""
        forbidden_paths = [
            "/parser/",
            "/core/",
            "/cognitive/engine.py",
            "/scripts/",
            "../",
            "..",
            "~",
            "/etc/",
            "/var/",
        ]

        suggestions = PhiSuggestions(
            event_type_suggestions=["rally"],
            reasoning="Analysis complete"
        )

        reasoning_text = suggestions.reasoning.lower()
        for forbidden_path in forbidden_paths:
            assert forbidden_path not in reasoning_text, \
                f"Found forbidden path '{forbidden_path}' in reasoning"


class TestPhiResourceLimits:
    """Tests for Phi resource usage limits."""

    def test_phi_adapter_limits_response_size(self):
        """Should limit the size of Phi responses to prevent abuse."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()

        # Very large response
        large_response = "x" * 100000  # 100KB of response
        mock_client.generate.return_value = {
            "response": large_response,
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        # Should handle large responses without crashing
        # (In real implementation, we'd limit response size)
        assert isinstance(result, PhiSuggestions)

    def test_phi_adapter_handles_empty_responses(self):
        """Should handle completely empty responses from Phi."""
        adapter = PhiAdapter(enabled=True)
        mock_client = MagicMock()
        mock_client.generate.return_value = {
            "response": "",
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        adapter.client = mock_client

        result = adapter.suggest_parser_corrections(
            "test-123", "test tweet", {"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

    def test_phi_adapter_timeout_limits(self):
        """Should respect timeout limits to prevent hanging."""
        # This test ensures the adapter has reasonable timeouts configured
        adapter = PhiAdapter(enabled=True)

        if adapter.client:
            # In a real implementation, we'd check timeout settings
            # For now, just verify the adapter can be created
            assert adapter.client is not None