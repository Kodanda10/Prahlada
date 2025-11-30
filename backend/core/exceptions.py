"""
Custom exceptions for the backend API.

These exceptions provide structured error handling with:
- HTTP status codes
- User-friendly messages
- Optional detailed error information
- Internal error codes for logging/debugging
"""

from typing import Any, Dict, Optional


class APIError(Exception):
    """
    Base exception for all API errors.
    
    All custom exceptions should inherit from this class.
    
    Attributes:
        message: Human-readable error message (safe to show to users)
        status_code: HTTP status code to return
        error_code: Internal error code for logging/debugging
        details: Additional error details (optional)
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for JSON response."""
        response = {
            "status": "error",
            "message": self.message,
            "code": self.error_code,
        }
        if self.details:
            response["details"] = self.details
        return response


class ValidationError(APIError):
    """
    Exception for request validation errors.
    
    Use when request data fails validation (missing fields, wrong types, etc.)
    """
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if reason:
            error_details["reason"] = reason
        
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=error_details,
        )


class NotFoundError(APIError):
    """
    Exception for resource not found errors.
    
    Use when a requested resource (tweet, event, user, etc.) doesn't exist.
    """
    
    def __init__(
        self,
        resource: str = "Resource",
        identifier: Optional[str] = None,
        message: Optional[str] = None,
    ):
        if message is None:
            if identifier:
                message = f"{resource} with ID '{identifier}' not found"
            else:
                message = f"{resource} not found"
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier} if identifier else {"resource": resource},
        )


class AuthenticationError(APIError):
    """
    Exception for authentication failures.
    
    Use when credentials are invalid, token is expired, etc.
    """
    
    def __init__(
        self,
        message: str = "Authentication failed",
        reason: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details={"reason": reason} if reason else {},
        )


class AuthorizationError(APIError):
    """
    Exception for authorization failures.
    
    Use when user is authenticated but lacks permission.
    """
    
    def __init__(
        self,
        message: str = "You don't have permission to perform this action",
        required_role: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details={"required_role": required_role} if required_role else {},
        )


class DatabaseError(APIError):
    """
    Exception for database operation failures.
    
    Use when database queries fail. Don't expose internal DB errors to users.
    """
    
    def __init__(
        self,
        message: str = "A database error occurred",
        operation: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details={"operation": operation} if operation else {},
        )


class ExternalServiceError(APIError):
    """
    Exception for external service failures.
    
    Use when calls to external services (vector store, cognitive engine, etc.) fail.
    """
    
    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        if message is None:
            message = f"External service '{service}' is unavailable"
        
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details={"service": service, "reason": reason} if reason else {"service": service},
        )


class RateLimitError(APIError):
    """
    Exception for rate limiting.
    
    Use when request rate exceeds allowed limits.
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: Optional[int] = None,
    ):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after} if retry_after else {},
        )


class ConflictError(APIError):
    """
    Exception for resource conflicts.
    
    Use when operation conflicts with existing state (duplicate, etc.)
    """
    
    def __init__(
        self,
        message: str = "Resource conflict",
        resource: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        details = {}
        if resource:
            details["resource"] = resource
        if reason:
            details["reason"] = reason
        
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details if details else None,
        )
