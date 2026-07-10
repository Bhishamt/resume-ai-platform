"""Repository layer for all admin-panel database queries.

All raw queries are isolated here. Business logic belongs in services.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.admin_log import AdminLog
from app.models.ai_feedback import AIFeedback
from app.models.analysis_report import AnalysisReport
from app.models.job_match import JobMatch
from app.models.notification import Notification
from app.models.resume import Resume
from app.models.system_setting import SystemSetting
from app.models.user import User


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def get_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[User], int]:
    """Return a paginated list of users with optional filters."""
    query = db.query(User)

    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            (func.lower(User.full_name).like(pattern))
            | (func.lower(User.email).like(pattern))
        )
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users, total


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Fetch a single user by UUID."""
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user: User, update_data: dict) -> User:
    """Apply a dict of field changes to a user record."""
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    """Hard-delete a user and cascade their data."""
    db.delete(user)
    db.commit()


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


def count_users(db: Session) -> int:
    return db.query(func.count(User.id)).scalar() or 0


def count_active_users(db: Session) -> int:
    return db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0


def count_new_users_since(db: Session, since: datetime) -> int:
    return (
        db.query(func.count(User.id))
        .filter(User.created_at >= since)
        .scalar()
        or 0
    )


def count_resumes(db: Session) -> int:
    return db.query(func.count(Resume.id)).scalar() or 0


def count_resumes_since(db: Session, since: datetime) -> int:
    return (
        db.query(func.count(Resume.id))
        .filter(Resume.upload_date >= since)
        .scalar()
        or 0
    )


def count_analysis_reports(db: Session) -> int:
    return db.query(func.count(AnalysisReport.id)).scalar() or 0


def count_job_matches(db: Session) -> int:
    return db.query(func.count(JobMatch.id)).scalar() or 0


def count_ai_requests(db: Session) -> int:
    return db.query(func.count(AIFeedback.id)).scalar() or 0


def count_ai_requests_since(db: Session, since: datetime) -> int:
    return (
        db.query(func.count(AIFeedback.id))
        .filter(AIFeedback.created_at >= since)
        .scalar()
        or 0
    )


def get_total_tokens_used(db: Session) -> int:
    """Sum all token_usage['total_tokens'] fields from ai_feedback."""
    rows = db.query(AIFeedback.token_usage).all()
    total = 0
    for (usage,) in rows:
        if isinstance(usage, dict):
            total += usage.get("total_tokens", 0)
    return total


def get_avg_response_time(db: Session) -> float:
    result = db.query(func.avg(AIFeedback.response_time)).scalar()
    return round(float(result), 3) if result else 0.0


def get_ai_provider_stats(db: Session) -> List[dict]:
    """Count AI requests grouped by provider."""
    rows = (
        db.query(AIFeedback.provider, func.count(AIFeedback.id).label("count"))
        .group_by(AIFeedback.provider)
        .all()
    )
    return [{"provider": r.provider, "count": r.count} for r in rows]


def get_resumes_by_day(db: Session, days: int = 30) -> List[dict]:
    """Daily resume upload counts for the last N days."""
    rows = (
        db.query(
            func.date_trunc("day", Resume.upload_date).label("day"),
            func.count(Resume.id).label("count"),
        )
        .filter(
            Resume.upload_date
            >= func.now() - func.cast(f"{days} days", type_=func.now().type)
        )
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [{"day": str(r.day)[:10], "count": r.count} for r in rows]


def get_users_by_day(db: Session, days: int = 30) -> List[dict]:
    """Daily new user registrations for the last N days."""
    rows = (
        db.query(
            func.date_trunc("day", User.created_at).label("day"),
            func.count(User.id).label("count"),
        )
        .filter(
            User.created_at
            >= func.now() - func.cast(f"{days} days", type_=func.now().type)
        )
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [{"day": str(r.day)[:10], "count": r.count} for r in rows]


def get_ats_score_distribution(db: Session) -> List[dict]:
    """Count analysis reports bucketed into ATS score ranges."""
    rows = db.query(AnalysisReport.ats_score).all()
    buckets = {
        "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0,
    }
    for (score,) in rows:
        if score is None:
            continue
        if score <= 20:
            buckets["0-20"] += 1
        elif score <= 40:
            buckets["21-40"] += 1
        elif score <= 60:
            buckets["41-60"] += 1
        elif score <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1
    return [{"range": k, "count": v} for k, v in buckets.items()]


def get_resumes_for_admin(
    db: Session, *, skip: int = 0, limit: int = 20
) -> Tuple[List[Resume], int]:
    """Return paginated resumes with user info for admin view."""
    query = db.query(Resume)
    total = query.count()
    resumes = query.order_by(Resume.upload_date.desc()).offset(skip).limit(limit).all()
    return resumes, total


# ---------------------------------------------------------------------------
# Admin Logs
# ---------------------------------------------------------------------------


def create_admin_log(
    db: Session,
    *,
    admin_id: Optional[UUID],
    action: str,
    entity: str,
    entity_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AdminLog:
    """Insert a new audit log entry."""
    log = AdminLog(
        admin_id=admin_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        log_metadata=metadata or {},
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_admin_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    entity: Optional[str] = None,
    admin_id: Optional[UUID] = None,
) -> Tuple[List[AdminLog], int]:
    """Return paginated audit logs with optional filters."""
    query = db.query(AdminLog)
    if action:
        query = query.filter(AdminLog.action == action)
    if entity:
        query = query.filter(AdminLog.entity == entity)
    if admin_id:
        query = query.filter(AdminLog.admin_id == admin_id)
    total = query.count()
    logs = (
        query.order_by(AdminLog.created_at.desc()).offset(skip).limit(limit).all()
    )
    return logs, total


# ---------------------------------------------------------------------------
# System Settings
# ---------------------------------------------------------------------------


def get_all_settings(db: Session) -> List[SystemSetting]:
    return db.query(SystemSetting).order_by(SystemSetting.key).all()


def get_setting(db: Session, key: str) -> Optional[SystemSetting]:
    return db.query(SystemSetting).filter(SystemSetting.key == key).first()


def upsert_setting(
    db: Session,
    *,
    key: str,
    value: str,
    description: Optional[str] = None,
    updated_by: Optional[UUID] = None,
) -> SystemSetting:
    """Create or update a system setting by key."""
    setting = get_setting(db, key)
    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
        setting.updated_by = updated_by
        setting.updated_at = datetime.now(timezone.utc)
    else:
        setting = SystemSetting(
            key=key,
            value=value,
            description=description,
            updated_by=updated_by,
        )
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


def get_notifications(
    db: Session,
    *,
    user_id: Optional[UUID] = None,
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[Notification], int]:
    query = db.query(Notification)
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    total = query.count()
    notifications = (
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    )
    return notifications, total


def create_notification(
    db: Session,
    *,
    user_id: UUID,
    title: str,
    message: str,
    type: str = "info",
) -> Notification:
    notif = Notification(user_id=user_id, title=title, message=message, type=type)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def mark_notification_read(
    db: Session, notification: Notification
) -> Notification:
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_notifications_read(db: Session, user_id: UUID) -> int:
    """Mark all unread notifications for a user as read. Returns updated count."""
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .update({"is_read": True})
    )
    db.commit()
    return count


def get_unread_count(db: Session, user_id: UUID) -> int:
    return (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .scalar()
        or 0
    )
