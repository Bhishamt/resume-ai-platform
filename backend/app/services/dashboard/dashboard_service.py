import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_feedback import AIFeedback
from app.models.dashboard_preferences import DashboardPreferences
from app.models.job_match import JobMatch
from app.models.upload_history import UploadHistory
from app.services.dashboard.analytics_service import AnalyticsService
from app.services.dashboard.recommendation_service import RecommendationService
from app.services.dashboard.statistics_service import StatisticsService
from app.services.dashboard.trend_service import TrendService

logger = logging.getLogger(__name__)

# Default Preferences
DEFAULT_WIDGETS = {
    "kpi_cards": True,
    "ats_trend": True,
    "job_match_trend": True,
    "resume_timeline": True,
    "skills_radar": True,
    "missing_skills": True,
    "career_insights": True,
    "ai_usage": True,
    "recent_activity": True,
}

DEFAULT_LAYOUT = [
    "kpi_cards",
    "ats_trend",
    "job_match_trend",
    "resume_timeline",
    "skills_radar",
    "missing_skills",
    "career_insights",
    "ai_usage",
    "recent_activity",
]


class DashboardService:
    @staticmethod
    def get_user_preferences(db: Session, user_id: UUID) -> DashboardPreferences:
        """
        Fetch or create default dashboard preferences for a user.
        """
        prefs = (
            db.query(DashboardPreferences)
            .filter(DashboardPreferences.user_id == user_id)
            .first()
        )

        if not prefs:
            prefs = DashboardPreferences(
                user_id=user_id,
                layout=DEFAULT_LAYOUT,
                widgets=DEFAULT_WIDGETS,
                theme="dark",
            )
            db.add(prefs)
            db.commit()
            db.refresh(prefs)

        return prefs

    @staticmethod
    def update_user_preferences(
        db: Session,
        user_id: UUID,
        layout: Optional[List[str]] = None,
        widgets: Optional[Dict[str, bool]] = None,
        theme: Optional[str] = None,
    ) -> DashboardPreferences:
        """
        Update user layout preferences.
        """
        prefs = DashboardService.get_user_preferences(db, user_id)

        if layout is not None:
            prefs.layout = layout
        if widgets is not None:
            # Merge widgets dictionary to prevent clearing existing settings
            merged_widgets = dict(prefs.widgets or DEFAULT_WIDGETS)
            merged_widgets.update(widgets)
            prefs.widgets = merged_widgets
        if theme is not None:
            prefs.theme = theme

        prefs.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(prefs)
        return prefs

    @staticmethod
    def get_recent_activity(db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Collect unified activity logs across uploads, matches, and AI calls.
        """
        activity = []

        # 1. Fetch upload history
        histories = (
            db.query(UploadHistory)
            .filter(UploadHistory.user_id == user_id)
            .order_by(UploadHistory.timestamp.desc())
            .limit(10)
            .all()
        )

        for h in histories:
            activity.append(
                {
                    "type": "upload",
                    "action": h.action,
                    "title": f"Resume {h.action}ed",
                    "description": h.resume.title if h.resume else "Deleted Resume",
                    "timestamp": h.timestamp.isoformat(),
                }
            )

        # 2. Fetch Job Matches
        matches = (
            db.query(JobMatch)
            .join(JobMatch.resume)
            .filter(JobMatch.resume.has(user_id=user_id))
            .order_by(JobMatch.created_at.desc())
            .limit(10)
            .all()
        )

        for m in matches:
            company = (
                m.job_description.company if m.job_description else "Unknown Company"
            )
            job_title = m.job_description.title if m.job_description else "Position"
            activity.append(
                {
                    "type": "match",
                    "action": "match",
                    "title": f"Job Match Computed: {m.overall_match}%",
                    "description": f"{job_title} at {company}",
                    "timestamp": m.created_at.isoformat(),
                }
            )

        # 3. Fetch AI Feedback
        feedbacks = (
            db.query(AIFeedback)
            .filter(AIFeedback.user_id == user_id)
            .order_by(AIFeedback.created_at.desc())
            .limit(10)
            .all()
        )

        for f in feedbacks:
            activity.append(
                {
                    "type": "ai",
                    "action": f.prompt_type,
                    "title": f"AI {f.prompt_type.replace('_', ' ').title()}",
                    "description": f"Tokens used: {f.token_usage.get('total_tokens', 0)}",
                    "timestamp": f.created_at.isoformat(),
                }
            )

        # Sort combined chronologically (descending)
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        return activity[:10]

    @staticmethod
    def get_consolidated_dashboard(db: Session, user_id: UUID) -> Dict[str, Any]:
        """
        Consolidate metrics, trends, skills, recommendations, preferences, and activity.
        """
        stats = StatisticsService.get_user_statistics(db, user_id)
        trends = TrendService.get_user_trends(db, user_id)
        skills = AnalyticsService.get_user_skills_analytics(db, user_id)
        recs = RecommendationService.get_career_insights(db, user_id)
        prefs = DashboardService.get_user_preferences(db, user_id)
        activity = DashboardService.get_recent_activity(db, user_id)

        # Convert preferences model to JSON-safe dictionary
        prefs_data = {
            "layout": prefs.layout,
            "widgets": prefs.widgets,
            "theme": prefs.theme,
            "updated_at": prefs.updated_at.isoformat(),
        }

        return {
            "stats": stats,
            "trends": trends,
            "skills": skills,
            "recommendations": recs,
            "preferences": prefs_data,
            "recent_activity": activity,
        }
