"""Pydantic schemas for the Admin Panel API (Phase 9)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class PaginatedMeta(BaseModel):
    total: int
    page: int
    per_page: int
    pages: int


# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------


class AdminUserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    meta: PaginatedMeta


class AdminUserUpdate(BaseModel):
    """Payload for updating a user's role or active status."""

    role: Optional[str] = Field(None, pattern="^(user|admin)$")
    is_active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Resume Management
# ---------------------------------------------------------------------------


class AdminResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    original_filename: str
    file_type: str
    file_size: int
    upload_status: str
    upload_date: datetime

    model_config = {"from_attributes": True}


class AdminResumeListResponse(BaseModel):
    resumes: List[AdminResumeResponse]
    meta: PaginatedMeta


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_month: int
    total_resumes: int
    resumes_today: int
    total_analysis_reports: int
    total_job_matches: int
    total_ai_requests: int
    ai_requests_today: int
    total_tokens_used: int
    avg_response_time_ms: float


class ChartDataPoint(BaseModel):
    day: str
    count: int


class ATSBucket(BaseModel):
    range: str
    count: int


class ProviderStat(BaseModel):
    provider: str
    count: int


class AnalyticsResponse(BaseModel):
    stats: DashboardStats
    user_growth: List[ChartDataPoint]
    daily_uploads: List[ChartDataPoint]
    ats_distribution: List[ATSBucket]
    ai_provider_stats: List[ProviderStat]


# ---------------------------------------------------------------------------
# AI Monitoring
# ---------------------------------------------------------------------------


class AIMonitoringResponse(BaseModel):
    total_requests: int
    total_tokens: int
    avg_response_time_ms: float
    provider_stats: List[ProviderStat]
    requests_today: int
    tokens_today: int


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------


class AdminLogResponse(BaseModel):
    id: UUID
    admin_id: Optional[UUID] = None
    action: str
    entity: str
    entity_id: Optional[str] = None
    log_metadata: Dict[str, Any] = Field(default_factory=dict, alias="log_metadata")
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class AdminLogListResponse(BaseModel):
    logs: List[AdminLogResponse]
    meta: PaginatedMeta


# ---------------------------------------------------------------------------
# System Settings
# ---------------------------------------------------------------------------


class SettingResponse(BaseModel):
    id: UUID
    key: str
    value: Optional[str]
    description: Optional[str]
    updated_by: Optional[UUID]
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., max_length=5000)
    description: Optional[str] = Field(None, max_length=1000)


class BulkSettingsUpdate(BaseModel):
    settings: List[SettingUpdate] = Field(..., min_length=1)


class SettingsListResponse(BaseModel):
    settings: List[SettingResponse]


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    type: str = Field(default="info", pattern="^(info|success|warning|error|system)$")


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int
    meta: PaginatedMeta


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------


class SystemHealthResponse(BaseModel):
    api_status: str
    database_status: str
    storage_used_bytes: int
    storage_used_mb: float
    uptime_seconds: float
    memory_used_mb: float
    memory_total_mb: float
    memory_percent: float
    cpu_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_percent: float
    ai_provider_status: str
