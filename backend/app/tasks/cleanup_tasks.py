"""Periodic maintenance / cleanup Celery tasks.

Scheduled via Celery Beat to run at off-peak hours.
These keep the system healthy without manual intervention.
"""

import logging
from pathlib import Path

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_expired_tokens",
    queue="cleanup",
)
def cleanup_expired_tokens() -> dict:
    """Purge expired JWT blacklist entries from Redis.

    Redis TTLs handle expiry automatically; this task is a safety net
    to log the current blacklist size for observability.
    """
    import asyncio

    async def _count_blacklisted():
        from app.core.redis_client import get_redis

        client = get_redis()
        keys = await client.keys("jwt:blacklist:*")
        return len(keys)

    loop = asyncio.new_event_loop()
    try:
        count = loop.run_until_complete(_count_blacklisted())
        logger.info(
            "cleanup_expired_tokens: %d blacklisted tokens in Redis (TTL-managed)",
            count,
        )
        return {"status": "ok", "blacklisted_tokens": count}
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_orphaned_files",
    queue="cleanup",
)
def cleanup_orphaned_files() -> dict:
    """Delete uploaded files that have no corresponding Resume DB record.

    Protects against disk bloat from failed uploads or manual DB deletions.
    """
    from app.database.base import SessionLocal
    from app.models.resume import Resume

    logger.info("cleanup_orphaned_files: starting scan")

    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    if not upload_dir.exists():
        return {"status": "ok", "deleted": 0, "scanned": 0}

    db = SessionLocal()
    deleted = 0
    scanned = 0

    try:
        # Collect all storage paths known to the DB
        known_paths = {row[0] for row in db.query(Resume.storage_path).all() if row[0]}

        # Walk all files in the upload directory
        for user_dir in upload_dir.iterdir():
            if not user_dir.is_dir():
                continue
            for file_path in user_dir.iterdir():
                if not file_path.is_file():
                    continue
                scanned += 1
                if str(file_path) not in known_paths:
                    try:
                        file_path.unlink()
                        deleted += 1
                        logger.info("Deleted orphaned file: %s", file_path)
                    except OSError as e:
                        logger.warning(
                            "Could not delete orphaned file %s: %s", file_path, e
                        )

        logger.info("cleanup_orphaned_files: scanned=%d deleted=%d", scanned, deleted)
        return {"status": "ok", "scanned": scanned, "deleted": deleted}

    finally:
        db.close()


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_old_cache",
    queue="cleanup",
)
def cleanup_old_cache() -> dict:
    """Flush dashboard and API cache keys older than their TTL.

    Normally Redis TTLs handle this automatically.
    This task logs cache key counts for monitoring purposes.
    """
    import asyncio

    async def _scan_cache():
        from app.core.redis_client import get_redis

        client = get_redis()
        cache_keys = await client.keys("cache:*")
        return len(cache_keys)

    loop = asyncio.new_event_loop()
    try:
        count = loop.run_until_complete(_scan_cache())
        logger.info("cleanup_old_cache: %d cache keys active", count)
        return {"status": "ok", "cache_keys": count}
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.cleanup_tasks.trigger_weekly_summaries",
    queue="cleanup",
)
def trigger_weekly_summaries() -> dict:
    """Fan-out weekly career summary emails to all active users.

    Queries active users and dispatches individual email tasks.
    """
    from app.database.base import SessionLocal
    from app.models.user import User
    from app.tasks.notification_tasks import send_weekly_summary_task

    logger.info("trigger_weekly_summaries: building recipient list")

    db = SessionLocal()
    dispatched = 0
    try:
        active_users = db.query(User).filter(User.is_active == True).all()  # noqa: E712

        for user in active_users:
            # Build lightweight summary data — real implementation pulls
            # actual stats from the DB; here we pass user context.
            summary_data = {
                "user_id": str(user.id),
                "period": "last_7_days",
            }
            send_weekly_summary_task.apply_async(
                kwargs={
                    "user_email": user.email,
                    "full_name": user.full_name,
                    "summary_data": summary_data,
                }
            )
            dispatched += 1

        logger.info("trigger_weekly_summaries: dispatched %d emails", dispatched)
        return {"status": "ok", "dispatched": dispatched}

    finally:
        db.close()
