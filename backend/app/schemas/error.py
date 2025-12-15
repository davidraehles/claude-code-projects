"""
Error response schemas for standardized API error handling.

Provides consistent error response format with correlation IDs
and categorization for better error tracking and debugging.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """
    Error type categorization for consistent error handling.

    Categories:
        VALIDATION: Request validation errors (400)
        AUTHENTICATION: Authentication failures (401)
        AUTHORIZATION: Permission/authorization errors (403)
        NOT_FOUND: Resource not found errors (404)
        CONFLICT: Resource conflict errors (409)
        SERVER: Internal server errors (500)
        SERVICE_UNAVAILABLE: Service/dependency unavailable (503)
    """

    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    SERVER = "server"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT = "rate_limit"


class ErrorResponse(BaseModel):
    """
    Standardized error response model.

    Provides consistent error structure across all API endpoints
    with correlation IDs for distributed tracing.
    """

    error_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique error identifier for correlation",
    )
    error_type: ErrorType = Field(
        description="Error category for classification"
    )
    message: str = Field(
        description="Human-readable error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details and context",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error occurrence timestamp",
    )
    path: str = Field(
        description="Request path where error occurred"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for distributed tracing",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error_id": "550e8400-e29b-41d4-a716-446655440000",
                "error_type": "validation",
                "message": "Invalid input data",
                "details": {
                    "field": "email",
                    "issue": "Invalid email format"
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "path": "/api/v1/users",
                "request_id": "req-123456"
            }
        }


# Custom exception classes for common error scenarios
class AppException(Exception):
    """
    Base application exception with error categorization.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize application exception.

        Args:
            message: Human-readable error message
            error_type: Error category
            status_code: HTTP status code
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details


class ValidationException(AppException):
    """Exception for request validation errors (400)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION,
            status_code=400,
            details=details,
        )


class AuthenticationException(AppException):
    """Exception for authentication failures (401)."""

    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHENTICATION,
            status_code=401,
            details=details,
        )


class AuthorizationException(AppException):
    """Exception for authorization/permission errors (403)."""

    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHORIZATION,
            status_code=403,
            details=details,
        )


class NotFoundException(AppException):
    """Exception for resource not found errors (404)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.NOT_FOUND,
            status_code=404,
            details=details,
        )


class ConflictException(AppException):
    """Exception for resource conflict errors (409)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.CONFLICT,
            status_code=409,
            details=details,
        )


class ServerException(AppException):
    """Exception for internal server errors (500)."""

    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.SERVER,
            status_code=500,
            details=details,
        )


class ServiceUnavailableException(AppException):
    """Exception for service/dependency unavailable errors (503)."""

    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.SERVICE_UNAVAILABLE,
            status_code=503,
            details=details,
        )
