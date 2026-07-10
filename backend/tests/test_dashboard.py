import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.analysis_report import AnalysisReport
from app.models.job_description import JobDescription
from app.models.job_match import JobMatch
from app.models.ai_feedback import AIFeedback
from app.models.dashboard_preferences import DashboardPreferences

from app.services.dashboard.statistics_service import StatisticsService
from app.services.dashboard.trend_service import TrendService
from app.services.dashboard.analytics_service import AnalyticsService
from app.services.dashboard.recommendation_service import RecommendationService
from app.services.dashboard.dashboard_service import DashboardService

# --- Helper function to create base user context in DB ---
def create_dummy_data(db_session: Session, user_id: uuid4):
    # 1. Resumes
    r1 = Resume(
        id=uuid4(),
        user_id=user_id,
        title="Resume Alpha",
        original_filename="alpha.pdf",
        stored_filename="alpha_stored.pdf",
        file_type="application/pdf",
        file_size=100,
        storage_path="/path1",
        upload_status="success",
        upload_date=datetime.now(timezone.utc) - timedelta(days=5)
    )
    r2 = Resume(
        id=uuid4(),
        user_id=user_id,
        title="Resume Beta",
        original_filename="beta.pdf",
        stored_filename="beta_stored.pdf",
        file_type="application/pdf",
        file_size=200,
        storage_path="/path2",
        upload_status="success",
        upload_date=datetime.now(timezone.utc) - timedelta(days=2)
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    # 2. Analysis Reports
    rep1 = AnalysisReport(
        id=uuid4(),
        resume_id=r1.id,
        ats_score=60,
        resume_score=65,
        strengths=["Good format"],
        weaknesses=["Missing Python keyword"],
        missing_keywords=["Python", "SQL"],
        created_at=datetime.now(timezone.utc) - timedelta(days=5)
    )
    rep2 = AnalysisReport(
        id=uuid4(),
        resume_id=r2.id,
        ats_score=80,
        resume_score=85,
        strengths=["Python included", "Docker included"],
        weaknesses=["Missing AWS"],
        missing_keywords=["AWS"],
        created_at=datetime.now(timezone.utc) - timedelta(days=2)
    )
    db_session.add_all([rep1, rep2])
    db_session.commit()

    # 3. Job Descriptions
    jd = JobDescription(
        id=uuid4(),
        user_id=user_id,
        title="Backend Engineer",
        company="TechCorp",
        description="We need a Python developer with SQL and AWS.",
        required_skills=["Python", "SQL", "AWS"],
        preferred_skills=["Docker"],
        created_at=datetime.now(timezone.utc) - timedelta(days=3)
    )
    db_session.add(jd)
    db_session.commit()

    # 4. Job Matches
    match = JobMatch(
        id=uuid4(),
        resume_id=r2.id,
        job_description_id=jd.id,
        overall_match=70,
        matching_skills=["Python", "Docker"],
        missing_skills=["AWS", "SQL"],
        score_explanations={},
        created_at=datetime.now(timezone.utc) - timedelta(days=2)
    )
    db_session.add(match)
    db_session.commit()

    # 5. AI Feedback
    ai1 = AIFeedback(
        id=uuid4(),
        user_id=user_id,
        resume_id=r1.id,
        provider="MockProvider",
        prompt_type="resume_review",
        prompt_version="1.0.0",
        response="{}",
        token_usage={"total_tokens": 100},
        response_time=0.2,
        created_at=datetime.now(timezone.utc) - timedelta(days=5)
    )
    db_session.add(ai1)
    db_session.commit()

    return r1, r2, rep1, rep2, jd, match, ai1

# --- 1. Unit Tests for Dashboard Services ---

def test_statistics_service(db_session):
    user_id = uuid4()
    create_dummy_data(db_session, user_id)

    stats = StatisticsService.get_user_statistics(db_session, user_id)

    assert stats["resume_count"] == 2
    assert stats["average_ats_score"] == 70.0
    assert stats["best_ats_score"] == 80
    assert stats["average_job_match"] == 70.0
    assert stats["best_job_match"] == 70
    assert stats["ai_usage_count"] == 1
    assert "resume_review" in stats["most_requested_ai_features"]

def test_trend_service(db_session):
    user_id = uuid4()
    create_dummy_data(db_session, user_id)

    trends = TrendService.get_user_trends(db_session, user_id)

    assert len(trends["ats_trend"]) == 2
    assert trends["ats_trend"][0]["score"] == 60
    assert trends["ats_trend"][1]["score"] == 80
    assert len(trends["upload_timeline"]) >= 1
    assert len(trends["job_match_trend"]) == 1

def test_analytics_service(db_session):
    user_id = uuid4()
    create_dummy_data(db_session, user_id)

    analytics = AnalyticsService.get_user_skills_analytics(db_session, user_id)

    # Top matching skills from JobMatch: Python, Docker
    top_skills = [item["skill"] for item in analytics["top_skills"]]
    assert "Python" in top_skills
    assert "Docker" in top_skills

    # Top missing skills from JobMatch/AnalysisReport: AWS, SQL, Python (from rep1 missing)
    missing_skills = [item["skill"] for item in analytics["missing_skills"]]
    assert "AWS" in missing_skills
    assert "SQL" in missing_skills

def test_recommendation_service(db_session):
    user_id = uuid4()
    create_dummy_data(db_session, user_id)

    recs = RecommendationService.get_career_insights(db_session, user_id)

    assert recs["interview_readiness"]["status"] == "Medium"
    assert recs["ats_improvement"]["direction"] == "improving"
    assert len(recs["technologies_to_learn"]) > 0

def test_dashboard_preferences_service(db_session):
    user_id = uuid4()

    # Get default preferences
    prefs = DashboardService.get_user_preferences(db_session, user_id)
    assert prefs.theme == "dark"
    assert "kpi_cards" in prefs.layout

    # Update preferences
    new_layout = ["ats_trend", "kpi_cards"]
    DashboardService.update_user_preferences(db_session, user_id, layout=new_layout, theme="light")

    updated = DashboardService.get_user_preferences(db_session, user_id)
    assert updated.theme == "light"
    assert updated.layout == new_layout

# --- 2. API Endpoint Routing Tests ---

def test_api_get_consolidated_dashboard(client, db_session, auth_headers):
    # Extract user ID from token
    from app.utils.jwt_utils import decode_token
    token = auth_headers["Authorization"][7:]
    payload = decode_token(token)
    user_uuid = UUID(payload["sub"])

    # Load dummy data
    create_dummy_data(db_session, user_uuid)

    response = client.get("/api/v1/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "stats" in data["data"]
    assert "trends" in data["data"]
    assert "recommendations" in data["data"]
    assert "preferences" in data["data"]

def test_api_update_preferences(client, db_session, auth_headers):
    payload = {
        "layout": ["ats_trend", "kpi_cards"],
        "widgets": {"kpi_cards": True, "ats_trend": False},
        "theme": "light"
    }
    response = client.put("/api/v1/dashboard/preferences", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["theme"] == "light"
    assert data["data"]["layout"] == ["ats_trend", "kpi_cards"]
