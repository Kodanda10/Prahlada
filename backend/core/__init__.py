"""
Core module for Project Prahlada Backend.

This module contains:
- Configuration management
- Custom exceptions
- Standardized response helpers
- Common utilities
"""

from .exceptions import (
    APIError,
    ValidationError,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    ExternalServiceError,
)

from .responses import (
    success_response,
    error_response,
    ErrorResponse,
    SuccessResponse,
)

from .config import settings

__all__ = [
    # Exceptions
    "APIError",
    "ValidationError", 
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "DatabaseError",
    "ExternalServiceError",
    # Responses
    "success_response",
    "error_response",
    "ErrorResponse",
    "SuccessResponse",
    # Config
    "settings",
]
