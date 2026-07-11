from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.job_matching import JobMatchRequest, JobMatchResponse
from app.schemas.user import APIResponse
from app.services import job_matching_service

router = APIRouter()


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compare resume against job description and generate match report",
)
def run_matching(
    payload: JobMatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run deterministic Job Matching engine on a resume and job description."""
    report = job_matching_service.run_job_match(
        db=db,
        user_id=current_user.id,
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        job_description_in=payload.job_description,
    )
    return APIResponse(
        success=True,
        message="Job matching calculated successfully.",
        data=JobMatchResponse.model_validate(report).model_dump(mode="json"),
    )


@router.get("", response_model=APIResponse, summary="Get user's job match reports")
def get_matches(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve all Job Match reports belonging to the user (paginated)."""
    reports = job_matching_service.get_user_job_matches(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return APIResponse(
        success=True,
        message="Job match reports retrieved successfully.",
        data=[
            JobMatchResponse.model_validate(r).model_dump(mode="json") for r in reports
        ],
    )


@router.get(
    "/{id}", response_model=APIResponse, summary="Get job match report details by ID"
)
def get_match(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve details of a specific job match report by its ID."""
    report = job_matching_service.get_job_match(
        db=db, match_id=id, user_id=current_user.id
    )
    return APIResponse(
        success=True,
        message="Job match report details retrieved successfully.",
        data=JobMatchResponse.model_validate(report).model_dump(mode="json"),
    )


@router.delete(
    "/{id}", response_model=APIResponse, summary="Delete job match report by ID"
)
def delete_match(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a specific job match report."""
    job_matching_service.delete_job_match(db=db, match_id=id, user_id=current_user.id)
    return APIResponse(success=True, message="Job match report deleted successfully.")
