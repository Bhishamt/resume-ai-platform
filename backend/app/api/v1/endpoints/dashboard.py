from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardPreferencesResponse,
    DashboardPreferencesUpdate,
)
from app.schemas.user import APIResponse
from app.services.dashboard.analytics_service import AnalyticsService
from app.services.dashboard.dashboard_service import DashboardService
from app.services.dashboard.recommendation_service import RecommendationService
from app.services.dashboard.statistics_service import StatisticsService
from app.services.dashboard.trend_service import TrendService

router = APIRouter()


@router.get(
    "",
    response_model=APIResponse,
    summary="Get consolidated dashboard payload",
)
def get_consolidated_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = DashboardService.get_consolidated_dashboard(db, current_user.id)
        return APIResponse(
            success=True,
            message="Dashboard consolidated data retrieved successfully.",
            data=data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while compiling dashboard: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=APIResponse,
    summary="Get user metrics and statistics KPIs",
)
def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = StatisticsService.get_user_statistics(db, current_user.id)
        return APIResponse(
            success=True,
            message="Dashboard statistics retrieved successfully.",
            data=data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate stats: {str(e)}",
        )


@router.get(
    "/trends",
    response_model=APIResponse,
    summary="Get chronological timelines and score trends",
)
def get_dashboard_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = TrendService.get_user_trends(db, current_user.id)
        return APIResponse(
            success=True, message="Dashboard trends retrieved successfully.", data=data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate trends: {str(e)}",
        )


@router.get(
    "/skills",
    response_model=APIResponse,
    summary="Get skills profiles (matching and missing)",
)
def get_dashboard_skills(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = AnalyticsService.get_user_skills_analytics(db, current_user.id)
        return APIResponse(
            success=True,
            message="Dashboard skills analytics retrieved successfully.",
            data=data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate skills analytics: {str(e)}",
        )


@router.get(
    "/recommendations",
    response_model=APIResponse,
    summary="Get deterministic career insights",
)
def get_dashboard_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = RecommendationService.get_career_insights(db, current_user.id)
        return APIResponse(
            success=True,
            message="Dashboard recommendations retrieved successfully.",
            data=data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile career recommendations: {str(e)}",
        )


@router.put(
    "/preferences",
    response_model=APIResponse,
    summary="Update user layout and widget configuration preferences",
)
def update_dashboard_preferences(
    payload: DashboardPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        prefs = DashboardService.update_user_preferences(
            db=db,
            user_id=current_user.id,
            layout=payload.layout,
            widgets=payload.widgets,
            theme=payload.theme,
        )
        prefs_response = DashboardPreferencesResponse.model_validate(prefs)
        return APIResponse(
            success=True,
            message="Dashboard preferences updated successfully.",
            data=prefs_response.model_dump(mode="json"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save preferences: {str(e)}",
        )
