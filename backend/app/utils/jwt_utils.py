"""JWT token utilities for access, refresh, and password reset tokens."""

from datetime import datetime, timedelta, timezone
from typing import Any, Union

import jwt

from app.core.config import settings


def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_password_reset_token(subject: Union[str, Any]) -> str:
    """Create a short-lived token for password reset."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "password_reset",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Returns the payload dict with 'sub' and 'type' keys.
    Raises jwt.ExpiredSignatureError if expired.
    Raises jwt.InvalidTokenError for any other validation failure.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.ALGORITHM],
    )
    return payload
