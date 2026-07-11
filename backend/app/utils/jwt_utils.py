"""JWT token utilities — access, refresh, password reset, and blacklist support.

Phase 10: Added `jti` (JWT ID) claim to all tokens for Redis-based revocation.
Logout blacklists the token's jti in Redis until its natural expiry time.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Union

import jwt

from app.core.config import settings


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token with a unique jti for blacklist support."""
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
        "jti": str(uuid.uuid4()),  # Unique token ID for blacklisting
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry and unique jti."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_password_reset_token(subject: Union[str, Any]) -> str:
    """Create a short-lived token for password reset (no jti — single-use by design)."""
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

    Returns the payload dict with 'sub', 'type', and 'jti' keys.
    Raises jwt.ExpiredSignatureError if expired.
    Raises jwt.InvalidTokenError for any other validation failure.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.ALGORITHM],
    )
    return payload


async def revoke_token(token: str) -> bool:
    """Blacklist a JWT token in Redis until its natural expiry.

    Used by the logout endpoint to immediately invalidate a token.
    Returns True if successfully blacklisted, False on error.
    """
    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        if not jti:
            # Legacy token without jti — can't blacklist individually
            return False

        exp = payload.get("exp", 0)
        now = datetime.now(timezone.utc).timestamp()
        remaining_seconds = max(int(exp - now), 0)

        if remaining_seconds == 0:
            # Already expired — no need to blacklist
            return True

        from app.core.redis_client import blacklist_token

        return await blacklist_token(jti, remaining_seconds + 60)  # +60s grace period

    except Exception:
        return False


async def is_token_revoked(payload: dict) -> bool:
    """Check if a decoded token payload has been revoked (blacklisted).

    Called by the auth dependency on every protected request.
    Returns False (not revoked) if Redis is unavailable — fail-open design.
    """
    jti = payload.get("jti")
    if not jti:
        return False  # Legacy tokens without jti are not revocable

    from app.core.redis_client import is_token_blacklisted

    return await is_token_blacklisted(jti)
