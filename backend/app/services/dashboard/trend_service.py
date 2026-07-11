from typing import Any, Dict
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.analysis_report import AnalysisReport
from app.models.job_match import JobMatch
from app.models.resume import Resume


class TrendService:
    @staticmethod
    def get_user_trends(db: Session, user_id: UUID) -> Dict[str, Any]:
        """
        Aggregate chronological trend data for the user dashboard.
        """
        # 1. ATS Score trend (Analysis reports chronological)
        reports = (
            db.query(AnalysisReport.created_at, AnalysisReport.ats_score, Resume.title)
            .join(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(AnalysisReport.created_at)
            .all()
        )

        ats_trend = [
            {
                "date": r.created_at.strftime("%Y-%m-%d"),
                "score": r.ats_score,
                "resume_title": r.title,
            }
            for r in reports
        ]

        # 2. Resume Upload timeline
        resumes = (
            db.query(Resume.upload_date)
            .filter(Resume.user_id == user_id, Resume.upload_status == "success")
            .order_by(Resume.upload_date)
            .all()
        )

        # Aggregate uploads by date string
        upload_counts = {}
        for r in resumes:
            date_str = r.upload_date.strftime("%Y-%m-%d")
            upload_counts[date_str] = upload_counts.get(date_str, 0) + 1

        upload_timeline = [
            {"date": d, "count": c} for d, c in sorted(upload_counts.items())
        ]

        # 3. Job Match trend
        matches = (
            db.query(JobMatch)
            .join(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(JobMatch.created_at)
            .all()
        )

        job_match_trend = [
            {
                "date": m.created_at.strftime("%Y-%m-%d"),
                "score": m.overall_match,
                "company": (
                    m.job_description.company if m.job_description else "Unknown"
                ),
                "title": m.job_description.title if m.job_description else "Unknown",
            }
            for m in matches
        ]

        return {
            "ats_trend": ats_trend,
            "upload_timeline": upload_timeline,
            "job_match_trend": job_match_trend,
        }
