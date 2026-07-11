"""Analytics service — aggregates platform-wide statistics for the admin dashboard."""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories import admin_repository
from app.schemas.admin import (AnalyticsResponse, ATSBucket, ChartDataPoint,
                               DashboardStats, ProviderStat)

logger = logging.getLogger(__name__)


def get_dashboard_stats(db: Session) -> DashboardStats:
    """Compute all top-level dashboard metrics."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    return DashboardStats(
        total_users=admin_repository.count_users(db),
        active_users=admin_repository.count_active_users(db),
        new_users_today=admin_repository.count_new_users_since(db, today_start),
        new_users_this_month=admin_repository.count_new_users_since(db, month_start),
        total_resumes=admin_repository.count_resumes(db),
        resumes_today=admin_repository.count_resumes_since(db, today_start),
        total_analysis_reports=admin_repository.count_analysis_reports(db),
        total_job_matches=admin_repository.count_job_matches(db),
        total_ai_requests=admin_repository.count_ai_requests(db),
        ai_requests_today=admin_repository.count_ai_requests_since(db, today_start),
        total_tokens_used=admin_repository.get_total_tokens_used(db),
        avg_response_time_ms=admin_repository.get_avg_response_time(db) * 1000,
    )


def get_analytics(db: Session, days: int = 30) -> AnalyticsResponse:
    """Return full analytics payload including chart data."""
    stats = get_dashboard_stats(db)

    raw_user_growth = admin_repository.get_users_by_day(db, days=days)
    raw_uploads = admin_repository.get_resumes_by_day(db, days=days)
    raw_ats = admin_repository.get_ats_score_distribution(db)
    raw_providers = admin_repository.get_ai_provider_stats(db)

    return AnalyticsResponse(
        stats=stats,
        user_growth=[ChartDataPoint(**r) for r in raw_user_growth],
        daily_uploads=[ChartDataPoint(**r) for r in raw_uploads],
        ats_distribution=[ATSBucket(**r) for r in raw_ats],
        ai_provider_stats=[ProviderStat(**r) for r in raw_providers],
    )
