"""Resume Management API endpoints.

All routes are protected by JWT authentication and verify user ownership.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.user import APIResponse
from app.schemas.resume import ResumeResponse, PaginatedResumes, UploadHistoryResponse, ResumeUpdate
from app.services import resume_service

router = APIRouter()

@router.post(
    "/upload",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a new resume",
)
def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX only, max 10MB)"),
    title: str | None = Form(None, description="Optional custom title for the resume"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Securely upload a PDF or DOCX resume, parse its contents, and save the metadata."""
    resume = resume_service.upload_resume(db, file, current_user.id, title)
    return APIResponse(
        success=True,
        message="Resume uploaded and parsed successfully.",
        data=ResumeResponse.model_validate(resume).model_dump(mode="json"),
    )

@router.get(
    "",
    response_model=APIResponse,
    summary="Get paginated list of user's resumes",
)
def get_resumes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve all resumes owned by the authenticated user with offset pagination."""
    items, total = resume_service.get_resumes_paginated(db, current_user.id, page, limit)
    paginated_data = PaginatedResumes(
        items=[ResumeResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
    )
    return APIResponse(
        success=True,
        message="Resumes retrieved successfully.",
        data=paginated_data.model_dump(mode="json"),
    )

@router.get(
    "/history",
    response_model=APIResponse,
    summary="Get user's upload activity log",
)
def get_upload_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve all resume-related actions (upload, replace, delete) done by the user."""
    history = resume_service.get_upload_history(db, current_user.id)
    history_responses = []
    
    # Enrich history with titles if needed or output directly
    for entry in history:
        resp = UploadHistoryResponse.model_validate(entry)
        if entry.resume:
            resp.resume_title = entry.resume.title
        else:
            resp.resume_title = "Deleted Resume"
        history_responses.append(resp)

    return APIResponse(
        success=True,
        message="Upload history retrieved successfully.",
        data=[h.model_dump(mode="json") for h in history_responses],
    )

@router.get(
    "/{id}",
    response_model=APIResponse,
    summary="Get resume details by ID",
)
def get_resume(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve full metadata and parsed text content of a specific resume."""
    resume = resume_service.get_resume_by_id(db, id, current_user.id)
    return APIResponse(
        success=True,
        message="Resume retrieved successfully.",
        data=ResumeResponse.model_validate(resume).model_dump(mode="json"),
    )

@router.delete(
    "/{id}",
    response_model=APIResponse,
    summary="Delete a resume by ID",
)
def delete_resume(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a resume record from the database and remove the physical file from disk."""
    resume_service.delete_resume(db, id, current_user.id)
    return APIResponse(
        success=True,
        message="Resume deleted successfully.",
    )

@router.put(
    "/{id}",
    response_model=APIResponse,
    summary="Update resume metadata / title",
)
def update_resume(
    id: UUID,
    schema: ResumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update title metadata for a specific resume."""
    resume = resume_service.update_resume_title(db, id, current_user.id, schema.title)
    return APIResponse(
        success=True,
        message="Resume updated successfully.",
        data=ResumeResponse.model_validate(resume).model_dump(mode="json"),
    )

@router.post(
    "/{id}/replace",
    response_model=APIResponse,
    summary="Replace physical file of an existing resume",
)
def replace_resume(
    id: UUID,
    file: UploadFile = File(..., description="New resume file (PDF or DOCX only, max 10MB)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Replace an existing resume's physical file and re-parse metadata, retaining the ID."""
    resume = resume_service.replace_resume(db, id, file, current_user.id)
    return APIResponse(
        success=True,
        message="Resume replaced and parsed successfully.",
        data=ResumeResponse.model_validate(resume).model_dump(mode="json"),
    )
