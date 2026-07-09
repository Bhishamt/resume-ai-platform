import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import BadRequestError

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def validate_file(file: UploadFile) -> None:
    """Validate file extension, MIME type, and size to secure uploads."""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    
    # 1. Validate extension
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestError(f"Unsupported file extension: {ext}. Only PDF and DOCX are allowed.")
    
    # 2. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise BadRequestError(f"Unsupported MIME type: {file.content_type}. Only PDF and DOCX are allowed.")

    # 3. Validate file size (via file descriptor size check, if possible)
    # Since UploadFile might be a SpooledTemporaryFile, we check size via seek/tell
    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        if size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise BadRequestError(f"File size exceeds the limit of {max_mb:.1f} MB.")
    except Exception as e:
        if isinstance(e, BadRequestError):
            raise e
        # If size check fails, continue but let limit be validated during write or trust request headers
        pass

def save_file(file: UploadFile, user_id: uuid.UUID) -> tuple[str, str]:
    """Save upload file to a user-specific folder with a unique name.

    Returns:
        tuple[str, str]: (stored_filename, absolute_storage_path)
    """
    # Validate file parameters
    validate_file(file)

    # Prevent path traversal: secure folder layout
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    user_dir = (upload_dir / str(user_id)).resolve()

    # Ensure directories exist
    user_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique stored name
    original_filename = file.filename or "resume"
    ext = os.path.splitext(original_filename)[1].lower()
    stored_filename = f"{uuid.uuid4()}{ext}"
    
    storage_path = user_dir / stored_filename

    # Double check path traversal safety
    if not str(storage_path.resolve()).startswith(str(upload_dir)):
        raise BadRequestError("Path traversal attempt detected.")

    # Write file content
    try:
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise BadRequestError(f"Failed to write file to storage: {str(e)}")

    return stored_filename, str(storage_path)

def delete_file(storage_path: str) -> None:
    """Delete a file from disk if it exists."""
    path = Path(storage_path).resolve()
    # Check that we only delete files inside the configured upload directory
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    if not str(path).startswith(str(upload_dir)):
        # Prevent deletion outside the sandbox
        return
        
    if path.is_file():
        try:
            path.unlink()
        except OSError:
            # Log issue but don't fail transaction
            pass
