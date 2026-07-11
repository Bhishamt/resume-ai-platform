"""Admin API endpoints — Phase 9: Enterprise Admin Panel.

All routes under /api/v1/admin/* require the 'admin' role.
RBAC is enforced at the dependency level via get_admin_user().

Routes:
    GET    /admin/dashboard         — platform stats overview
    GET    /admin/analytics         — full analytics + chart data
    GET    /admin/users             — paginated user list
    GET    /admin/users/{id}        — single user detail
    PUT    /admin/users/{id}        — update user role/status
    DELETE /admin/users/{id}        — delete user account
    GET    /admin/resumes           — paginated resume list
    DELETE /admin/resumes/{id}      — delete corrupted resume
    GET    /admin/ai-monitoring     — AI usage statistics
    GET    /admin/logs              — paginated audit log
    GET    /admin/settings          — all system settings
    PUT    /admin/settings          — bulk update settings
    GET    /admin/system            — system health metrics
    GET    /admin/notifications     — admin notification centre
    POST   /admin/notifications     — create / broadcast notification
"""

import logging
import os
import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_admin_user, get_db
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories import admin_repository
from app.schemas.admin import (AdminResumeListResponse, AdminResumeResponse,
                               AdminUserUpdate, AIMonitoringResponse,
                               BulkSettingsUpdate, NotificationCreate,
                               PaginatedMeta, SystemHealthResponse)
from app.schemas.user import APIResponse
from app.services.admin import (analytics_service, log_service,
                                notification_service, settings_service,
                                user_management)
from app.services.admin.admin_service import get_client_ip

logger = logging.getLogger(__name__)
router = APIRouter()

# Track application start time for uptime metric
_APP_START_TIME = time.time()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@router.get(
    "/dashboard",
    response_model=APIResponse,
    summary="Admin dashboard stats",
)
def get_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return high-level platform statistics for the admin dashboard."""
    stats = analytics_service.get_dashboard_stats(db)
    return APIResponse(
        success=True,
        message="Dashboard stats retrieved.",
        data=stats.model_dump(),
    )


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


@router.get(
    "/analytics",
    response_model=APIResponse,
    summary="Full platform analytics",
)
def get_analytics(
    days: int = Query(default=30, ge=7, le=90, description="Rolling window in days"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return full analytics payload including chart data for the admin panel."""
    data = analytics_service.get_analytics(db, days=days)
    return APIResponse(
        success=True,
        message="Analytics retrieved.",
        data=data.model_dump(),
    )


# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------


@router.get(
    "/users",
    response_model=APIResponse,
    summary="List all users (admin)",
)
def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, max_length=255),
    role: Optional[str] = Query(default=None, pattern="^(user|admin)$"),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Paginated, searchable, filterable list of all users."""
    result = user_management.list_users(
        db,
        page=page,
        per_page=per_page,
        search=search,
        role=role,
        is_active=is_active,
    )
    return APIResponse(
        success=True,
        message="Users retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.get(
    "/users/{user_id}",
    response_model=APIResponse,
    summary="Get user detail (admin)",
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Retrieve the admin-visible profile for a specific user."""
    result = user_management.get_user(db, user_id)
    return APIResponse(
        success=True,
        message="User retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.put(
    "/users/{user_id}",
    response_model=APIResponse,
    summary="Update user role or status (admin)",
)
def update_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Update a user's role and/or active status. Change is audit-logged."""
    result = user_management.update_user(
        db,
        admin=admin,
        user_id=user_id,
        role=payload.role,
        is_active=payload.is_active,
        ip_address=get_client_ip(request),
    )
    return APIResponse(
        success=True,
        message="User updated.",
        data=result.model_dump(mode="json"),
    )


