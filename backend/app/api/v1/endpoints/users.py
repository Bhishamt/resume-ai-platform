"""User profile API endpoints.

GET  /users/profile
PUT  /users/profile
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.user import APIResponse, UserProfileUpdate
from app.services import user_service

router = APIRouter()


@router.get(
    "/profile",
    response_model=APIResponse,
    summary="Get current user profile",
)
def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve the authenticated user's profile."""
    profile = user_service.get_profile(db, current_user.id)
    return APIResponse(
        success=True,
        message="Profile retrieved successfully.",
        data=profile.model_dump(mode="json"),
    )


@router.put(
    "/profile",
    response_model=APIResponse,
    summary="Update current user profile",
)
def update_profile(
    schema: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile."""
    updated = user_service.update_profile(db, current_user.id, schema)
    return APIResponse(
        success=True,
        message="Profile updated successfully.",
        data=updated.model_dump(mode="json"),
    )
