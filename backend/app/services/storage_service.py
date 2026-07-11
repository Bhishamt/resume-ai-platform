"""Storage service — thin façade over the pluggable storage backend.

Existing callers import from this module unchanged. The backend is selected
by STORAGE_BACKEND env var (local | s3) via the storage factory.

Public API (preserved):
    validate_file(file: UploadFile) -> None
    save_file(file: UploadFile, user_id: UUID) -> tuple[str, str]
    delete_file(storage_path: str) -> None
"""

import logging
import os
from uuid import UUID

from fastapi import UploadFile

from app.storage.storage_factory import get_storage

logger = logging.getLogger(__name__)


def validate_file(file: UploadFile) -> None:
    """Validate file extension, MIME type, and size.

    Delegates to the storage provider's validation so rules are consistent
    regardless of whether files go to local disk or S3.
    """
    size = _probe_size(file)
    storage = get_storage()
    storage.validate_file(
        filename=file.filename or "",
        content_type=file.content_type,
        size=size,
    )


def save_file(file: UploadFile, user_id: UUID) -> tuple[str, str]:
    """Save an uploaded file using the configured storage backend.

    Returns:
        (stored_filename, storage_path_or_key)
    """
    storage = get_storage()
    stored_filename, storage_path = storage.save(
        file_obj=file.file,
        filename=file.filename or "resume",
        user_id=user_id,
    )
    logger.info(
        "save_file: user=%s stored_as=%s backend=%s",
        user_id,
        stored_filename,
        type(storage).__name__,
    )
    return stored_filename, storage_path


def delete_file(storage_path: str) -> None:
    """Delete a file from the configured storage backend.

    Silently succeeds if the file does not exist.
    """
    if not storage_path:
        return
    storage = get_storage()
    storage.delete(storage_path)
    logger.info("delete_file: %s", storage_path)


def get_file_url(storage_path: str) -> str:
    """Return a URL to access a stored file.

    For local storage: a relative API path.
    For S3: a pre-signed URL.
    """
    storage = get_storage()
    return storage.get_url(storage_path)


def _probe_size(file: UploadFile) -> int:
    """Determine file size from an UploadFile without consuming the stream."""
    try:
        pos = file.file.tell()
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(pos)
        return size
    except Exception:
        return 0
