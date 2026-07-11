import logging
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.exceptions import (AuthorizationError, BadRequestError,
                                 NotFoundError)
from app.models.resume import Resume
from app.models.upload_history import UploadHistory
from app.services import storage_service
from app.services.parser.parser_factory import ParserFactory

logger = logging.getLogger(__name__)


def upload_resume(
    db: Session, file: UploadFile, user_id: UUID, title: str | None = None
) -> Resume:
    """Save upload to disk, parse raw text, store DB entry, and log history."""
    storage_service.validate_file(file)
    # 1. Save file securely to disk
    stored_filename, storage_path = storage_service.save_file(file, user_id)

    # Calculate file size
    try:
        file_size = file.size if hasattr(file, "size") and file.size else 0
        if not file_size:
            # Fallback size check from disk
            import os

            file_size = os.path.getsize(storage_path)
    except Exception:
        file_size = 0

    # 2. Parse file
    parsed_text = None
    upload_status = "success"
    try:
        parser = ParserFactory.get_parser(file.filename or "", file.content_type)
        parsed_data = parser.parse(storage_path)
        parsed_text = parsed_data.get("raw_text")
    except Exception as e:
        logger.error(f"Failed to parse resume: {str(e)}")
        upload_status = "failed"

    # Create Resume DB entry
    resume = Resume(
        user_id=user_id,
        title=title or file.filename or "Untitled Resume",
        original_filename=file.filename or "resume",
        stored_filename=stored_filename,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        upload_status=upload_status,
        storage_path=storage_path,
        parsed_text=parsed_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Log action to history
    history = UploadHistory(
        user_id=user_id,
        resume_id=resume.id,
        action="upload",
    )
    db.add(history)
    db.commit()

    logger.info(f"Resume {resume.id} uploaded successfully by user {user_id}.")
    return resume


def get_resumes_paginated(
    db: Session, user_id: UUID, page: int = 1, limit: int = 10
) -> tuple[list[Resume], int]:
    """Retrieve user's resumes with offset pagination.

    Returns:
        tuple[list[Resume], int]: (resumes_list, total_count)
    """
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    query = db.query(Resume).filter(Resume.user_id == user_id)
    total_count = query.count()

    resumes = (
        query.order_by(desc(Resume.upload_date))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return resumes, total_count


def get_resume_by_id(db: Session, resume_id: UUID, user_id: UUID) -> Resume:
    """Retrieve a single resume details after verifying user ownership."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise NotFoundError("Resume not found.")

    if resume.user_id != user_id:
        raise AuthorizationError("You do not have permission to access this resume.")

    return resume


def delete_resume(db: Session, resume_id: UUID, user_id: UUID) -> None:
    """Delete a resume from DB and secure file storage, logging action to history."""
    resume = get_resume_by_id(db, resume_id, user_id)

    # 1. Delete physical file from disk
    storage_service.delete_file(resume.storage_path)

    # 2. Record deletion to history before Cascade delete triggers
    history = UploadHistory(
        user_id=user_id,
        resume_id=resume.id,
        action="delete",
    )
    db.add(history)
    db.commit()

    # 3. Delete DB record (Cascade deletes related histories)
    db.delete(resume)
    db.commit()

    logger.info(f"Resume {resume_id} deleted by user {user_id}.")


def update_resume_title(
    db: Session, resume_id: UUID, user_id: UUID, title: str
) -> Resume:
    """Update title metadata for a resume."""
    if not title or not title.strip():
        raise BadRequestError("Title cannot be empty.")

    resume = get_resume_by_id(db, resume_id, user_id)
    resume.title = title.strip()
    db.commit()
    db.refresh(resume)
    return resume


def replace_resume(
    db: Session, resume_id: UUID, file: UploadFile, user_id: UUID
) -> Resume:
    """Replace physical file and metadata of an existing resume with a new upload."""
    storage_service.validate_file(file)
    resume = get_resume_by_id(db, resume_id, user_id)

    # 1. Securely save the new file to disk first
    stored_filename, storage_path = storage_service.save_file(file, user_id)

    # Calculate new size
    try:
        file_size = file.size if hasattr(file, "size") and file.size else 0
        if not file_size:
            import os

            file_size = os.path.getsize(storage_path)
    except Exception:
        file_size = 0

    # 2. Parse new file
    parsed_text = None
    upload_status = "success"
    try:
        parser = ParserFactory.get_parser(file.filename or "", file.content_type)
        parsed_data = parser.parse(storage_path)
        parsed_text = parsed_data.get("raw_text")
    except Exception as e:
        logger.error(f"Failed to parse replaced resume: {str(e)}")
        upload_status = "failed"

    # 3. Delete old physical file from disk
    storage_service.delete_file(resume.storage_path)

    # 4. Update model fields
    resume.original_filename = file.filename or "resume"
    resume.stored_filename = stored_filename
    resume.file_type = file.content_type or "application/octet-stream"
    resume.file_size = file_size
    resume.upload_status = upload_status
    resume.storage_path = storage_path
    resume.parsed_text = parsed_text

    db.commit()
    db.refresh(resume)

    # 5. Log replace to history
    history = UploadHistory(
        user_id=user_id,
        resume_id=resume.id,
        action="replace",
    )
    db.add(history)
    db.commit()

    logger.info(f"Resume {resume_id} replaced successfully by user {user_id}.")
    return resume


def get_upload_history(db: Session, user_id: UUID) -> list[UploadHistory]:
    """Retrieve history logs for the user."""
    return (
        db.query(UploadHistory)
        .filter(UploadHistory.user_id == user_id)
        .order_by(desc(UploadHistory.timestamp))
        .all()
    )
