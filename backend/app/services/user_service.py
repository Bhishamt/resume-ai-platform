"""User service — profile management business logic."""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories import user_repository
from app.schemas.user import UserProfileUpdate, UserResponse

logger = logging.getLogger(__name__)


def get_profile(db: Session, user_id: UUID) -> UserResponse:
    """Retrieve a user's profile by ID."""
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found.")
    return UserResponse.model_validate(user)


def update_profile(
    db: Session, user_id: UUID, update_data: UserProfileUpdate
) -> UserResponse:
    """Update a user's profile fields."""
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found.")

    changes = update_data.model_dump(exclude_unset=True)
    if not changes:
        return UserResponse.model_validate(user)

    updated_user = user_repository.update(db, user, changes)
    logger.info("Profile updated for user: %s", updated_user.email)
    return UserResponse.model_validate(updated_user)
