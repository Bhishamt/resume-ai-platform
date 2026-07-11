"""Resume processing background tasks.

Offloads CPU-bound parsing and ATS analysis from the API request cycle
so uploads return immediately while processing continues asynchronously.
"""

import logging
from uuid import UUID

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.resume_tasks.parse_resume_async",
    queue="default",
    max_retries=3,
    default_retry_delay=30,
)
def parse_resume_async(self, resume_id: str, storage_path: str, filename: str) -> dict:
    """Parse a resume file and update the database with extracted text.

    Args:
        resume_id: UUID string of the Resume record to update.
        storage_path: Absolute path (local) or S3 key of the uploaded file.
        filename: Original filename for MIME-type detection.

    Returns:
        dict with 'status' and 'resume_id'.
    """
    from app.database.base import SessionLocal
    from app.models.resume import Resume
    from app.services.parser.parser_factory import ParserFactory

    logger.info("parse_resume_async started: resume_id=%s", resume_id)

    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == UUID(resume_id)).first()
        if not resume:
            logger.warning("Resume not found for parsing: %s", resume_id)
            return {"status": "not_found", "resume_id": resume_id}

        # Mark as processing
        resume.upload_status = "processing"
        db.commit()

        try:
            parser = ParserFactory.get_parser(filename, None)
            parsed_data = parser.parse(storage_path)
            resume.parsed_text = parsed_data.get("raw_text", "")
            resume.upload_status = "parsed"
            db.commit()
            logger.info("Resume parsed successfully: %s", resume_id)
            return {"status": "parsed", "resume_id": resume_id}
        except Exception as exc:
            resume.upload_status = "parse_failed"
            db.commit()
            logger.error("Resume parsing failed: %s — %s", resume_id, exc)
            raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="app.tasks.resume_tasks.trigger_ats_analysis_async",
    queue="default",
    max_retries=3,
    default_retry_delay=60,
)
def trigger_ats_analysis_async(self, resume_id: str, user_id: str) -> dict:
    """Run full ATS analysis for a resume in the background.

    Args:
        resume_id: UUID string of the Resume to analyse.
        user_id: UUID string of the owning user.

    Returns:
        dict with 'status' and 'report_id' on success.
    """
    from app.database.base import SessionLocal
    from app.models.resume import Resume
    from app.services.ats import ats_service

    logger.info("trigger_ats_analysis_async: resume_id=%s", resume_id)

    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == UUID(resume_id)).first()
        if not resume:
            return {"status": "not_found", "resume_id": resume_id}

        if not resume.parsed_text:
            logger.warning("No parsed text for ATS analysis: %s", resume_id)
            return {"status": "no_text", "resume_id": resume_id}

        try:
            report = ats_service.run_ats_analysis(db, resume, UUID(user_id))
            logger.info(
                "ATS analysis complete: resume_id=%s report_id=%s", resume_id, report.id
            )
            return {
                "status": "complete",
                "resume_id": resume_id,
                "report_id": str(report.id),
            }
        except Exception as exc:
            logger.error("ATS analysis failed: %s — %s", resume_id, exc)
            raise self.retry(exc=exc)

    finally:
        db.close()
