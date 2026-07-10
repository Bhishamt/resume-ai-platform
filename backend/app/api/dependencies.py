"""FastAPI dependencies for database sessions and authentication."""

from typing import Generator
from uuid import UUID

import jwt
from fastapi import Depends, Header

from app.core.exceptions import AuthenticationError
from app.database.session import SessionLocal
from app.models.user import User
from app.repositories import user_repository
from app.utils.jwt_utils import decode_token
from sqlalchemy.orm import Session


def get_db() -> Generator:
    """Yield a database session, ensuring it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT access token.

    Expects header: Authorization: Bearer <token>
    """
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format.")

    token = authorization[7:]  # Strip "Bearer "

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Access token has expired.")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid access token.")

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload.")

    user = user_repository.get_by_id(db, UUID(user_id))
    if not user:
        raise AuthenticationError("User not found.")

    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise AuthenticationError("This account has been deactivated.")
    return current_user


def get_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the requesting user is an active admin.

    Raises:
        AuthorizationError: If the user does not hold the 'admin' role.
    """
    from app.core.exceptions import AuthorizationError  # avoid circular import

    if current_user.role != "admin":
        raise AuthorizationError("Admin privileges required.")
    return current_user
