"""User management service — admin-level CRUD for user accounts."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.user import User
from app.repositories import admin_repository
from app.schemas.admin import (AdminUserListResponse, AdminUserResponse,
                               PaginatedMeta)
from app.services.admin import log_service

logger = logging.getLogger(__name__)


def list_users(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> AdminUserListResponse:
    """Return a paginated, filterable list of users for the admin panel."""
    skip = (page - 1) * per_page
    users, total = admin_repository.get_users(
        db,
        skip=skip,
        limit=per_page,
        search=search,
        role=role,
        is_active=is_active,
    )
    pages = (total + per_page - 1) // per_page

    return AdminUserListResponse(
        users=[AdminUserResponse.model_validate(u) for u in users],
        meta=PaginatedMeta(total=total, page=page, per_page=per_page, pages=pages),
    )


def get_user(db: Session, user_id: UUID) -> AdminUserResponse:
    """Fetch a single user's admin-visible profile."""
    user = admin_repository.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found.")
    return AdminUserResponse.model_validate(user)


def update_user(
    db: Session,
    *,
    admin: User,
    user_id: UUID,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    ip_address: Optional[str] = None,
) -> AdminUserResponse:
    """Update a user's role or active status. Logs the change."""
    if user_id == admin.id:
        raise BadRequestError(
            "Admins cannot modify their own account via this endpoint."
        )

    user = admin_repository.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found.")

    changes: dict = {}
    metadata: dict = {"before": {}, "after": {}}

    if role is not None and role != user.role:
        metadata["before"]["role"] = user.role
        metadata["after"]["role"] = role
        changes["role"] = role

    if is_active is not None and is_active != user.is_active:
        metadata["before"]["is_active"] = user.is_active
        metadata["after"]["is_active"] = is_active
        changes["is_active"] = is_active

    if not changes:
        return AdminUserResponse.model_validate(user)

    updated = admin_repository.update_user(db, user, changes)

    # Determine action label for the audit log
    if "role" in changes and "is_active" in changes:
        action = "update_user"
    elif "role" in changes:
        action = "change_role"
    else:
        action = "disable_account" if not is_active else "enable_account"

    log_service.log_action(
        db,
        admin_id=admin.id,
        action=action,
        entity="user",
        entity_id=str(user_id),
        metadata=metadata,
        ip_address=ip_address,
    )

    logger.info(
        "Admin %s performed '%s' on user %s. Changes: %s",
        admin.id,
        action,
        user_id,
        changes,
    )
    return AdminUserResponse.model_validate(updated)


def delete_user(
    db: Session,
    *,
    admin: User,
    user_id: UUID,
    ip_address: Optional[str] = None,
) -> None:
    """Permanently delete a user and all cascaded data. Logs the deletion."""
    if user_id == admin.id:
        raise BadRequestError(
            "Admins cannot delete their own account via this endpoint."
        )

    user = admin_repository.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found.")

    # Log before deletion so user data is still available
    log_service.log_action(
        db,
        admin_id=admin.id,
        action="delete_account",
        entity="user",
        entity_id=str(user_id),
        metadata={
            "deleted_email": user.email,
            "deleted_name": user.full_name,
        },
        ip_address=ip_address,
    )

    admin_repository.delete_user(db, user)
    logger.info("Admin %s deleted user %s (%s)", admin.id, user_id, user.email)
