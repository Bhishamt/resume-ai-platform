"""Audit log service — creates and retrieves admin action logs."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import admin_repository
from app.schemas.admin import (AdminLogListResponse, AdminLogResponse,
                               PaginatedMeta)

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    *,
    admin_id: Optional[UUID],
    action: str,
    entity: str,
    entity_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Create an audit log entry. Fails silently so it never breaks business flows."""
    try:
        admin_repository.create_admin_log(
            db,
            admin_id=admin_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata=metadata or {},
            ip_address=ip_address,
        )
    except Exception:
        logger.exception(
            "Failed to write audit log: action=%s entity=%s", action, entity
        )


def get_logs(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 50,
    action: Optional[str] = None,
    entity: Optional[str] = None,
    admin_id: Optional[UUID] = None,
) -> AdminLogListResponse:
    """Return a paginated, filterable list of audit log entries."""
    skip = (page - 1) * per_page
    logs, total = admin_repository.get_admin_logs(
        db,
        skip=skip,
        limit=per_page,
        action=action,
        entity=entity,
        admin_id=admin_id,
    )
    pages = (total + per_page - 1) // per_page
    return AdminLogListResponse(
        logs=[AdminLogResponse.model_validate(log) for log in logs],
        meta=PaginatedMeta(total=total, page=page, per_page=per_page, pages=pages),
    )
