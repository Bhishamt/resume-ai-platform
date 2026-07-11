"""AI processing background tasks.

Routes heavy LLM calls and job matching through the AI queue so API
endpoints return task IDs immediately rather than blocking for 30+ seconds.
"""

import logging
from uuid import UUID

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.ai_tasks.run_ai_analysis_async",
    queue="ai",
    max_retries=2,
    default_retry_delay=120,
    soft_time_limit=300,  # 5 min soft limit
    time_limit=360,  # 6 min hard limit
)
def run_ai_analysis_async(
    self,
    resume_id: str,
    user_id: str,
    request_type: str,
    extra_context: dict | None = None,
) -> dict:
    """Run an AI analysis request for a resume in the background.

    Args:
        resume_id: Target resume UUID string.
        user_id: Requesting user UUID string.
        request_type: Type of AI task ('review', 'rewrite', 'cover_letter',
                       'summary', 'interview_questions').
        extra_context: Optional dict with supplementary data (job_description, etc.)

    Returns:
        dict with 'status', 'resume_id', and 'feedback_id'.
    """
    from app.database.base import SessionLocal
    from app.models.resume import Resume
    from app.services.ai import ai_service

    logger.info("run_ai_analysis_async: type=%s resume_id=%s", request_type, resume_id)

    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == UUID(resume_id)).first()
        if not resume:
            return {"status": "not_found", "resume_id": resume_id}

        if not resume.parsed_text:
            return {"status": "no_parsed_text", "resume_id": resume_id}

        try:
            feedback = ai_service.generate_feedback(
                db=db,
                resume=resume,
                user_id=UUID(user_id),
                request_type=request_type,
                extra_context=extra_context or {},
            )
            logger.info(
                "AI analysis complete: type=%s resume_id=%s feedback_id=%s",
                request_type,
                resume_id,
                feedback.id,
            )
            return {
                "status": "complete",
                "resume_id": resume_id,
                "feedback_id": str(feedback.id),
                "request_type": request_type,
            }
        except Exception as exc:
            logger.error("AI analysis failed: %s — %s", resume_id, exc)
            raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="app.tasks.ai_tasks.run_job_match_async",
    queue="ai",
    max_retries=2,
    default_retry_delay=60,
    soft_time_limit=180,
    time_limit=240,
)
def run_job_match_async(
    self,
    resume_id: str,
    user_id: str,
    job_description_id: str,
) -> dict:
    """Run job-resume matching analysis in the background.

    Args:
        resume_id: UUID string of the resume to match.
        user_id: UUID string of the requesting user.
        job_description_id: UUID string of the JobDescription record.

    Returns:
        dict with 'status', 'match_id', and 'match_score'.
    """
    from app.database.base import SessionLocal
    from app.models.job_description import JobDescription
    from app.models.resume import Resume
    from app.services.job_matching_service import run_matching

    logger.info(
        "run_job_match_async: resume_id=%s jd_id=%s",
        resume_id,
        job_description_id,
    )

    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == UUID(resume_id)).first()
        job_desc = (
            db.query(JobDescription)
            .filter(JobDescription.id == UUID(job_description_id))
            .first()
        )

        if not resume or not job_desc:
            return {"status": "not_found", "resume_id": resume_id}

        try:
            match = run_matching(
                db=db, resume=resume, job_description=job_desc, user_id=UUID(user_id)
            )
            logger.info(
                "Job match complete: match_id=%s score=%.1f",
                match.id,
                match.match_score,
            )
            return {
                "status": "complete",
                "resume_id": resume_id,
                "match_id": str(match.id),
                "match_score": match.match_score,
            }
        except Exception as exc:
            logger.error("Job matching failed: resume_id=%s — %s", resume_id, exc)
            raise self.retry(exc=exc)

    finally:
        db.close()
