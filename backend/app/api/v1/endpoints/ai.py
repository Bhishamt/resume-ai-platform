from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.user import APIResponse
from app.schemas.ai import (
    AIReviewRequest,
    AICoverLetterRequest,
    AIImproveSummaryRequest,
    AIImproveProjectsRequest,
    AIInterviewRequest,
    AICareerRequest,
    AIFeedbackResponse,
)
from app.services.ai.ai_service import ai_service

router = APIRouter()

@router.post(
    "/review",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed resume feedback",
)
async def review_resume(
    payload: AIReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        feedback = await ai_service.review_resume(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id,
            analysis_id=payload.analysis_id
        )
        return APIResponse(
            success=True,
            message="Resume review generated successfully.",
            data=feedback
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating resume review: {str(e)}"
        )

@router.post(
    "/cover-letter",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate cover letters",
)
async def generate_cover_letter(
    payload: AICoverLetterRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        letters = await ai_service.generate_cover_letter(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id,
            job_description_id=payload.job_description_id,
            company_name=payload.company_name,
            job_title=payload.job_title,
            job_text=payload.job_text
        )
        return APIResponse(
            success=True,
            message="Cover letters generated successfully.",
            data=letters
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating cover letters: {str(e)}"
        )

@router.post(
    "/improve-summary",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Improve resume summary and bullet points",
)
async def improve_summary(
    payload: AIImproveSummaryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = await ai_service.improve_summary(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id
        )
        return APIResponse(
            success=True,
            message="Summary suggestions generated successfully.",
            data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating summary improvements: {str(e)}"
        )

@router.post(
    "/improve-projects",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Improve project descriptions and action verbs",
)
async def improve_projects(
    payload: AIImproveProjectsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = await ai_service.improve_projects(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id
        )
        return APIResponse(
            success=True,
            message="Project improvements generated successfully.",
            data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while improving project descriptions: {str(e)}"
        )

@router.post(
    "/interview",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate interview preparation material",
)
async def prepare_interview(
    payload: AIInterviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = await ai_service.prepare_interview(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id,
            job_description_id=payload.job_description_id
        )
        return APIResponse(
            success=True,
            message="Interview questions generated successfully.",
            data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating interview prep: {str(e)}"
        )

@router.post(
    "/career",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate career guidance suggestions",
)
async def suggest_career(
    payload: AICareerRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = await ai_service.suggest_career(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id
        )
        return APIResponse(
            success=True,
            message="Career guidance generated successfully.",
            data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating career suggestions: {str(e)}"
        )

@router.get(
    "/history",
    response_model=APIResponse,
    summary="Get user's AI assistant logs history",
)
def get_ai_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    history = ai_service.get_history(db=db, user_id=current_user.id)
    history_responses = [AIFeedbackResponse.model_validate(h) for h in history]
    return APIResponse(
        success=True,
        message="AI history retrieved successfully.",
        data=[h.model_dump(mode="json") for h in history_responses]
    )

@router.delete(
    "/history/{id}",
    response_model=APIResponse,
    summary="Delete a historical AI feedback log",
)
def delete_ai_history(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    deleted = ai_service.delete_history_item(db=db, user_id=current_user.id, feedback_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI feedback log not found or unauthorized."
        )
    return APIResponse(
        success=True,
        message="AI feedback log deleted successfully."
    )
