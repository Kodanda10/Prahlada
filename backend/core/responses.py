"""
Standardized response helpers for the backend API.

Provides consistent response formatting across all endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Model for error detail information."""
    
    field: Optional[str] = None
    reason: Optional[str] = None
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Standardized error response model.
    
    All API errors should return this format.
    """
    
    status: str = "error"
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Invalid request payload",
                "code": "VALIDATION_ERROR",
                "details": {
                    "field": "email",
                    "reason": "must be a valid email address"
                }
            }
        }


class SuccessResponse(BaseModel):
    """
    Standardized success response model.
    
    Use for simple success messages without complex data.
    """
    
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {"id": "12345"}
            }
        }


class PaginatedResponse(BaseModel):
    """
    Standardized paginated response model.
    
    Use for list endpoints that support pagination.
    """
    
    status: str = "success"
    data: List[Any]
    total: int
    page: int = 1
    page_size: int = 10
    has_more: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": [],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "has_more": True
            }
        }


def error_response(
    message: str,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    
    Args:
        message: Human-readable error message
        code: Error code for programmatic handling
        details: Additional error details
        
    Returns:
        Dictionary suitable for JSON response
        
    Example:
        >>> error_response("User not found", "NOT_FOUND", {"user_id": "123"})
        {"status": "error", "message": "User not found", "code": "NOT_FOUND", "details": {"user_id": "123"}}
    """
    response = {
        "status": "error",
        "message": message,
    }
    if code:
        response["code"] = code
    if details:
        response["details"] = details
    return response


def success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized success response dictionary.
    
    Args:
        message: Human-readable success message
        data: Optional data payload
        
    Returns:
        Dictionary suitable for JSON response
        
    Example:
        >>> success_response("Tweet ingested", {"tweet_id": "123"})
        {"status": "success", "message": "Tweet ingested", "data": {"tweet_id": "123"}}
    """
    response = {
        "status": "success",
        "message": message,
    }
    if data:
        response["data"] = data
    return response


def paginated_response(
    data: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """
    Create a standardized paginated response dictionary.
    
    Args:
        data: List of items for current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary suitable for JSON response
    """
    return {
        "status": "success",
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": (page * page_size) < total,
    }


def validation_error_response(
    field: str,
    reason: str,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a validation error response for a specific field.
    
    Args:
        field: Name of the invalid field
        reason: Why the validation failed
        message: Optional custom message (defaults to generic)
        
    Returns:
        Dictionary suitable for JSON response
    """
    return error_response(
        message=message or f"Validation failed for field '{field}'",
        code="VALIDATION_ERROR",
        details={"field": field, "reason": reason},
    )
