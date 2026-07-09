"""Authentication service — all auth business logic lives here.

Routes delegate to this service. This service calls repositories for data access.
"""

import logging
from uuid import UUID

import jwt
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
)
from app.core.security import hash_password, validate_password_strength, verify_password
from app.repositories import user_repository
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.utils.jwt_utils import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
)

logger = logging.getLogger(__name__)


def register(db: Session, schema: UserRegister) -> UserResponse:
    """Register a new user account."""
    existing = user_repository.get_by_email(db, schema.email)
    if existing:
        raise ConflictError("A user with this email already exists.")

    hashed = hash_password(schema.password)

    user = user_repository.create(
        db,
        full_name=schema.full_name,
        email=schema.email,
        password_hash=hashed,
    )
    logger.info("User registered: %s", user.email)
    return UserResponse.model_validate(user)


def login(db: Session, schema: UserLogin) -> TokenResponse:
    """Authenticate a user and return JWT tokens."""
    user = user_repository.get_by_email(db, schema.email)

    if not user or not verify_password(schema.password, user.password_hash):
        logger.warning("Failed login attempt for email: %s", schema.email)
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    user_repository.update_last_login(db, user)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    logger.info("User logged in: %s", user.email)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


def refresh_token(db: Session, refresh_token_str: str) -> TokenResponse:
    """Validate a refresh token and issue new token pair."""
    try:
        payload = decode_token(refresh_token_str)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Refresh token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid refresh token.")

    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid token type.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload.")

    user = user_repository.get_by_id(db, UUID(user_id))
    if not user:
        raise AuthenticationError("User not found.")

    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


def forgot_password(db: Session, schema: ForgotPasswordRequest) -> str:
    """Generate a password reset token.

    Always returns a success message to prevent email enumeration.
    In production, this would send an email. For Phase 3, the token is logged.
    """
    user = user_repository.get_by_email(db, schema.email)

    if user:
        reset_token = create_password_reset_token(subject=str(user.id))
        # In production, send this via email (SMTP/SendGrid)
        logger.info(
            "Password reset token generated for %s: %s",
            user.email,
            reset_token,
        )

    return "If an account with that email exists, a password reset link has been sent."


def reset_password(db: Session, schema: ResetPasswordRequest) -> str:
    """Reset a user's password using a valid reset token."""
    try:
        payload = decode_token(schema.token)
    except jwt.ExpiredSignatureError:
        raise BadRequestError("Password reset token has expired.")
    except jwt.InvalidTokenError:
        raise BadRequestError("Invalid password reset token.")

    if payload.get("type") != "password_reset":
        raise BadRequestError("Invalid token type.")

    user_id = payload.get("sub")
    if not user_id:
        raise BadRequestError("Invalid token payload.")

    user = user_repository.get_by_id(db, UUID(user_id))
    if not user:
        raise BadRequestError("Invalid password reset token.")

    try:
        validate_password_strength(schema.new_password)
    except ValueError as e:
        raise BadRequestError(str(e))

    new_hash = hash_password(schema.new_password)
    user_repository.update(db, user, {"password_hash": new_hash})

    logger.info("Password reset successful for user: %s", user.email)
    return "Password has been reset successfully."
