"""AWS S3 storage provider.

Files are stored under {bucket}/{user_id}/{uuid}{ext}.
Supports pre-signed URL generation for secure file access.
Also compatible with MinIO and LocalStack via AWS_S3_ENDPOINT_URL.
"""

import logging
import os
import uuid
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.storage.base_storage import BaseStorage

logger = logging.getLogger(__name__)


class S3Storage(BaseStorage):
    """Store files on AWS S3 (or S3-compatible storage like MinIO)."""

    def __init__(self) -> None:
        try:
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError

            self._BotoCoreError = BotoCoreError
            self._ClientError = ClientError

            kwargs = {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID or None,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY or None,
                "region_name": settings.AWS_REGION,
            }
            if settings.AWS_S3_ENDPOINT_URL:
                kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL

            self._s3 = boto3.client("s3", **kwargs)
            self._bucket = settings.AWS_BUCKET_NAME

            if not self._bucket:
                raise ValueError("AWS_BUCKET_NAME must be configured for S3 storage.")

        except ImportError as exc:
            raise RuntimeError(
                "boto3 is required for S3 storage. Install it with: pip install boto3"
            ) from exc

    def save(self, file_obj, filename: str, user_id: UUID) -> tuple[str, str]:
        """Upload a file to S3.

        Returns:
            (stored_filename, s3_key) where s3_key is the full S3 object key.
        """
        content_type = getattr(file_obj, "content_type", None)
        size = self._get_size(file_obj)
        self.validate_file(filename, content_type, size)

        ext = os.path.splitext(filename)[1].lower()
        stored_filename = f"{uuid.uuid4()}{ext}"
        s3_key = f"{user_id}/{stored_filename}"

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            self._s3.upload_fileobj(
                file_obj,
                self._bucket,
                s3_key,
                ExtraArgs=extra_args,
            )
            logger.info("S3Storage.save: %s → s3://%s/%s", filename, self._bucket, s3_key)
            return stored_filename, s3_key

        except (self._BotoCoreError, self._ClientError) as exc:
            logger.error("S3 upload failed for key=%s: %s", s3_key, exc)
            raise BadRequestError(f"Failed to upload file to S3: {exc}") from exc

    def delete(self, storage_path: str) -> None:
        """Delete a file (S3 key) from the bucket. Silently ignores missing keys."""
        try:
            self._s3.delete_object(Bucket=self._bucket, Key=storage_path)
            logger.info("S3Storage.delete: %s", storage_path)
        except (self._BotoCoreError, self._ClientError) as exc:
            logger.warning("S3Storage.delete failed for %s: %s", storage_path, exc)

    def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Generate a pre-signed URL valid for `expires_in` seconds (default 1 hour)."""
        try:
            url = self._s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": storage_path},
                ExpiresIn=expires_in,
            )
            return url
        except (self._BotoCoreError, self._ClientError) as exc:
            logger.error("S3 presigned URL failed for %s: %s", storage_path, exc)
            return ""

    @staticmethod
    def _get_size(file_obj) -> int:
        """Determine file size from file-like object."""
        try:
            pos = file_obj.tell()
            import os as _os
            file_obj.seek(0, _os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(pos)
            return size
        except Exception:
            return 0
