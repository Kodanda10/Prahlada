"""
Unit tests for backend core modules.

Tests exceptions, responses, and configuration.
"""

import os
import pytest

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from backend.core.exceptions import (
    APIError,
    ValidationError,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    ExternalServiceError,
    RateLimitError,
    ConflictError,
)
from backend.core.responses import (
    success_response,
    error_response,
    ErrorResponse,
    SuccessResponse,
    validation_error_response,
)
from backend.core.config import Settings


class TestAPIError:
    """Unit tests for APIError base class."""

    def test_api_error_basic(self):
        """Should create basic APIError."""
        error = APIError("Test error", status_code=400, error_code="TEST_ERROR")

        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.error_code == "TEST_ERROR"
        assert error.details == {}

    def test_api_error_with_details(self):
        """Should create APIError with details."""
        details = {"field": "email", "reason": "invalid format"}
        error = APIError(
            "Validation failed",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )

        assert error.message == "Validation failed"
        assert error.details == details

    def test_api_error_to_dict(self):
        """Should convert to dictionary correctly."""
        error = APIError(
            "Test error",
            status_code=400,
            error_code="TEST_ERROR",
            details={"key": "value"}
        )

        result = error.to_dict()

        expected = {
            "status": "error",
            "message": "Test error",
            "code": "TEST_ERROR",
            "details": {"key": "value"}
        }
        assert result == expected

    def test_api_error_to_dict_no_details(self):
        """Should omit details when empty."""
        error = APIError("Test error", status_code=400, error_code="TEST_ERROR")

        result = error.to_dict()

        expected = {
            "status": "error",
            "message": "Test error",
            "code": "TEST_ERROR"
        }
        assert result == expected


class TestValidationError:
    """Unit tests for ValidationError."""

    def test_validation_error_basic(self):
        """Should create ValidationError with field and reason."""
        error = ValidationError(field="email", reason="invalid format")

        assert error.message == "Validation failed"
        assert error.status_code == 422
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details == {"field": "email", "reason": "invalid format"}

    def test_validation_error_custom_message(self):
        """Should use custom message when provided."""
        error = ValidationError(
            message="Custom validation error",
            field="password",
            reason="too short"
        )

        assert error.message == "Custom validation error"
        assert error.details == {"field": "password", "reason": "too short"}

    def test_validation_error_no_field_reason(self):
        """Should work without field and reason."""
        error = ValidationError(message="Generic validation error")

        assert error.message == "Generic validation error"
        assert error.details == {}


class TestNotFoundError:
    """Unit tests for NotFoundError."""

    def test_not_found_error_with_identifier(self):
        """Should create NotFoundError with resource and identifier."""
        error = NotFoundError(resource="User", identifier="123")

        assert error.message == "User with ID '123' not found"
        assert error.status_code == 404
        assert error.error_code == "NOT_FOUND"
        assert error.details == {"resource": "User", "identifier": "123"}

    def test_not_found_error_without_identifier(self):
        """Should create NotFoundError without identifier."""
        error = NotFoundError(resource="User")

        assert error.message == "User not found"
        assert error.status_code == 404
        assert error.error_code == "NOT_FOUND"
        assert error.details == {"resource": "User"}

    def test_not_found_error_custom_message(self):
        """Should use custom message when provided."""
        error = NotFoundError(resource="Document", message="Document not available")

        assert error.message == "Document not available"
        assert error.details == {"resource": "Document"}


class TestAuthenticationError:
    """Unit tests for AuthenticationError."""

    def test_authentication_error_basic(self):
        """Should create AuthenticationError."""
        error = AuthenticationError()

        assert error.message == "Authentication failed"
        assert error.status_code == 401
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.details == {}

    def test_authentication_error_with_reason(self):
        """Should include reason in details."""
        error = AuthenticationError(reason="Invalid credentials")

        assert error.details == {"reason": "Invalid credentials"}


class TestAuthorizationError:
    """Unit tests for AuthorizationError."""

    def test_authorization_error_basic(self):
        """Should create AuthorizationError."""
        error = AuthorizationError()

        assert error.message == "You don't have permission to perform this action"
        assert error.status_code == 403
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert error.details == {}

    def test_authorization_error_with_role(self):
        """Should include required role in details."""
        error = AuthorizationError(required_role="admin")

        assert error.details == {"required_role": "admin"}


