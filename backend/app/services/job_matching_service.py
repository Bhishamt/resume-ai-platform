import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import (AuthorizationError, BadRequestError,
                                 NotFoundError)
from app.models.job_description import JobDescription
from app.models.job_match import JobMatch
from app.schemas.job_matching import JobDescriptionCreate
from app.services import resume_service
from app.services.job_matching.matching_engine import MatchingEngine
from app.services.parser.parser_factory import ParserFactory

logger = logging.getLogger(__name__)


def create_job_description(
    db: Session, user_id: UUID, obj_in: JobDescriptionCreate
) -> JobDescription:
    """Save a job description to the database."""
    job_desc = JobDescription(
        user_id=user_id,
        title=obj_in.title,
        company=obj_in.company,
        location=obj_in.location,
        employment_type=obj_in.employment_type,
        description=obj_in.description,
        required_skills=obj_in.required_skills,
        preferred_skills=obj_in.preferred_skills,
        required_experience=obj_in.required_experience,
        education_requirement=obj_in.education_requirement,
    )
    db.add(job_desc)
    db.commit()
    db.refresh(job_desc)
    return job_desc


def get_job_description(db: Session, jd_id: UUID, user_id: UUID) -> JobDescription:
    """Fetch a job description and verify ownership."""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise NotFoundError("Job description not found.")
    if jd.user_id != user_id:
        raise AuthorizationError(
            "You do not have permission to access this job description."
        )
    return jd


def get_user_job_descriptions(db: Session, user_id: UUID) -> list[JobDescription]:
    """Fetch all job descriptions created by the user."""
    return (
        db.query(JobDescription)
        .filter(JobDescription.user_id == user_id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )


def run_job_match(
    db: Session,
    user_id: UUID,
    resume_id: UUID,
    job_description_id: UUID = None,
    job_description_in: JobDescriptionCreate = None,
) -> JobMatch:
    """Trigger the matching engine on a resume and job description, then save the report."""
    # 1. Fetch resume and verify ownership
    resume = resume_service.get_resume_by_id(db, resume_id, user_id)

    # 2. Fetch or create Job Description
    if job_description_id:
        jd = get_job_description(db, job_description_id, user_id)
    elif job_description_in:
        jd = create_job_description(db, user_id, job_description_in)
    else:
        raise BadRequestError(
            "Must provide either an existing job_description_id or raw job_description details."
        )

    # 3. Retrieve or cache parsed resume text
    parsed_text = resume.parsed_text
    if not parsed_text:
        logger.info(f"Parsing resume on-the-fly for job matching: {resume.id}")
        try:
            parser = ParserFactory.get_parser(
                resume.original_filename, resume.file_type
            )
            parsed_data = parser.parse(resume.storage_path)
            parsed_text = parsed_data.get("raw_text", "")

            # Cache the parsed text back to resume
            resume.parsed_text = parsed_text
            db.add(resume)
            db.commit()
            db.refresh(resume)
        except Exception as e:
            logger.error(f"Failed to parse resume file {resume.storage_path}: {str(e)}")
            parsed_text = ""

    if not parsed_text or not parsed_text.strip():
        raise BadRequestError(
            "Unable to match. The selected resume contains no readable text content."
        )

    # 4. Run matching engine
    match_res = MatchingEngine.match_resume_to_job(
        resume_text=parsed_text,
        job_title=jd.title,
        job_description=jd.description,
        required_skills=jd.required_skills,
        preferred_skills=jd.preferred_skills,
        required_experience=jd.required_experience,
        education_requirement=jd.education_requirement,
    )

    # 5. Save match report
    job_match = JobMatch(
        resume_id=resume.id,
        job_description_id=jd.id,
        overall_match=match_res["overall_match"],
        skill_match=match_res["skill_match"],
        experience_match=match_res["experience_match"],
        education_match=match_res["education_match"],
        keyword_match=match_res["keyword_match"],
        missing_skills=match_res["missing_skills"],
        matching_skills=match_res["matching_skills"],
        missing_keywords=match_res["missing_keywords"],
        recommendations=match_res["recommendations"],
        score_explanations=match_res["score_explanations"],
    )
    db.add(job_match)
    db.commit()
    db.refresh(job_match)

    # Eager load the description relationship
    job_match.job_description = jd
    return job_match


def get_job_match(db: Session, match_id: UUID, user_id: UUID) -> JobMatch:
    """Fetch a job match report and verify ownership."""
    match = db.query(JobMatch).filter(JobMatch.id == match_id).first()
    if not match:
        raise NotFoundError("Job match report not found.")

    # Verify ownership through the associated resume
    if match.resume.user_id != user_id:
        raise AuthorizationError(
            "You do not have permission to access this match report."
        )
    return match


def get_user_job_matches(
    db: Session, user_id: UUID, skip: int = 0, limit: int = 100
) -> list[JobMatch]:
    """Fetch all match reports belonging to the user's resumes (paginated)."""
    return (
        db.query(JobMatch)
        .join(JobMatch.resume)
        .filter(JobMatch.resume.has(user_id=user_id))
        .order_by(JobMatch.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_job_match(db: Session, match_id: UUID, user_id: UUID) -> None:
    """Delete a match report and verify ownership."""
    match = get_job_match(db, match_id, user_id)
    db.delete(match)
    db.commit()
