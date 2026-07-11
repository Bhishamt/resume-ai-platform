"""Local filesystem storage provider.

Files are stored under UPLOAD_DIR / {user_id} / {uuid}{ext}.
Protects against path traversal attacks by resolving and validating paths.
"""

import logging
import os
import shutil
import uuid
from pathlib import Path
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.storage.base_storage import BaseStorage

logger = logging.getLogger(__name__)


class LocalStorage(BaseStorage):
    """Store files on the local filesystem."""

    def __init__(self, upload_dir: str | None = None) -> None:
        self._upload_dir = Path(upload_dir or settings.UPLOAD_DIR).resolve()

    def save(self, file_obj, filename: str, user_id: UUID) -> tuple[str, str]:
        """Save a file to UPLOAD_DIR/{user_id}/{uuid}{ext}.

        Returns:
            (stored_filename, absolute_storage_path)
        """
        # Validate before writing
        content_type = getattr(file_obj, "content_type", None)
        size = self._get_size(file_obj)
        self.validate_file(filename, content_type, size)

        ext = os.path.splitext(filename)[1].lower()
        stored_filename = f"{uuid.uuid4()}{ext}"

        user_dir = (self._upload_dir / str(user_id)).resolve()

        # Guard against path traversal
        if not str(user_dir).startswith(str(self._upload_dir)):
            raise BadRequestError("Path traversal attempt detected.")

        user_dir.mkdir(parents=True, exist_ok=True)
        storage_path = user_dir / stored_filename

        try:
            # Reset file pointer before reading
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            with open(storage_path, "wb") as buffer:
                shutil.copyfileobj(file_obj, buffer)
        except OSError as exc:
            raise BadRequestError(f"Failed to write file to storage: {exc}") from exc

        logger.info("LocalStorage.save: %s → %s", filename, storage_path)
        return stored_filename, str(storage_path)

    def delete(self, storage_path: str) -> None:
        """Delete a file from the local filesystem.

        Silently ignores missing files. Refuses to delete outside UPLOAD_DIR.
        """
        path = Path(storage_path).resolve()
        if not str(path).startswith(str(self._upload_dir)):
            logger.warning(
                "LocalStorage.delete blocked — path outside upload dir: %s", path
            )
            return

        if path.is_file():
            try:
                path.unlink()
                logger.info("LocalStorage.delete: %s", path)
            except OSError as exc:
                logger.warning("LocalStorage.delete failed for %s: %s", path, exc)

    def get_url(self, storage_path: str) -> str:
        """Return a relative URL for serving the file through the API."""
        path = Path(storage_path)
        # Return path relative to the upload dir for API access
        try:
            relative = path.relative_to(self._upload_dir)
            return f"/uploads/{relative}"
        except ValueError:
            return storage_path

    @staticmethod
    def _get_size(file_obj) -> int:
        """Determine file size from file-like object."""
        try:
            pos = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(pos)
            return size
        except Exception:
            return 0