class TestDatabaseError:
    """Unit tests for DatabaseError."""

    def test_database_error_basic(self):
        """Should create DatabaseError."""
        error = DatabaseError()

        assert error.message == "A database error occurred"
        assert error.status_code == 500
        assert error.error_code == "DATABASE_ERROR"
        assert error.details == {}

    def test_database_error_with_operation(self):
        """Should include operation in details."""
        error = DatabaseError(operation="user_query")

        assert error.details == {"operation": "user_query"}


class TestExternalServiceError:
    """Unit tests for ExternalServiceError."""

    def test_external_service_error_basic(self):
        """Should create ExternalServiceError."""
        error = ExternalServiceError(service="vector_store")

        assert error.message == "External service 'vector_store' is unavailable"
        assert error.status_code == 503
        assert error.error_code == "SERVICE_UNAVAILABLE"
        assert error.details == {"service": "vector_store"}

    def test_external_service_error_with_reason(self):
        """Should include reason in details."""
        error = ExternalServiceError(service="ai_engine", reason="timeout")

        assert error.details == {"service": "ai_engine", "reason": "timeout"}


class TestRateLimitError:
    """Unit tests for RateLimitError."""

    def test_rate_limit_error_basic(self):
        """Should create RateLimitError."""
        error = RateLimitError()

        assert error.message == "Rate limit exceeded. Please try again later."
        assert error.status_code == 429
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.details == {}

    def test_rate_limit_error_with_retry_after(self):
        """Should include retry_after in details."""
        error = RateLimitError(retry_after=60)

        assert error.details == {"retry_after_seconds": 60}


class TestConflictError:
    """Unit tests for ConflictError."""

    def test_conflict_error_basic(self):
        """Should create ConflictError."""
        error = ConflictError()

        assert error.message == "Resource conflict"
        assert error.status_code == 409
        assert error.error_code == "CONFLICT"
        assert error.details == {}

    def test_conflict_error_with_details(self):
        """Should include resource and reason."""
        error = ConflictError(resource="User", reason="email already exists")

        assert error.details == {"resource": "User", "reason": "email already exists"}


class TestResponseHelpers:
    """Unit tests for response helper functions."""

    def test_success_response_basic(self):
        """Should create basic success response."""
        result = success_response("Operation successful")

        expected = {
            "status": "success",
            "message": "Operation successful"
        }
        assert result == expected

    def test_success_response_with_data(self):
        """Should include data in success response."""
        data = {"user_id": "123", "email": "test@example.com"}
        result = success_response("User created", data=data)

        expected = {
            "status": "success",
            "message": "User created",
            "data": data
        }
        assert result == expected

    def test_error_response_basic(self):
        """Should create basic error response."""
        result = error_response("Something went wrong")

        expected = {
            "status": "error",
            "message": "Something went wrong"
        }
        assert result == expected

    def test_error_response_full(self):
        """Should create full error response."""
        result = error_response(
            "Validation failed",
            code="VALIDATION_ERROR",
            details={"field": "email", "reason": "invalid"}
        )

        expected = {
            "status": "error",
            "message": "Validation failed",
            "code": "VALIDATION_ERROR",
            "details": {"field": "email", "reason": "invalid"}
        }
        assert result == expected

    def test_validation_error_response(self):
        """Should create validation error response."""
        result = validation_error_response("email", "must be valid email")

        expected = {
            "status": "error",
            "message": "Validation failed for field 'email'",
            "code": "VALIDATION_ERROR",
            "details": {"field": "email", "reason": "must be valid email"}
        }
        assert result == expected

    def test_validation_error_response_custom_message(self):
        """Should use custom message in validation error response."""
        result = validation_error_response(
            "password",
            "too short",
            message="Password validation failed"
        )

        expected = {
            "status": "error",
            "message": "Password validation failed",
            "code": "VALIDATION_ERROR",
            "details": {"field": "password", "reason": "too short"}
        }
        assert result == expected


class TestResponseModels:
    """Unit tests for response Pydantic models."""

    def test_error_response_model(self):
        """Should create ErrorResponse model."""
        response = ErrorResponse(
            message="Test error",
            code="TEST_ERROR",
            details={"key": "value"}
        )

        assert response.status == "error"
        assert response.message == "Test error"
        assert response.code == "TEST_ERROR"
        assert response.details == {"key": "value"}

    def test_success_response_model(self):
        """Should create SuccessResponse model."""
        response = SuccessResponse(
            message="Operation successful",
            data={"result": "ok"}
        )

        assert response.status == "success"
        assert response.message == "Operation successful"
        assert response.data == {"result": "ok"}

    def test_success_response_model_no_data(self):
        """Should create SuccessResponse without data."""
        response = SuccessResponse(message="Operation successful")

        assert response.status == "success"
        assert response.message == "Operation successful"
        assert response.data is None


