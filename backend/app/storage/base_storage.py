"""Abstract base class for file storage providers.

All storage implementations must implement this interface so they can
be swapped without changing any business logic.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class BaseStorage(ABC):
    """Storage provider interface."""

    @abstractmethod
    def save(self, file_obj, filename: str, user_id: UUID) -> tuple[str, str]:
        """Persist a file.

        Args:
            file_obj: A file-like object (FastAPI UploadFile.file).
            filename:  Original filename — used for extension detection.
            user_id:   Owner of the file — used for path namespacing.

        Returns:
            (stored_filename, storage_path_or_key)
            - stored_filename: UUID-based name stored in the DB.
            - storage_path_or_key: Absolute path (local) or S3 key (cloud).
        """
        ...

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        """Remove a file from storage.

        Must silently succeed if the file does not exist.
        """
        ...

    @abstractmethod
    def get_url(self, storage_path: str) -> str:
        """Return a URL to access the file.

        For local storage this is a relative path.
        For S3 this is a pre-signed URL or CDN URL.
        """
        ...

    def validate_file(self, filename: str, content_type: str | None, size: int) -> None:
        """Validate file before storage.

        Raises BadRequestError for invalid files.
        Default implementation enforces PDF/DOCX + size limit.
        Override in subclasses to add provider-specific checks.
        """
        import os

        from app.core.config import settings
        from app.core.exceptions import BadRequestError

        ALLOWED_EXTENSIONS = {".pdf", ".docx"}
        ALLOWED_MIME_TYPES = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise BadRequestError(
                f"Unsupported file extension: {ext}. Only PDF and DOCX are allowed."
            )

        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise BadRequestError(
                f"Unsupported MIME type: {content_type}. Only PDF and DOCX are allowed."
            )

        if size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise BadRequestError(f"File size exceeds the limit of {max_mb:.1f} MB.")
