from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.analysis_report import AnalysisReport
from app.models.resume import Resume

def get_by_id(db: Session, report_id: UUID) -> Optional[AnalysisReport]:
    """Fetch an analysis report by its UUID."""
    return db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()

def get_all_by_user_id(db: Session, user_id: UUID) -> list[AnalysisReport]:
    """Fetch all analysis reports belonging to the user's resumes."""
    return (
        db.query(AnalysisReport)
        .join(Resume, AnalysisReport.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .order_by(AnalysisReport.created_at.desc())
        .all()
    )

def create(db: Session, resume_id: UUID, report_data: dict) -> AnalysisReport:
    """Create a new analysis report record."""
    report = AnalysisReport(
        resume_id=resume_id,
        ats_score=report_data["ats_score"],
        resume_score=report_data["resume_score"],
        keyword_score=report_data["keyword_score"],
        formatting_score=report_data["formatting_score"],
        experience_score=report_data["experience_score"],
        education_score=report_data["education_score"],
        projects_score=report_data["projects_score"],
        grammar_score=report_data["grammar_score"],
        strengths=report_data["strengths"],
        weaknesses=report_data["weaknesses"],
        missing_keywords=report_data["missing_keywords"],
        suggestions=report_data["suggestions"],
        scoring_explanations=report_data["scoring_explanations"],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def delete(db: Session, report: AnalysisReport) -> None:
    """Delete an analysis report record."""
    db.delete(report)
    db.commit()
