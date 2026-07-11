from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models.ai_feedback import AIFeedback
from app.models.resume import Resume
from app.services.ai.ai_service import AIService
from app.services.ai.cache import ai_cache
from app.services.ai.groq_provider import GroqProvider
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.prompt_templates import PromptTemplate
from app.services.ai.response_parser import ResponseParser

# --- 1. Unit Tests for Provider Layer ---


@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_groq_provider_success(mock_post):
    # Mock successful response from Groq
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"overall_review": "Good resume"}'}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    }
    mock_post.return_value = mock_response

    provider = GroqProvider(api_key="test_key")
    result = await provider.generate_response(
        "User Prompt", "System instructions", json_mode=True
    )

    assert result["response"] == '{"overall_review": "Good resume"}'
    assert result["tokens"]["prompt_tokens"] == 100
    assert result["tokens"]["completion_tokens"] == 50
    assert result["tokens"]["total_tokens"] == 150
    assert result["response_time"] > 0


# --- 2. Unit Tests for Prompt Builder ---


def test_prompt_builder_success():
    tpl = PromptTemplate(
        name="test_prompt",
        version="1.0.0",
        variables=["var_a", "var_b"],
        template="Hello {var_a}, welcome to {var_b}.",
        expected_output="text",
    )
    variables = {"var_a": "John", "var_b": "ResumeAI"}
    prompt = PromptBuilder.build(tpl, variables)
    assert prompt == "Hello John, welcome to ResumeAI."


def test_prompt_builder_missing_variable():
    tpl = PromptTemplate(
        name="test_prompt",
        version="1.0.0",
        variables=["var_a", "var_b"],
        template="Hello {var_a}, welcome to {var_b}.",
        expected_output="text",
    )
    variables = {"var_a": "John"}
    with pytest.raises(ValueError) as exc_info:
        PromptBuilder.build(tpl, variables)
    assert "Missing required variables" in str(exc_info.value)


# --- 3. Unit Tests for Response Parser ---


def test_response_parser_clean_json():
    json_str = '{"overall_review": "Excellent"}'
    parsed = ResponseParser.parse_json(json_str)
    assert parsed["overall_review"] == "Excellent"


def test_response_parser_markdown_fences():
    json_str = '```json\n{"overall_review": "Excellent"}\n```'
    parsed = ResponseParser.parse_json(json_str)
    assert parsed["overall_review"] == "Excellent"


def test_response_parser_invalid_json():
    json_str = '{"overall_review": "Excellent"'
    with pytest.raises(ValueError) as exc_info:
        ResponseParser.parse_json(json_str)
    assert "not valid JSON" in str(exc_info.value)


# --- 4. Unit Tests for Cache ---


def test_ai_cache():
    ai_cache.clear()
    prompt = "Review this resume"
    provider = "GroqProvider"
    prompt_type = "resume_review"
    data = {"review": "Good"}

    assert ai_cache.get(prompt, provider, prompt_type) is None
    ai_cache.set(prompt, provider, prompt_type, data)
    assert ai_cache.get(prompt, provider, prompt_type) == data


# --- 5. Mock Provider for Service & API Tests ---


class MockProvider:
    async def generate_response(
        self, prompt: str, system_prompt: str = None, json_mode: bool = False
    ):
        # Determine response based on prompt type or keywords
        if "overall_review" in prompt:
            content = '{"overall_review": "Mocked review", "resume_improvements": ["Mocked improvement"], "better_summary": "Mocked summary", "better_skills": ["Mocked skill"], "better_experience": "Mocked experience", "better_projects": ["Mocked project"]}'
        elif "cover_letter" in prompt:
            content = '{"professional_cover_letter": "Mocked cover letter", "company_specific_version": "Mocked company letter", "ats_friendly_version": "Mocked ATS letter"}'
        elif "rewrite" in prompt:
            content = '{"stronger_bullet_points": ["Mocked bullet"], "better_action_verbs": ["Mocked verb"], "better_project_descriptions": ["Mocked description"]}'
        elif "technical_questions" in prompt:
            content = '{"technical_questions": [{"question": "Q1?", "suggested_answer": "A1"}], "hr_questions": [], "behavioral_questions": [], "resume_based_questions": []}'
        elif "learning_roadmap" in prompt:
            content = '{"learning_roadmap": ["Mocked path"], "missing_technologies": ["Mocked tech"], "certifications": ["Mocked cert"], "career_suggestions": ["Mocked suggestion"]}'
        else:
            content = "{}"

        return {
            "response": content,
            "tokens": {
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80,
            },
            "response_time": 0.1,
        }


