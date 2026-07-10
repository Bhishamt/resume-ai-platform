"""Core admin service — orchestration and RBAC validation.

All admin operations must route through this service, which enforces
that the requesting user holds the 'admin' role before delegating work
to the specialised sub-services.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.user import User
from app.repositories import admin_repository

logger = logging.getLogger(__name__)


def require_admin(user: User) -> None:
    """Raise AuthorizationError if the user is not an admin.

    This is a guard that can be called from any service to enforce RBAC
    without duplicating the role-check logic.
    """
    if user.role != "admin":
        logger.warning(
            "Non-admin access attempt by user_id=%s email=%s",
            user.id,
            user.email,
        )
        raise AuthorizationError("Admin privileges required.")


def get_user_or_404(db: Session, user_id: UUID) -> User:
    """Fetch a user by UUID or raise NotFoundError."""
    user = admin_repository.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found.")
    return user


def get_client_ip(request: Request) -> Optional[str]:
    """Extract the real client IP, honouring X-Forwarded-For headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None