@router.delete(
    "/users/{user_id}",
    response_model=APIResponse,
    summary="Delete user account (admin)",
)
def delete_user(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Permanently delete a user and all their data. Action is audit-logged."""
    user_management.delete_user(
        db,
        admin=admin,
        user_id=user_id,
        ip_address=get_client_ip(request),
    )
    return APIResponse(
        success=True,
        message="User deleted successfully.",
    )


# ---------------------------------------------------------------------------
# Resume Management
# ---------------------------------------------------------------------------


@router.get(
    "/resumes",
    response_model=APIResponse,
    summary="List all resumes (admin)",
)
def list_resumes(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return a paginated list of all uploaded resumes."""
    skip = (page - 1) * per_page
    resumes, total = admin_repository.get_resumes_for_admin(
        db, skip=skip, limit=per_page
    )
    pages = (total + per_page - 1) // per_page
    result = AdminResumeListResponse(
        resumes=[AdminResumeResponse.model_validate(r) for r in resumes],
        meta=PaginatedMeta(total=total, page=page, per_page=per_page, pages=pages),
    )
    return APIResponse(
        success=True,
        message="Resumes retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.delete(
    "/resumes/{resume_id}",
    response_model=APIResponse,
    summary="Delete a corrupted resume (admin)",
)
def delete_resume(
    resume_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Delete a specific resume record and its stored file."""
    from app.models.resume import Resume

    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise NotFoundError(f"Resume {resume_id} not found.")

    log_service.log_action(
        db,
        admin_id=admin.id,
        action="delete_resume",
        entity="resume",
        entity_id=str(resume_id),
        metadata={"filename": resume.original_filename, "user_id": str(resume.user_id)},
        ip_address=get_client_ip(request),
    )

    # Remove from disk if it exists
    try:
        if os.path.exists(resume.storage_path):
            os.remove(resume.storage_path)
    except OSError:
        logger.warning("Could not remove file at %s", resume.storage_path)

    db.delete(resume)
    db.commit()
    return APIResponse(success=True, message="Resume deleted.")


# ---------------------------------------------------------------------------
# AI Monitoring
# ---------------------------------------------------------------------------


@router.get(
    "/ai-monitoring",
    response_model=APIResponse,
    summary="AI usage monitoring (admin)",
)
def get_ai_monitoring(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return AI provider statistics and token usage metrics."""
    from datetime import datetime, timezone

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Token usage today — compute inline to avoid extra DB round-trips
    from app.models.ai_feedback import AIFeedback

    rows_today = (
        db.query(AIFeedback.token_usage)
        .filter(AIFeedback.created_at >= today_start)
        .all()
    )
    tokens_today = sum((r[0] or {}).get("total_tokens", 0) for r in rows_today)

    result = AIMonitoringResponse(
        total_requests=admin_repository.count_ai_requests(db),
        total_tokens=admin_repository.get_total_tokens_used(db),
        avg_response_time_ms=admin_repository.get_avg_response_time(db) * 1000,
        provider_stats=[
            _ProviderStat(provider=r["provider"], count=r["count"])
            for r in admin_repository.get_ai_provider_stats(db)
        ],
        requests_today=admin_repository.count_ai_requests_since(db, today_start),
        tokens_today=tokens_today,
    )
    return APIResponse(
        success=True,
        message="AI monitoring data retrieved.",
        data=result.model_dump(),
    )


# Local import alias to avoid circular
from app.schemas.admin import ProviderStat as _ProviderStat  # noqa: E402

# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------


@router.get(
    "/logs",
    response_model=APIResponse,
    summary="Audit log (admin)",
)
def get_logs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    action: Optional[str] = Query(default=None),
    entity: Optional[str] = Query(default=None),
    admin_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return a paginated, filterable audit log."""
    result = log_service.get_logs(
        db,
        page=page,
        per_page=per_page,
        action=action,
        entity=entity,
        admin_id=admin_id,
    )
    return APIResponse(
        success=True,
        message="Audit logs retrieved.",
        data=result.model_dump(mode="json"),
    )


# ---------------------------------------------------------------------------
# System Settings
# ---------------------------------------------------------------------------


@router.get(
    "/settings",
    response_model=APIResponse,
    summary="Get all system settings (admin)",
)
def get_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Retrieve all platform configuration settings."""
    result = settings_service.get_all(db)
    return APIResponse(
        success=True,
        message="Settings retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.put(
    "/settings",
    response_model=APIResponse,
    summary="Bulk update system settings (admin)",
)
def update_settings(
    payload: BulkSettingsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Upsert one or more system settings. Changes are audit-logged."""
    result = settings_service.bulk_update(
        db,
        admin_id=admin.id,
        payload=payload,
        ip_address=get_client_ip(request),
    )
    return APIResponse(
        success=True,
        message="Settings updated.",
        data=result.model_dump(mode="json"),
    )


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------


@router.get(
    "/system",
    response_model=APIResponse,
    summary="System health metrics (admin)",
)
def get_system_health(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return live system health metrics (CPU, memory, disk, DB, AI provider)."""

    # --- Database probe ---
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "degraded"

    # --- AI provider probe (simple reachability) ---
    try:
        from app.core.config import settings as cfg

        ai_status = "healthy" if cfg.GROQ_API_KEY else "unconfigured"
    except Exception:
        ai_status = "unknown"

    # --- psutil metrics (graceful fallback if not installed) ---
    try:
        import psutil

        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage("/")
        memory_used_mb = round(mem.used / 1024 / 1024, 1)
        memory_total_mb = round(mem.total / 1024 / 1024, 1)
        memory_percent = round(mem.percent, 1)
        cpu_percent = round(cpu, 1)
        disk_used_gb = round(disk.used / 1024 / 1024 / 1024, 2)
        disk_total_gb = round(disk.total / 1024 / 1024 / 1024, 2)
        disk_percent = round(disk.percent, 1)
    except ImportError:
        memory_used_mb = memory_total_mb = memory_percent = 0.0
        cpu_percent = 0.0
        disk_used_gb = disk_total_gb = disk_percent = 0.0

    # --- Storage (uploads dir) ---
    try:
        from app.core.config import settings as cfg

        upload_dir = cfg.UPLOAD_DIR
        storage_used = sum(
            os.path.getsize(os.path.join(dirpath, f))
            for dirpath, _, files in os.walk(upload_dir)
            for f in files
        )
    except Exception:
        storage_used = 0

    health = SystemHealthResponse(
        api_status="healthy",
        database_status=db_status,
        storage_used_bytes=storage_used,
        storage_used_mb=round(storage_used / 1024 / 1024, 2),
        uptime_seconds=round(time.time() - _APP_START_TIME, 1),
        memory_used_mb=memory_used_mb,
        memory_total_mb=memory_total_mb,
        memory_percent=memory_percent,
        cpu_percent=cpu_percent,
        disk_used_gb=disk_used_gb,
        disk_total_gb=disk_total_gb,
        disk_percent=disk_percent,
        ai_provider_status=ai_status,
    )
    return APIResponse(
        success=True,
        message="System health retrieved.",
        data=health.model_dump(),
    )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


@router.get(
    "/notifications",
    response_model=APIResponse,
    summary="Admin notifications",
)
def get_notifications(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    is_read: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Return the admin's own notification feed."""
    result = notification_service.list_notifications(
        db,
        user_id=admin.id,
        is_read=is_read,
        page=page,
        per_page=per_page,
    )
    return APIResponse(
        success=True,
        message="Notifications retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.post(
    "/notifications",
    response_model=APIResponse,
    summary="Create or broadcast notification (admin)",
)
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Create a notification for a specific user."""
    result = notification_service.create_notification(db, payload=payload)
    return APIResponse(
        success=True,
        message="Notification created.",
        data=result.model_dump(mode="json"),
    )


@router.post(
    "/notifications/broadcast",
    response_model=APIResponse,
    summary="Broadcast notification to all users (admin)",
)
def broadcast_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Send a notification to every active user on the platform."""
    count = notification_service.broadcast_notification(
        db,
        title=payload.title,
        message=payload.message,
        type=payload.type,
        admin_id=admin.id,
    )
    return APIResponse(
        success=True,
        message=f"Notification broadcast to {count} users.",
        data={"count": count},
    )