# --- 6. Integration Tests for AIService ---


@pytest.fixture
def mock_ai_service():
    return AIService(provider=MockProvider())


def test_ai_service_review_resume(db_session, mock_ai_service):
    # Setup database elements
    user_id = uuid4()
    resume = Resume(
        id=uuid4(),
        user_id=user_id,
        title="Software Engineer Resume",
        original_filename="resume.pdf",
        stored_filename="resume_stored.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/path/to/resume",
        parsed_text="John Doe Software Engineer Python FastAPI React",
    )
    db_session.add(resume)
    db_session.commit()

    # Call service
    import asyncio

    result = asyncio.run(mock_ai_service.review_resume(db_session, user_id, resume.id))

    assert result["overall_review"] == "Mocked review"

    # Check DB feedback is created
    feedbacks = db_session.query(AIFeedback).all()
    assert len(feedbacks) == 1
    assert feedbacks[0].prompt_type == "resume_review"
    assert feedbacks[0].user_id == user_id
    assert feedbacks[0].resume_id == resume.id


# --- 7. API Endpoint Tests ---


@pytest.fixture(autouse=True)
def override_ai_service():
    # Override standard service with mock provider
    with patch(
        "app.api.v1.endpoints.ai.ai_service", AIService(provider=MockProvider())
    ):
        yield


def test_api_review_resume(client, db_session, registered_user, auth_headers):
    # Retrieve user from DB to get ID
    db_session.query(AIFeedback).first()

    # Add dummy Resume
    resume = Resume(
        id=uuid4(),
        user_id=uuid4(),  # updated in header
        title="Test Resume",
        original_filename="resume.pdf",
        stored_filename="resume_stored.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/path",
        parsed_text="Dummy Text",
    )
    # We must ensure the resume user_id matches registered_user's user_id. Let's find it.
    from app.utils.jwt_utils import decode_token

    token = auth_headers["Authorization"][7:]
    payload = decode_token(token)
    user_uuid = UUID(payload["sub"])
    resume.user_id = user_uuid

    db_session.add(resume)
    db_session.commit()

    response = client.post(
        "/api/v1/ai/review", json={"resume_id": str(resume.id)}, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["overall_review"] == "Mocked review"


def test_api_generate_cover_letter(client, db_session, auth_headers):
    from app.utils.jwt_utils import decode_token

    token = auth_headers["Authorization"][7:]
    payload = decode_token(token)
    user_uuid = UUID(payload["sub"])

    resume = Resume(
        id=uuid4(),
        user_id=user_uuid,
        title="Test Resume",
        original_filename="resume.pdf",
        stored_filename="resume_stored.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/path",
        parsed_text="Dummy Text",
    )
    db_session.add(resume)
    db_session.commit()

    response = client.post(
        "/api/v1/ai/cover-letter",
        json={
            "resume_id": str(resume.id),
            "company_name": "Google",
            "job_title": "Software Engineer",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["professional_cover_letter"] == "Mocked cover letter"


def test_api_get_delete_history(client, db_session, auth_headers):
    from app.utils.jwt_utils import decode_token

    token = auth_headers["Authorization"][7:]
    payload = decode_token(token)
    user_uuid = UUID(payload["sub"])

    feedback = AIFeedback(
        id=uuid4(),
        user_id=user_uuid,
        provider="MockProvider",
        prompt_type="resume_review",
        prompt_version="1.0.0",
        response='{"overall_review": "Good"}',
        token_usage={"prompt_tokens": 10},
        response_time=0.1,
    )
    db_session.add(feedback)
    db_session.commit()

    # GET history
    get_resp = client.get("/api/v1/ai/history", headers=auth_headers)
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == str(feedback.id)

    # DELETE history
    del_resp = client.delete(f"/api/v1/ai/history/{feedback.id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Verify deletion in DB
    assert db_session.query(AIFeedback).count() == 0
