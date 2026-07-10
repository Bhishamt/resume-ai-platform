from typing import List, Dict, Any
from uuid import UUID
from collections import Counter
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.job_match import JobMatch
from app.models.analysis_report import AnalysisReport

class AnalyticsService:
    @staticmethod
    def get_user_skills_analytics(db: Session, user_id: UUID) -> Dict[str, Any]:
        """
        Aggregate skill profiles based on matching and missing keywords from reports & matches.
        """
        matching_counter = Counter()
        missing_counter = Counter()

        # 1. Collect skills from Job Match history
        matches = db.query(JobMatch).join(Resume).filter(
            Resume.user_id == user_id
        ).all()

        for m in matches:
            if isinstance(m.matching_skills, list):
                # Normalize skill case for consistent aggregation
                matching_counter.update(s.strip() for s in m.matching_skills if s)
            if isinstance(m.missing_skills, list):
                missing_counter.update(s.strip() for s in m.missing_skills if s)

        # 2. Collect missing keywords from Analysis Reports
        reports = db.query(AnalysisReport).join(Resume).filter(
            Resume.user_id == user_id
        ).all()

        for r in reports:
            if isinstance(r.missing_keywords, list):
                missing_counter.update(k.strip() for k in r.missing_keywords if k)

        top_skills = [
            {"skill": skill, "count": count}
            for skill, count in matching_counter.most_common(10)
        ]

        top_missing_skills = [
            {"skill": skill, "count": count}
            for skill, count in missing_counter.most_common(10)
        ]

        # Return format suited for Radar/Bar chart mapping
        return {
            "top_skills": top_skills,
            "missing_skills": top_missing_skills
        }