class TestSettings:
    """Unit tests for Settings configuration."""

    def test_settings_defaults(self):
        """Should load default settings."""
        settings = Settings()

        assert settings.APP_NAME == "Project Prahlada API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.DEBUG is False
        assert settings.AUTH_ALGORITHM == "HS256"
        assert settings.AUTH_TOKEN_EXPIRE_MINUTES == 60
        assert len(settings.CORS_ORIGINS) == 6


    def test_settings_validation(self):
        """Should validate required settings."""
        # Settings should pass validation with defaults
        settings = Settings()
        assert settings is not None

    def test_environment_enum(self):
        """Should define valid environment profiles."""
        from backend.core.config import Environment

        assert Environment.LOCAL == "local"
        assert Environment.TEST == "test"
        assert Environment.PRODUCTION == "prod"

    @pytest.mark.parametrize("env,expected", [
        ("local", True),
        ("test", False),
        ("prod", False)
    ])
    def test_is_local_property(self, monkeypatch, env, expected):
        """Should correctly identify local environment."""
        monkeypatch.setenv("ENV", env)
        # Clear lru_cache to force reload
        from backend.core.config import get_settings
        get_settings.cache_clear()

        settings = Settings()
        assert settings.is_local == expected

    @pytest.mark.parametrize("env,expected", [
        ("local", False),
        ("test", True),
        ("prod", False)
    ])
    def test_is_test_property(self, monkeypatch, env, expected):
        """Should correctly identify test environment."""
        monkeypatch.setenv("ENV", env)
        from backend.core.config import get_settings
        get_settings.cache_clear()

        settings = Settings()
        assert settings.is_test == expected

    @pytest.mark.parametrize("env,expected", [
        ("local", False),
        ("test", False),
        ("prod", True)
    ])
    def test_is_production_property(self, monkeypatch, env, expected):
        """Should correctly identify production environment."""
        monkeypatch.setenv("ENV", env)
        from backend.core.config import get_settings
        get_settings.cache_clear()

        settings = Settings()
        assert settings.is_production == expected

    def test_phi_config_property(self):
        """Should provide Phi configuration summary."""
        settings = Settings()
        phi_config = settings.phi_config

        expected_keys = ["enabled", "base_url", "model", "backup_model", "timeout"]
        for key in expected_keys:
            assert key in phi_config

    def test_environment_summary(self):
        """Should provide environment configuration summary."""
        settings = Settings()
        summary = settings.get_environment_summary()

        expected_keys = [
            "environment", "debug", "database_configured",
            "auth_configured", "phi_enabled", "vector_store_model",
            "log_level", "admin_configured"
        ]

        for key in expected_keys:
            assert key in summary

    def test_test_environment_overrides(self, monkeypatch):
        """Should apply test environment overrides."""
        monkeypatch.setenv("ENV", "test")
        monkeypatch.setenv("AUTH_SECRET_KEY", "")  # Clear to test override

        from backend.core.config import get_settings
        get_settings.cache_clear()

        settings = Settings()

        assert settings.is_test is True
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "WARNING"
        assert settings.USE_PHI_LOCAL is False
        # Should have test defaults set
        assert settings.AUTH_SECRET_KEY == "test-secret-key-for-testing-only"

    def test_local_environment_overrides(self, monkeypatch):
        """Should apply local environment overrides."""
        monkeypatch.setenv("ENV", "local")
        monkeypatch.setenv("DATABASE_URL", "")  # Clear to test override

        from backend.core.config import get_settings
        get_settings.cache_clear()

        settings = Settings()

        assert settings.is_local is True
        assert settings.DEBUG is True
        assert settings.USE_PHI_LOCAL is False

    def test_production_validation_requires_settings(self, monkeypatch):
        """Should require essential settings in production."""
        monkeypatch.setenv("ENV", "prod")
        monkeypatch.setenv("AUTH_SECRET_KEY", "")
        monkeypatch.setenv("DATABASE_URL", "")

        from backend.core.config import get_settings
        get_settings.cache_clear()

        with pytest.raises(ValueError, match="Required setting"):
            Settings()


    def test_has_admin_credentials_none(self):
        """Should return False when admin credentials are not set."""
        settings = Settings()

        assert settings.has_admin_credentials is False

    def test_has_admin_credentials_partial(self, monkeypatch):
        """Should return False when only partial credentials are set."""
        monkeypatch.setenv("ADMIN_USERNAME", "admin")
        settings = Settings()

        assert settings.has_admin_credentials is False
