import pytest
from uuid import uuid4
from fastapi import status
from app.services.ats.section_detector import SectionDetector
from app.services.ats.keyword_analyzer import KeywordAnalyzer
from app.services.ats.formatting_checker import FormattingChecker
from app.services.ats.score_calculator import ScoreCalculator
from app.services.ats.ats_engine import AtsEngine
from app.models.resume import Resume
from app.models.analysis_report import AnalysisReport

# Dummy resume text for testing
TEST_RESUME_TEXT = """
Jane Doe
jane.doe@example.com
(555) 555-5555

Professional Summary
Highly motivated software engineer with 5 years of experience in cloud computing and web development.

Technical Skills
Python, Javascript, React, SQL, Docker, AWS, Git, FastAPI, CI/CD, HTML, CSS

Work Experience
Lead Software Engineer | Tech Solutions (2020 - Present)
- Led a team of developers to build a scalable saas backend using FastAPI and Docker.
- Optimized database queries in PostgreSQL, improving performance by 30%.
- Integrated CI/CD pipelines to automate deployment on AWS.

Education
Bachelor of Science in Computer Science
University of Tech (2015 - 2019)

Projects
- E-commerce Platform: Built a fullstack web app using React and Python.
- Personal Portfolio: Developed a static site with Tailwind CSS.

Certifications
- AWS Certified Developer
"""

class TestAtsEngineHeuristics:
    def test_section_detector(self):
        res = SectionDetector.detect_sections(TEST_RESUME_TEXT)
        assert "Summary" in res["detected_sections"]
        assert "Skills" in res["detected_sections"]
        assert "Experience" in res["detected_sections"]
        assert "Education" in res["detected_sections"]
        assert "Projects" in res["detected_sections"]
        assert "Certifications" in res["detected_sections"]
        assert res["score"] == 100
        assert len(res["missing_sections"]) == 0

    def test_keyword_analyzer(self):
        res = KeywordAnalyzer.analyze_keywords(TEST_RESUME_TEXT)
        assert "Python" in res["found_by_category"]["Technical Skills"]
        assert "React" in res["found_by_category"]["Technical Skills"]
        assert "Fastapi" in res["found_by_category"]["Technical Skills"] or "FASTAPI" in res["found_by_category"]["Technical Skills"]
        assert "LED" in res["found_by_category"]["Action Verbs"]
        assert "Optimized" in res["found_by_category"]["Action Verbs"]
        assert "Software Development" in res["found_by_category"]["Industry Keywords"] or "Saas" in res["found_by_category"]["Industry Keywords"] or "Cloud Computing" in res["found_by_category"]["Industry Keywords"]
        
        # Check missing recommended critical keywords
        # The test resume text has: Python, Javascript, React, SQL, Docker, AWS, Git, FastAPI, CI/CD, Agile is missing
        assert "Agile" in res["missing_keywords"]
        assert res["score"] > 50

    def test_formatting_checker(self):
        detected_sections = ["Summary", "Skills", "Experience", "Education", "Projects"]
        res = FormattingChecker.check_formatting(TEST_RESUME_TEXT, detected_sections)
        assert res["details"]["has_email"] is True
        assert res["details"]["has_phone"] is True
        assert res["details"]["has_name"] is True
        assert res["details"]["bullet_count"] >= 3
        assert res["score"] >= 70

    def test_score_calculator(self):
        # Experience Years
        exp_score, years = ScoreCalculator.calculate_experience_score(TEST_RESUME_TEXT, ["led", "optimized", "integrated"])
        assert years >= 5
        assert exp_score >= 60


        # Education
        edu_score = ScoreCalculator.calculate_education_score(TEST_RESUME_TEXT)
        assert edu_score == 100  # Degree (40) + Institution (40) + Year (20)

        # Grammar Check
        grammar_res = ScoreCalculator.calculate_grammar_score(TEST_RESUME_TEXT)
        assert grammar_res["score"] > 60

        # Weighted Final Score
        cat_scores = {
            "keyword_score": 80,
            "experience_score": 85,
            "formatting_score": 90,
            "projects_score": 75,
            "education_score": 100,
            "grammar_score": 95,
            "section_score": 100
        }
        final_score = ScoreCalculator.calculate_final_score(cat_scores)
        assert final_score == 87



# ---------- API and Endpoint Integration Tests ----------

class TestAnalysisEndpoints:
    @pytest.fixture
    def mock_resume(self, db_session, registered_user):
        """Create a mock resume in DB."""
        # Query the user
        from app.models.user import User
        user = db_session.query(User).filter(User.email == registered_user["email"]).first()
        
        resume = Resume(
            user_id=user.id,
            title="Jane Doe Resume",
            original_filename="jane_doe.pdf",
            stored_filename="jane_doe_stored.pdf",
            file_type="application/pdf",
            file_size=1024,
            upload_status="success",
            storage_path="uploads/jane_doe_stored.pdf",
            parsed_text=TEST_RESUME_TEXT
        )
        db_session.add(resume)
        db_session.commit()
        db_session.refresh(resume)
        return resume

    def test_create_analysis_report_success(self, client, auth_headers, mock_resume):
        response = client.post(
            f"/api/v1/analysis/{mock_resume.id}",
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["resume_id"] == str(mock_resume.id)
        assert "ats_score" in data["data"]
        assert len(data["data"]["strengths"]) > 0
        assert len(data["data"]["suggestions"]) > 0

    def test_create_analysis_report_not_found(self, client, auth_headers):
        random_uuid = uuid4()
        response = client.post(
            f"/api/v1/analysis/{random_uuid}",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()

    def test_get_analyses_list(self, client, auth_headers, mock_resume, db_session):
        # Create a report first
        client.post(f"/api/v1/analysis/{mock_resume.id}", headers=auth_headers)
        
        response = client.get("/api/v1/analysis", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["data"][0]["resume_id"] == str(mock_resume.id)

    def test_get_analysis_details(self, client, auth_headers, mock_resume):
        # Create
        create_resp = client.post(f"/api/v1/analysis/{mock_resume.id}", headers=auth_headers)
        report_id = create_resp.json()["data"]["id"]

        # Get details
        response = client.get(f"/api/v1/analysis/{report_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == report_id
        assert data["data"]["ats_score"] == create_resp.json()["data"]["ats_score"]

    def test_delete_analysis_report(self, client, auth_headers, mock_resume):
        # Create
        create_resp = client.post(f"/api/v1/analysis/{mock_resume.id}", headers=auth_headers)
        report_id = create_resp.json()["data"]["id"]

        # Delete
        response = client.delete(f"/api/v1/analysis/{report_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify not found
        get_resp = client.get(f"/api/v1/analysis/{report_id}", headers=auth_headers)
        assert get_resp.status_code == 404
