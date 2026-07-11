from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.analysis import AnalysisReportResponse
from app.schemas.user import APIResponse
from app.services import analysis_service

router = APIRouter()


@router.post(
    "/{resume_id}",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a resume and generate ATS score",
)
def analyze_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Trigger the ATS scoring engine on a specific resume, persisting the report."""
    report = analysis_service.create_analysis(db, resume_id, current_user.id)
    return APIResponse(
        success=True,
        message="Resume analyzed successfully.",
        data=AnalysisReportResponse.model_validate(report).model_dump(mode="json"),
    )


@router.get("", response_model=APIResponse, summary="Get user's analysis reports")
def get_analyses(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Retrieve all ATS analysis reports belonging to the authenticated user."""
    reports = analysis_service.get_user_analyses(db, current_user.id)
    return APIResponse(
        success=True,
        message="Analysis reports retrieved successfully.",
        data=[
            AnalysisReportResponse.model_validate(r).model_dump(mode="json")
            for r in reports
        ],
    )


@router.get(
    "/{id}", response_model=APIResponse, summary="Get analysis report details by ID"
)
def get_analysis(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve details of a specific ATS analysis report by its ID."""
    report = analysis_service.get_analysis_by_id(db, id, current_user.id)
    return APIResponse(
        success=True,
        message="Analysis report details retrieved successfully.",
        data=AnalysisReportResponse.model_validate(report).model_dump(mode="json"),
    )


@router.delete(
    "/{id}", response_model=APIResponse, summary="Delete analysis report by ID"
)
def delete_analysis(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a specific ATS analysis report."""
    analysis_service.delete_analysis(db, id, current_user.id)
    return APIResponse(success=True, message="Analysis report deleted successfully.")
