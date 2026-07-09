"""Custom exception classes and FastAPI exception handlers.

Returns consistent API responses without exposing internal details.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: list[str] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(AppException):
    """Raised when user lacks permissions."""

    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(AppException):
    """Raised on resource conflict (e.g., duplicate email)."""

    def __init__(self, message: str = "Resource already exists."):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class NotFoundError(AppException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found."):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class BadRequestError(AppException):
    """Raised for invalid request data."""

    def __init__(self, message: str = "Invalid request.", errors: list[str] | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors,
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


def _error_response(status_code: int, message: str, errors: list[Any] | None = None) -> JSONResponse:
    """Build a consistent error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": errors or [],
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException: %s (status=%d)", exc.message, exc.status_code)
        return _error_response(exc.status_code, exc.message, exc.errors)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        error_messages = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            error_messages.append(f"{field}: {msg}")
        logger.warning("Validation error: %s", error_messages)
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation failed.",
            error_messages,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", str(exc))
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An internal server error occurred.",
        )
