"""
Global exception classes and handlers.
Provides consistent error responses across the application.
"""
from typing import Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An error occurred",
        headers: dict[str, str] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(AppException):
    """Conflict exception (e.g., duplicate resource)."""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(AppException):
    """Validation exception with Laravel-compatible errors format."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: dict[str, list[str]] | None = None,
        detail: str | None = None,
    ):
        # Use message as detail for compatibility with parent class
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
        self.message = message
        self.errors = errors or {}


class PaymentException(AppException):
    """Payment processing exception."""

    def __init__(self, detail: str = "Payment processing failed"):
        super().__init__(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)


class BookingException(AppException):
    """Booking-related exception."""

    def __init__(self, detail: str = "Booking error", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotImplementedException(AppException):
    """Feature not yet implemented exception."""

    def __init__(self, detail: str = "Feature not yet implemented"):
        super().__init__(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=detail)


# Exception Handlers


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions."""
    # Special handling for ValidationException to include errors field
    if isinstance(exc, ValidationException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "errors": exc.errors,
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors - Laravel compatible format."""
    # Build Laravel-style errors dict: {field: [messages]}
    errors_dict = {}
    first_error_message = None

    for error in exc.errors():
        # Get field name (skip 'body' prefix if present)
        field_parts = [str(loc) for loc in error["loc"] if loc != "body"]
        field_name = field_parts[0] if field_parts else "field"

        # Format error message to be user-friendly
        error_msg = error["msg"]

        # Customize messages for common validation errors
        if error["type"] == "value_error.email":
            error_msg = f"The {field_name} must be a valid email address."
        elif error["type"] == "value_error.missing":
            error_msg = f"The {field_name} field is required."
        elif error["type"] == "string_too_short":
            error_msg = f"The {field_name} must be at least {error.get('ctx', {}).get('limit_value', 8)} characters."
        elif error["type"] == "string_pattern_mismatch":
            error_msg = f"The {field_name} format is invalid."
        elif "Passwords do not match" in error_msg or "password confirmation" in error_msg.lower():
            error_msg = "The password confirmation does not match."

        # Add to errors dict
        if field_name not in errors_dict:
            errors_dict[field_name] = []
        errors_dict[field_name].append(error_msg)

        # Store first error for main message
        if first_error_message is None:
            first_error_message = error_msg

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": first_error_message or "Validation error",
            "errors": errors_dict,
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": True,
            "message": "Database constraint violation",
            "detail": str(exc.orig) if hasattr(exc, "orig") else str(exc),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    # Safely access debug setting (might not exist in SQLAdmin context)
    debug = getattr(getattr(request.app.state, 'settings', None), 'debug', True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc) if debug else None,
        },
    )
