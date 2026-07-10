import pytest
from uuid import uuid4
from fastapi import status
from app.services.job_matching.similarity_engine import SimilarityEngine
from app.services.job_matching.skill_matcher import SkillMatcher
from app.services.job_matching.keyword_matcher import KeywordMatcher
from app.services.job_matching.experience_matcher import ExperienceMatcher
from app.services.job_matching.education_matcher import EducationMatcher
from app.services.job_matching.matching_engine import MatchingEngine
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.job_match import JobMatch

TEST_RESUME_TEXT = """
Jane Doe
jane.doe@example.com
(555) 555-5555

Professional Summary
Senior Software Engineer with 6 years of experience in backend development, distributed systems, and cloud architecture.

Technical Skills
Python, Javascript, React, SQL, Docker, AWS, Git, FastAPI, CI/CD, HTML, CSS, Kubernetes, PostgreSQL

Work Experience
Senior Software Engineer | Tech Solutions (2020 - Present)
- Built scalable backends using FastAPI and Docker.
- Integrated CI/CD pipelines to automate deployment on AWS.

Education
Bachelor of Science in Computer Science
University of Tech (2015 - 2019)
"""

TEST_JD_DESCRIPTION = """
We are looking for a Senior Software Engineer to build scalable backend systems.
Required Skills: Python, FastAPI, Docker, Kubernetes.
Preferred Skills: AWS, PostgreSQL, React.
Education: Bachelor's degree in Computer Science.
Experience: 5+ years of experience.
"""

class TestJobMatchingEngine:
    def test_similarity_engine(self):
        doc1 = "Python developer with experience in FastAPI"
        doc2 = "FastAPI developer with experience in Python"
        score = SimilarityEngine.calculate_similarity(doc1, doc2)
        assert score > 0.5
        assert score <= 1.0

        empty_score = SimilarityEngine.calculate_similarity("", doc2)
        assert empty_score == 0.0

    def test_skill_matcher(self):
        req = ["Python", "FastAPI", "Docker", "Kubernetes", "Golang"]
        pref = ["AWS", "PostgreSQL", "React", "Ruby"]
        res = SkillMatcher.match_skills(TEST_RESUME_TEXT, req, pref)
        
        assert "Python" in res["matching_skills"]
        assert "FastAPI" in res["matching_skills"]
        assert "Golang" in res["missing_preferred"] or "Golang" in res["missing_skills"]
        assert res["score"] > 50
        assert len(res["reasons"]) > 0

    def test_keyword_matcher(self):
        res = KeywordMatcher.match_keywords(TEST_RESUME_TEXT, "Senior Software Engineer", TEST_JD_DESCRIPTION)
        assert "Python" in res["matching_keywords"]
        assert "FastAPI" in res["matching_keywords"]
        assert res["score"] > 50

    def test_experience_matcher(self):
        # Requires 5 years, candidate has 6 years (2020 to present = 6 years)
        res = ExperienceMatcher.match_experience(TEST_RESUME_TEXT, "5+ years", "Senior Software Engineer")
        assert res["candidate_years"] >= 5
        assert res["score"] == 100

        # Mismatch seniority test
        res_junior = ExperienceMatcher.match_experience("Developer with 2 years of experience", "5+ years", "Senior Lead Engineer")
        assert res_junior["score"] < 100
        assert any("Seniority mismatch" in r["rule"] for r in res_junior["reasons"])

    def test_education_matcher(self):
        res = EducationMatcher.match_education(TEST_RESUME_TEXT, "Bachelor's degree in Computer Science")
        assert res["score"] == 100

        # Lower degree test
        res_low = EducationMatcher.match_education(TEST_RESUME_TEXT, "PhD in Computer Science")
        assert res_low["score"] < 100

    def test_matching_engine_integration(self):
        res = MatchingEngine.match_resume_to_job(
            resume_text=TEST_RESUME_TEXT,
            job_title="Senior Software Engineer",
            job_description=TEST_JD_DESCRIPTION,
            required_skills=["Python", "FastAPI", "Docker", "Kubernetes"],
            preferred_skills=["AWS", "PostgreSQL"],
            required_experience="5 years",
            education_requirement="Bachelor's in Computer Science"
        )
        assert res["overall_match"] > 70
        assert "Skills" in res["score_explanations"]
        assert "Experience" in res["score_explanations"]
        assert "reasons" in res["score_explanations"]["Skills"]

# ---------- API Integration Tests ----------

class TestJobMatchingEndpoints:
    @pytest.fixture
    def mock_resume(self, db_session, registered_user):
        from app.models.user import User
        user = db_session.query(User).filter(User.email == registered_user["email"]).first()
        
        resume = Resume(
            user_id=user.id,
            title="Matching Resume",
            original_filename="resume.pdf",
            stored_filename="resume_stored.pdf",
            file_type="application/pdf",
            file_size=1024,
            upload_status="success",
            storage_path="uploads/resume_stored.pdf",
            parsed_text=TEST_RESUME_TEXT
        )
        db_session.add(resume)
        db_session.commit()
        db_session.refresh(resume)
        return resume

    def test_job_match_lifecycle(self, client, auth_headers, mock_resume):
        # 1. Post a new match
        payload = {
            "resume_id": str(mock_resume.id),
            "job_description": {
                "title": "Senior Backend Developer",
                "company": "FastTech",
                "location": "Remote",
                "employment_type": "Full-time",
                "description": TEST_JD_DESCRIPTION,
                "required_skills": ["Python", "FastAPI", "Docker"],
                "preferred_skills": ["AWS", "PostgreSQL"],
                "required_experience": "5 years",
                "education_requirement": "Bachelor's in Computer Science"
            }
        }
        
        response = client.post("/api/v1/job-matching", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "overall_match" in data["data"]
        match_id = data["data"]["id"]

        # 2. Get matches list
        list_resp = client.get("/api/v1/job-matching", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) >= 1

        # 3. Get specific match details
        details_resp = client.get(f"/api/v1/job-matching/{match_id}", headers=auth_headers)
        assert details_resp.status_code == 200
        assert details_resp.json()["data"]["overall_match"] == data["data"]["overall_match"]

        # 4. Delete specific match
        del_resp = client.delete(f"/api/v1/job-matching/{match_id}", headers=auth_headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True

        # 5. Verify deleted is gone
        verify_resp = client.get(f"/api/v1/job-matching/{match_id}", headers=auth_headers)
        assert verify_resp.status_code == 404
