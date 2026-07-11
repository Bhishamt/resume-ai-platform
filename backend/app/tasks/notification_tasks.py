"""Email notification background tasks.

All email sending is handled asynchronously via Celery so that API
responses are never blocked by SMTP latency or provider failures.
"""

import asyncio
import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_welcome_email_task",
    queue="email",
    max_retries=3,
    default_retry_delay=30,
)
def send_welcome_email_task(self, user_email: str, full_name: str) -> dict:
    """Send a welcome email to a newly registered user."""
    from app.services.email.email_service import get_email_service

    logger.info("send_welcome_email_task: to=%s", user_email)
    try:
        service = get_email_service()
        _run_async(service.send_welcome(to_email=user_email, full_name=full_name))
        return {"status": "sent", "to": user_email, "type": "welcome"}
    except Exception as exc:
        logger.error("Welcome email failed for %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_verification_email_task",
    queue="email",
    max_retries=3,
    default_retry_delay=30,
)
def send_verification_email_task(
    self, user_email: str, full_name: str, verification_token: str
) -> dict:
    """Send email verification link."""
    from app.services.email.email_service import get_email_service

    logger.info("send_verification_email_task: to=%s", user_email)
    try:
        service = get_email_service()
        _run_async(
            service.send_verification(
                to_email=user_email,
                full_name=full_name,
                token=verification_token,
            )
        )
        return {"status": "sent", "to": user_email, "type": "verification"}
    except Exception as exc:
        logger.error("Verification email failed for %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_password_reset_email_task",
    queue="email",
    max_retries=3,
    default_retry_delay=30,
)
def send_password_reset_email_task(
    self, user_email: str, full_name: str, reset_token: str
) -> dict:
    """Send password reset link via email."""
    from app.services.email.email_service import get_email_service

    logger.info("send_password_reset_email_task: to=%s", user_email)
    try:
        service = get_email_service()
        _run_async(
            service.send_password_reset(
                to_email=user_email,
                full_name=full_name,
                token=reset_token,
            )
        )
        return {"status": "sent", "to": user_email, "type": "password_reset"}
    except Exception as exc:
        logger.error("Password reset email failed for %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_analysis_complete_task",
    queue="email",
    max_retries=3,
    default_retry_delay=30,
)
def send_analysis_complete_task(
    self,
    user_email: str,
    full_name: str,
    resume_title: str,
    ats_score: float,
    resume_id: str,
) -> dict:
    """Notify user that their resume analysis is ready."""
    from app.services.email.email_service import get_email_service

    logger.info("send_analysis_complete_task: to=%s resume_id=%s", user_email, resume_id)
    try:
        service = get_email_service()
        _run_async(
            service.send_analysis_complete(
                to_email=user_email,
                full_name=full_name,
                resume_title=resume_title,
                ats_score=ats_score,
                resume_id=resume_id,
            )
        )
        return {"status": "sent", "to": user_email, "type": "analysis_complete"}
    except Exception as exc:
        logger.error("Analysis complete email failed for %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_job_match_complete_task",
    queue="email",
    max_retries=3,
    default_retry_delay=30,
)
def send_job_match_complete_task(
    self,
    user_email: str,
    full_name: str,
    job_title: str,
    match_score: float,
    match_id: str,
) -> dict:
    """Notify user that their job match analysis is ready."""
    from app.services.email.email_service import get_email_service

    logger.info("send_job_match_complete_task: to=%s match_id=%s", user_email, match_id)
    try:
        service = get_email_service()
        _run_async(
            service.send_job_match_complete(
                to_email=user_email,
                full_name=full_name,
                job_title=job_title,
                match_score=match_score,
                match_id=match_id,
            )
        )
        return {"status": "sent", "to": user_email, "type": "job_match_complete"}
    except Exception as exc:
        logger.error("Job match email failed for %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_weekly_summary_task",
    queue="email",
    max_retries=2,
    default_retry_delay=300,
)
def send_weekly_summary_task(
    self,
    user_email: str,
    full_name: str,
    summary_data: dict,
) -> dict:
    """Send weekly career progress summary email."""
    from app.services.email.email_service import get_email_service

    logger.info("send_weekly_summary_task: to=%s", user_email)
    try:
        service = get_email_service()
        _run_async(
            service.send_weekly_summary(
                to_email=user_email,
                full_name=full_name,
                summary_data=summary_data,
            )
        )
        return {"status": "sent", "to": user_email, "type": "weekly_summary"}
    except Exception as exc:
        logger.error("Weekly summary email failed for %s: %s", user_email, exc)
        raise self.retry(exc=exc)
