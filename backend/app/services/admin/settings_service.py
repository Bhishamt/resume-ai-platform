"""Settings service — read and write system-wide platform configuration."""

import logging
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import admin_repository
from app.schemas.admin import BulkSettingsUpdate, SettingResponse, SettingsListResponse
from app.services.admin import log_service

logger = logging.getLogger(__name__)


def get_all(db: Session) -> SettingsListResponse:
    """Return all system settings ordered by key."""
    settings = admin_repository.get_all_settings(db)
    return SettingsListResponse(
        settings=[SettingResponse.model_validate(s) for s in settings]
    )


def bulk_update(
    db: Session,
    *,
    admin_id: UUID,
    payload: BulkSettingsUpdate,
    ip_address: str | None = None,
) -> SettingsListResponse:
    """Upsert a batch of settings and log each change."""
    before_snapshot: dict = {}
    after_snapshot: dict = {}

    for item in payload.settings:
        existing = admin_repository.get_setting(db, item.key)
        before_snapshot[item.key] = existing.value if existing else None
        after_snapshot[item.key] = item.value

        admin_repository.upsert_setting(
            db,
            key=item.key,
            value=item.value,
            description=item.description,
            updated_by=admin_id,
        )

    log_service.log_action(
        db,
        admin_id=admin_id,
        action="update_settings",
        entity="system_setting",
        metadata={"before": before_snapshot, "after": after_snapshot},
        ip_address=ip_address,
    )

    logger.info("Admin %s updated %d setting(s).", admin_id, len(payload.settings))
    return get_all(db)
