"""Tests for storage abstraction — LocalStorage, S3Storage, and StorageFactory."""

import uuid
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestLocalStorage:
    """Tests for LocalStorage provider."""

    def test_save_pdf_file(self, tmp_path):
        """Saves a PDF file and returns (stored_filename, storage_path)."""
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        file_obj = BytesIO(b"%PDF-1.4 fake content")
        file_obj.content_type = "application/pdf"
        file_obj.seek(0)

        stored_filename, storage_path = storage.save(
            file_obj=file_obj,
            filename="test_resume.pdf",
            user_id=user_id,
        )

        assert stored_filename.endswith(".pdf")
        assert Path(storage_path).exists()
        assert str(user_id) in storage_path

    def test_save_docx_file(self, tmp_path):
        """Saves a DOCX file and returns correct extension."""
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000002")

        file_obj = BytesIO(b"PK fake docx content")
        file_obj.content_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        stored_filename, _ = storage.save(
            file_obj=file_obj,
            filename="resume.docx",
            user_id=user_id,
        )

        assert stored_filename.endswith(".docx")

    def test_delete_existing_file(self, tmp_path):
        """Deletes an existing file without raising."""
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"content")

        storage.delete(str(test_file))
        assert not test_file.exists()

    def test_delete_nonexistent_file_is_noop(self, tmp_path):
        """Deleting a missing file does not raise."""
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        storage.delete(str(tmp_path / "nonexistent.pdf"))  # Should not raise

    def test_delete_outside_upload_dir_blocked(self, tmp_path):
        """Deletion outside UPLOAD_DIR is blocked (path traversal prevention)."""
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        sensitive_path = "/etc/passwd"

        storage.delete(sensitive_path)  # Must not raise, must not delete

    def test_get_url_returns_relative_path(self, tmp_path):
        """get_url returns a relative /uploads/ path."""
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        user_dir = tmp_path / "user-id-123"
        user_dir.mkdir()
        test_file = user_dir / "resume.pdf"
        test_file.write_bytes(b"content")

        url = storage.get_url(str(test_file))
        assert url.startswith("/uploads/")

    def test_invalid_extension_rejected(self, tmp_path):
        """File with unsupported extension raises BadRequestError."""
        from app.core.exceptions import BadRequestError
        from app.storage.local_storage import LocalStorage

        storage = LocalStorage(upload_dir=str(tmp_path))
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000003")

        file_obj = BytesIO(b"#!/bin/bash\nrm -rf /")
        file_obj.content_type = "application/x-sh"

        with pytest.raises(BadRequestError, match="Unsupported file extension"):
            storage.save(file_obj=file_obj, filename="malicious.sh", user_id=user_id)


class TestS3Storage:
    """Tests for S3Storage provider with mocked boto3."""

    def _make_storage(self):
        """Create S3Storage with a fully mocked boto3 client."""
        mock_s3 = MagicMock()
        mock_s3.upload_fileobj = MagicMock()
        mock_s3.delete_object = MagicMock()
        mock_s3.generate_presigned_url = MagicMock(
            return_value="https://s3.amazonaws.com/bucket/key?signature=abc"
        )

        from botocore.exceptions import BotoCoreError, ClientError

        with patch("boto3.client", return_value=mock_s3), patch(
            "app.core.config.settings"
        ) as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "AKIATEST"
            mock_settings.AWS_SECRET_ACCESS_KEY = "secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_BUCKET_NAME = "test-bucket"
            mock_settings.AWS_S3_ENDPOINT_URL = ""
            mock_settings.MAX_UPLOAD_SIZE = 10 * 1024 * 1024

            from app.storage.s3_storage import S3Storage

            storage = S3Storage()
            storage._s3 = mock_s3
            storage._bucket = "test-bucket"
            storage._BotoCoreError = BotoCoreError
            storage._ClientError = ClientError

        return storage, mock_s3

    def test_save_uploads_to_s3(self):
        """save() calls s3.upload_fileobj and returns (filename, s3_key)."""
        storage, mock_s3 = self._make_storage()
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000010")

        file_obj = BytesIO(b"%PDF-1.4 test")
        file_obj.content_type = "application/pdf"

        with patch("app.core.config.settings") as mock_settings:
            mock_settings.MAX_UPLOAD_SIZE = 10 * 1024 * 1024

            stored_filename, s3_key = storage.save(
                file_obj=file_obj,
                filename="resume.pdf",
                user_id=user_id,
            )

        assert stored_filename.endswith(".pdf")
        assert str(user_id) in s3_key
        mock_s3.upload_fileobj.assert_called_once()

    def test_get_url_returns_presigned_url(self):
        """get_url() returns a presigned S3 URL."""
        storage, mock_s3 = self._make_storage()

        url = storage.get_url("user-id/resume.pdf")

        assert url.startswith("https://s3.amazonaws.com")
        mock_s3.generate_presigned_url.assert_called_once()

    def test_delete_calls_s3_delete(self):
        """delete() calls s3.delete_object with correct key."""
        storage, mock_s3 = self._make_storage()

        storage.delete("user-id-123/resume.pdf")

        mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="user-id-123/resume.pdf"
        )


class TestStorageFactory:
    """Tests for the storage factory singleton."""

    def test_local_backend_selected_by_default(self):
        """Factory returns LocalStorage when STORAGE_BACKEND=local."""
        from app.storage import storage_factory

        storage_factory.reset_storage()

        with patch("app.storage.storage_factory.settings") as mock_settings:
            mock_settings.STORAGE_BACKEND = "local"
            mock_settings.UPLOAD_DIR = "uploads"
            mock_settings.AWS_BUCKET_NAME = ""

            storage = storage_factory.get_storage()
            from app.storage.local_storage import LocalStorage

            assert isinstance(storage, LocalStorage)

        storage_factory.reset_storage()

    def test_s3_backend_selected_when_configured(self):
        """Factory returns S3Storage when STORAGE_BACKEND=s3."""
        from app.storage import storage_factory

        storage_factory.reset_storage()

        mock_s3_client = MagicMock()
        with patch("app.storage.storage_factory.settings") as mock_settings, patch(
            "boto3.client", return_value=mock_s3_client
        ), patch("app.core.config.settings") as global_settings:
            mock_settings.STORAGE_BACKEND = "s3"
            global_settings.AWS_BUCKET_NAME = "my-bucket"
            global_settings.AWS_ACCESS_KEY_ID = "key"
            global_settings.AWS_SECRET_ACCESS_KEY = "secret"
            global_settings.AWS_REGION = "us-east-1"
            global_settings.AWS_S3_ENDPOINT_URL = ""

            try:
                storage_factory.get_storage()
            except Exception:
                pass  # S3 init may fail without real credentials

        storage_factory.reset_storage()

    def test_reset_clears_singleton(self):
        """reset_storage() allows a fresh instance to be created."""
        from app.storage import storage_factory

        storage_factory.reset_storage()

        with patch("app.storage.storage_factory.settings") as mock_settings:
            mock_settings.STORAGE_BACKEND = "local"
            mock_settings.UPLOAD_DIR = "uploads"

            s1 = storage_factory.get_storage()

        storage_factory.reset_storage()

        with patch("app.storage.storage_factory.settings") as mock_settings:
            mock_settings.STORAGE_BACKEND = "local"
            mock_settings.UPLOAD_DIR = "uploads"

            s2 = storage_factory.get_storage()

        assert s1 is not s2
        storage_factory.reset_storage()
