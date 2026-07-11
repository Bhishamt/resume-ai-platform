"""Tests for Celery tasks — run synchronously via CELERY_TASK_ALWAYS_EAGER=True."""

import os
import pytest
from unittest.mock import MagicMock, patch

# Force eager mode before importing tasks
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")


class TestResumeParsingTask:
    """Tests for app.tasks.resume_tasks.parse_resume_async."""

    def test_parse_resume_not_found(self):
        """Task returns not_found when resume_id doesn't exist in DB."""
        from app.tasks.resume_tasks import parse_resume_async

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("app.database.base.SessionLocal", return_value=mock_db):
            result = parse_resume_async.run(
                resume_id="00000000-0000-0000-0000-000000000001",
                storage_path="/tmp/fake.pdf",
                filename="resume.pdf",
            )

        assert result["status"] == "not_found"

    def test_parse_resume_success(self):
        """Task returns 'parsed' when parsing succeeds."""
        from app.tasks.resume_tasks import parse_resume_async

        mock_resume = MagicMock()
        mock_resume.id = "00000000-0000-0000-0000-000000000001"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_resume

        mock_parser = MagicMock()
        mock_parser.parse.return_value = {"raw_text": "John Doe — Software Engineer"}

        with patch("app.database.base.SessionLocal", return_value=mock_db), \
             patch("app.services.parser.parser_factory.ParserFactory.get_parser", return_value=mock_parser):
            result = parse_resume_async.run(
                resume_id="00000000-0000-0000-0000-000000000001",
                storage_path="/tmp/resume.pdf",
                filename="resume.pdf",
            )

        assert result["status"] == "parsed"
        assert mock_resume.parsed_text == "John Doe — Software Engineer"
        assert mock_resume.upload_status == "parsed"

    def test_parse_resume_parser_failure(self):
        """Task sets upload_status='parse_failed' when parser raises an exception."""
        from app.tasks.resume_tasks import parse_resume_async
        from celery.exceptions import Retry

        mock_resume = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_resume

        with patch("app.database.base.SessionLocal", return_value=mock_db), \
             patch("app.services.parser.parser_factory.ParserFactory.get_parser", side_effect=RuntimeError("corrupt file")), \
             pytest.raises((Retry, RuntimeError)):
            parse_resume_async.run(
                resume_id="00000000-0000-0000-0000-000000000001",
                storage_path="/tmp/bad.pdf",
                filename="bad.pdf",
            )

        assert mock_resume.upload_status == "parse_failed"


class TestAITask:
    """Tests for app.tasks.ai_tasks.run_ai_analysis_async."""

    def test_ai_task_no_resume(self):
        """Returns not_found when resume doesn't exist."""
        from app.tasks.ai_tasks import run_ai_analysis_async

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("app.database.base.SessionLocal", return_value=mock_db):
            result = run_ai_analysis_async.run(
                resume_id="00000000-0000-0000-0000-000000000002",
                user_id="00000000-0000-0000-0000-000000000099",
                request_type="review",
            )

        assert result["status"] == "not_found"

    def test_ai_task_no_parsed_text(self):
        """Returns no_parsed_text when resume has no parsed content."""
        from app.tasks.ai_tasks import run_ai_analysis_async

        mock_resume = MagicMock()
        mock_resume.parsed_text = None

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_resume

        with patch("app.database.base.SessionLocal", return_value=mock_db):
            result = run_ai_analysis_async.run(
                resume_id="00000000-0000-0000-0000-000000000002",
                user_id="00000000-0000-0000-0000-000000000099",
                request_type="review",
            )

        assert result["status"] == "no_parsed_text"


class TestNotificationTask:
    """Tests for notification task dispatcher."""

    def test_welcome_email_task_dispatched(self):
        """Welcome email task calls email service when EMAIL_ENABLED=True."""
        from app.tasks.notification_tasks import send_welcome_email_task

        mock_service = MagicMock()
        mock_service.send_welcome = MagicMock(return_value=None)

        import asyncio

        async def async_true():
            return True

        mock_service.send_welcome = MagicMock(return_value=asyncio.coroutine(lambda: True)())

        with patch("app.services.email.email_service.get_email_service", return_value=mock_service):
            with patch("app.tasks.notification_tasks._run_async", return_value=True):
                result = send_welcome_email_task.run(
                    user_email="test@example.com",
                    full_name="Test User",
                )

        assert result["status"] == "sent"
        assert result["type"] == "welcome"


class TestCleanupTask:
    """Tests for cleanup tasks."""

    def test_cleanup_orphaned_files_no_dir(self, tmp_path):
        """Handles missing upload directory gracefully."""
        from app.tasks.cleanup_tasks import cleanup_orphaned_files

        with patch("app.core.config.settings") as mock_settings, \
             patch("app.database.base.SessionLocal") as mock_session:
            mock_settings.UPLOAD_DIR = str(tmp_path / "nonexistent")
            mock_db = MagicMock()
            mock_db.query.return_value.all.return_value = []
            mock_session.return_value = mock_db

            result = cleanup_orphaned_files.run()

        assert result["status"] == "ok"
        assert result["deleted"] == 0
