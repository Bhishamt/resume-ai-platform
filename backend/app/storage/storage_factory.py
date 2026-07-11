"""Storage factory — returns the configured storage provider singleton.

Usage:
    from app.storage.storage_factory import get_storage
    storage = get_storage()
    stored_filename, path = storage.save(file.file, file.filename, user_id)

The provider is selected from STORAGE_BACKEND env var:
  - local  : LocalStorage (default — no external dependencies)
  - s3     : S3Storage (requires AWS_* env vars)
"""

import logging

from app.core.config import settings
from app.storage.base_storage import BaseStorage

logger = logging.getLogger(__name__)

_storage_instance: BaseStorage | None = None


def get_storage() -> BaseStorage:
    """Return the singleton storage provider based on STORAGE_BACKEND config."""
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    backend = settings.STORAGE_BACKEND.lower()

    if backend == "s3":
        from app.storage.s3_storage import S3Storage
        _storage_instance = S3Storage()
        logger.info("Storage backend: S3 (bucket=%s)", settings.AWS_BUCKET_NAME)
    else:
        from app.storage.local_storage import LocalStorage
        _storage_instance = LocalStorage()
        logger.info("Storage backend: Local (dir=%s)", settings.UPLOAD_DIR)

    return _storage_instance


def reset_storage() -> None:
    """Reset the storage singleton — used in tests to swap providers."""
    global _storage_instance
    _storage_instance = None
