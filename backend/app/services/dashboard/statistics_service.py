from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.resume import Resume
from app.models.analysis_report import AnalysisReport
from app.models.job_match import JobMatch
from app.models.ai_feedback import AIFeedback

class StatisticsService:
    @staticmethod
    def get_user_statistics(db: Session, user_id: UUID) -> Dict[str, Any]:
        """
        Aggregate high-level metrics (KPIs) for the user.
        """
        # 1. Resume count
        resume_count = db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.upload_status == "success"
        ).count()

        # 2. ATS Score stats (Average and Best)
        ats_stats = db.query(
            func.avg(AnalysisReport.ats_score),
            func.max(AnalysisReport.ats_score)
        ).join(Resume).filter(
            Resume.user_id == user_id
        ).first()

        avg_ats = round(float(ats_stats[0]), 1) if ats_stats and ats_stats[0] is not None else 0.0
        best_ats = int(ats_stats[1]) if ats_stats and ats_stats[1] is not None else 0

        # 3. Job Match stats (Average and Best)
        match_stats = db.query(
            func.avg(JobMatch.overall_match),
            func.max(JobMatch.overall_match)
        ).join(Resume).filter(
            Resume.user_id == user_id
        ).first()

        avg_match = round(float(match_stats[0]), 1) if match_stats and match_stats[0] is not None else 0.0
        best_match = int(match_stats[1]) if match_stats and match_stats[1] is not None else 0

        # 4. AI Usage stats
        ai_calls_count = db.query(AIFeedback).filter(
            AIFeedback.user_id == user_id
        ).count()

        # AI Feature requested breakdown
        ai_features_breakdown = db.query(
            AIFeedback.prompt_type,
            func.count(AIFeedback.id)
        ).filter(
            AIFeedback.user_id == user_id
        ).group_by(
            AIFeedback.prompt_type
        ).all()

        ai_features = {item[0]: int(item[1]) for item in ai_features_breakdown}

        return {
            "resume_count": resume_count,
            "average_ats_score": avg_ats,
            "best_ats_score": best_ats,
            "average_job_match": avg_match,
            "best_job_match": best_match,
            "ai_usage_count": ai_calls_count,
            "most_requested_ai_features": ai_features
        }
