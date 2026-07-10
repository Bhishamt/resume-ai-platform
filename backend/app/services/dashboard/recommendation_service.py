from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.analysis_report import AnalysisReport
from app.models.job_match import JobMatch
from app.services.dashboard.analytics_service import AnalyticsService

class RecommendationService:
    @staticmethod
    def get_career_insights(db: Session, user_id: UUID) -> Dict[str, Any]:
        """
        Generate deterministic career insights based on database history.
        No LLM queries are used here.
        """
        # 1. Fetch skills analytics
        skills_data = AnalyticsService.get_user_skills_analytics(db, user_id)
        missing_skills_list = [item["skill"] for item in skills_data["missing_skills"]]
        
        # 2. Technologies to learn
        tech_to_learn = missing_skills_list[:5] if missing_skills_list else ["Docker", "Kubernetes", "TypeScript", "System Design", "AWS"]

        # 3. Calculate ATS Improvement over time
        reports = db.query(AnalysisReport).join(Resume).filter(
            Resume.user_id == user_id
        ).order_by(AnalysisReport.created_at.asc()).all()

        ats_evaluation = "Upload and analyze your resume to track ATS improvement over time."
        ats_trend_direction = "stable"
        
        if len(reports) >= 2:
            earliest_score = reports[0].ats_score
            latest_score = reports[-1].ats_score
            diff = latest_score - earliest_score
            
            if diff > 0:
                ats_evaluation = f"Great work! Your ATS compatibility score has improved by {diff} points since your first analysis."
                ats_trend_direction = "improving"
            elif diff < 0:
                ats_evaluation = f"Your latest resume has a lower ATS score ({latest_score}) than your first upload ({earliest_score}). We suggest reverting formatting changes or re-adding missing keywords."
                ats_trend_direction = "declining"
            else:
                ats_evaluation = f"Your ATS score has remained steady at {latest_score} points. Focus on adding critical job-description keywords to boost it."
                ats_trend_direction = "stable"
        elif len(reports) == 1:
            ats_evaluation = f"Your current ATS score is {reports[0].ats_score} points. Upload modified resumes to compare improvements."

        # 4. Job Match & Interview Readiness
        matches = db.query(JobMatch).join(Resume).filter(
            Resume.user_id == user_id
        ).all()

        readiness_status = "Not Evaluated"
        readiness_score = 0
        readiness_text = "Match your resumes against job descriptions to compute interview readiness."

        if matches:
            overall_scores = [m.overall_match for m in matches]
            avg_match = sum(overall_scores) / len(overall_scores)
            readiness_score = int(avg_match)

            if avg_match >= 75:
                readiness_status = "High"
                readiness_text = f"Your average job match is {readiness_score}%. You exhibit strong alignment with target job profiles and are ready for technical interviews."
            elif avg_match >= 55:
                readiness_status = "Medium"
                readiness_text = f"Your average job match is {readiness_score}%. You are competitive, but adding missing key skills (e.g. {', '.join(tech_to_learn[:2])}) will improve response rates."
            else:
                readiness_status = "Low"
                readiness_text = f"Your average job match is {readiness_score}%. Focus on tailoring your resumes to job requirements to clear preliminary matching screens."

        # 5. General Career growth suggestions
        career_suggestions = []
        if tech_to_learn:
            career_suggestions.append(f"Incorporate missing skills: {', '.join(tech_to_learn[:3])} into your experience bullet points.")
        if readiness_status == "Low" or readiness_status == "Medium":
            career_suggestions.append("Apply to roles that prioritize your top matching skills rather than missing tech.")
        career_suggestions.append("Update certifications section on your resume as you master new skills.")

        return {
            "most_common_missing_skills": missing_skills_list[:6],
            "technologies_to_learn": tech_to_learn,
            "ats_improvement": {
                "evaluation": ats_evaluation,
                "direction": ats_trend_direction
            },
            "interview_readiness": {
                "status": readiness_status,
                "score": readiness_score,
                "description": readiness_text
            },
            "career_growth_suggestions": career_suggestions
        }
