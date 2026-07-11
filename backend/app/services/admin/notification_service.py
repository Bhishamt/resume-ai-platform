"""Notification service — create, list, and mark notifications for users."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories import admin_repository
from app.schemas.admin import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    PaginatedMeta,
)

logger = logging.getLogger(__name__)


def list_notifications(
    db: Session,
    *,
    user_id: Optional[UUID] = None,
    is_read: Optional[bool] = None,
    page: int = 1,
    per_page: int = 50,
) -> NotificationListResponse:
    """Return a paginated list of notifications."""
    skip = (page - 1) * per_page
    notifications, total = admin_repository.get_notifications(
        db,
        user_id=user_id,
        is_read=is_read,
        skip=skip,
        limit=per_page,
    )
    pages = (total + per_page - 1) // per_page
    unread_count = admin_repository.get_unread_count(db, user_id) if user_id else 0
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
        meta=PaginatedMeta(total=total, page=page, per_page=per_page, pages=pages),
    )


def create_notification(
    db: Session, *, payload: NotificationCreate
) -> NotificationResponse:
    """Send an in-app notification to a specific user."""
    notif = admin_repository.create_notification(
        db,
        user_id=payload.user_id,
        title=payload.title,
        message=payload.message,
        type=payload.type,
    )
    logger.info(
        "Notification created for user_id=%s title=%r", payload.user_id, payload.title
    )
    return NotificationResponse.model_validate(notif)


def mark_read(
    db: Session, *, notification_id: UUID, user_id: UUID
) -> NotificationResponse:
    """Mark a single notification as read."""
    notifications, _ = admin_repository.get_notifications(
        db, user_id=user_id, skip=0, limit=1000
    )
    target = next((n for n in notifications if n.id == notification_id), None)
    if not target:
        raise NotFoundError(f"Notification {notification_id} not found.")
    updated = admin_repository.mark_notification_read(db, target)
    return NotificationResponse.model_validate(updated)


def mark_all_read(db: Session, *, user_id: UUID) -> int:
    """Mark all notifications for a user as read. Returns count updated."""
    count = admin_repository.mark_all_notifications_read(db, user_id)
    logger.info("Marked %d notifications as read for user_id=%s", count, user_id)
    return count


def broadcast_notification(
    db: Session,
    *,
    title: str,
    message: str,
    type: str = "info",
    admin_id: UUID,
) -> int:
    """Send a notification to ALL active users. Returns count created."""
    from app.models.user import User

    users = db.query(User).filter(User.is_active).all()
    count = 0
    for user in users:
        admin_repository.create_notification(
            db,
            user_id=user.id,
            title=title,
            message=message,
            type=type,
        )
        count += 1
    logger.info(
        "Admin %s broadcast notification to %d users: %r", admin_id, count, title
    )
    return count
