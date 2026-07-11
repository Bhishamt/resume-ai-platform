from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.analysis_report import AnalysisReport
from app.repositories import analysis_repository
from app.services import resume_service
from app.services.ats.ats_engine import AtsEngine


def create_analysis(db: Session, resume_id: UUID, user_id: UUID) -> AnalysisReport:
    """Run ATS analysis on user's resume, save, and return report."""
    # 1. Fetch resume and verify user ownership (throws exceptions if invalid/unauthorized)
    resume = resume_service.get_resume_by_id(db, resume_id, user_id)

    # 2. Run deterministic analysis engine
    report_data = AtsEngine.analyze_resume(db, resume)

    # 3. Save report to DB
    return analysis_repository.create(db, resume_id, report_data)


def get_analysis_by_id(db: Session, report_id: UUID, user_id: UUID) -> AnalysisReport:
    """Fetch analysis report details after verifying user ownership."""
    report = analysis_repository.get_by_id(db, report_id)
    if not report:
        raise NotFoundError("Analysis report not found.")

    if report.resume.user_id != user_id:
        raise AuthorizationError(
            "You do not have permission to access this analysis report."
        )

    return report


def get_user_analyses(db: Session, user_id: UUID) -> list[AnalysisReport]:
    """Fetch all analysis reports belonging to the user."""
    return analysis_repository.get_all_by_user_id(db, user_id)


def delete_analysis(db: Session, report_id: UUID, user_id: UUID) -> None:
    """Delete an analysis report after verifying user ownership."""
    report = get_analysis_by_id(db, report_id, user_id)
    analysis_repository.delete(db, report)
