"""Tests for email service providers and template rendering."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSMTPProvider:
    """Tests for the SMTP email provider."""

    @pytest.mark.asyncio
    async def test_smtp_send_success(self):
        """SMTPProvider.send returns True on successful delivery."""
        from app.services.email.smtp_provider import SMTPProvider

        with patch(
            "app.services.email.smtp_provider.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = None  # aiosmtplib.send returns None on success
            provider = SMTPProvider()
            result = await provider.send(
                to_email="user@example.com",
                subject="Test Subject",
                html_body="<p>Hello</p>",
            )

        assert result is True

    @pytest.mark.asyncio
    async def test_smtp_send_failure_returns_false(self):
        """SMTPProvider.send returns False on SMTP exception."""
        import aiosmtplib

        from app.services.email.smtp_provider import SMTPProvider

        with patch(
            "app.services.email.smtp_provider.aiosmtplib.send",
            side_effect=aiosmtplib.SMTPException("Connection refused"),
        ):
            provider = SMTPProvider()
            result = await provider.send(
                to_email="user@example.com",
                subject="Test",
                html_body="<p>Test</p>",
            )

        assert result is False


class TestConsoleProvider:
    """Tests for the Console email provider (dev/test)."""

    @pytest.mark.asyncio
    async def test_console_provider_always_returns_true(self):
        """ConsoleProvider always returns True (prints to stdout)."""
        from app.services.email.smtp_provider import ConsoleProvider

        provider = ConsoleProvider()
        result = await provider.send(
            to_email="dev@test.com",
            subject="Dev test",
            html_body="<h1>Hello</h1>",
        )
        assert result is True


class TestSendGridProvider:
    """Tests for the SendGrid email provider."""

    @pytest.mark.asyncio
    async def test_sendgrid_send_success(self):
        """SendGridProvider.send returns True on 202 response."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.SENDGRID_API_KEY = "SG.test123"
            mock_settings.SMTP_FROM_EMAIL = "test@example.com"
            mock_settings.SMTP_FROM_NAME = "Test"

            mock_sg_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 202
            mock_sg_client.send.return_value = mock_response

            with patch(
                "sendgrid.SendGridAPIClient", return_value=mock_sg_client
            ), patch("app.services.email.sendgrid_provider.settings", mock_settings):
                from app.services.email.sendgrid_provider import \
                    SendGridProvider

                provider = SendGridProvider()
                provider._sg = mock_sg_client

                result = await provider.send(
                    to_email="user@example.com",
                    subject="Hello",
                    html_body="<p>World</p>",
                )

            assert result is True


class TestEmailService:
    """Tests for the high-level EmailService facade."""

    @pytest.mark.asyncio
    async def test_send_welcome_calls_provider(self):
        """EmailService.send_welcome delegates to the provider."""
        mock_provider = AsyncMock()
        mock_provider.send = AsyncMock(return_value=True)

        with patch("app.core.config.settings") as mock_settings:
            mock_settings.EMAIL_ENABLED = True
            mock_settings.FRONTEND_URL = "http://localhost:5173"

            from app.services.email.email_service import EmailService

            service = EmailService(mock_provider)

            with patch(
                "app.services.email.email_service.settings", mock_settings
            ), patch(
                "app.services.email.email_service.render_template",
                return_value="<html>Welcome</html>",
            ):
                result = await service.send_welcome("user@example.com", "Alice")

        assert result is True
        mock_provider.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_skipped_when_disabled(self):
        """EmailService does not call provider when EMAIL_ENABLED=False."""
        mock_provider = AsyncMock()
        mock_provider.send = AsyncMock(return_value=True)

        with patch("app.services.email.email_service.settings") as mock_settings:
            mock_settings.EMAIL_ENABLED = False

            from app.services.email.email_service import EmailService

            service = EmailService(mock_provider)
            result = await service.send_email("user@example.com", "Test", "<p>body</p>")

        assert result is True
        mock_provider.send.assert_not_called()

    def test_get_email_service_returns_smtp_by_default(self):
        """get_email_service returns an EmailService backed by SMTPProvider."""
        import app.services.email.email_service as module

        # Reset singleton for test isolation
        module._email_service_instance = None

        with patch("app.services.email.email_service.settings") as mock_settings:
            mock_settings.EMAIL_PROVIDER = "smtp"

            with patch("app.services.email.smtp_provider.SMTPProvider"):
                from app.services.email.email_service import (
                    EmailService, get_email_service)

                service = get_email_service()
                assert isinstance(service, EmailService)

        # Reset singleton after test
        module._email_service_instance = None


class TestTemplateRendering:
    """Test Jinja2 email template rendering."""

    def test_welcome_template_renders(self):
        """Welcome template renders without errors."""
        from app.services.email.email_service import render_template

        with patch("app.services.email.email_service.settings") as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:5173"
            mock_settings.PROJECT_NAME = "Test Platform"

            html = render_template(
                "welcome.html",
                {
                    "full_name": "John Doe",
                    "login_url": "http://localhost:5173/login",
                    "dashboard_url": "http://localhost:5173/dashboard",
                },
            )

        assert "John Doe" in html
        assert "Welcome" in html

    def test_password_reset_template_renders(self):
        """Password reset template includes reset URL."""
        from app.services.email.email_service import render_template

        with patch("app.services.email.email_service.settings") as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:5173"
            mock_settings.PROJECT_NAME = "Test Platform"

            html = render_template(
                "password_reset.html",
                {
                    "full_name": "Jane Smith",
                    "reset_url": "http://localhost:5173/reset?token=abc123",
                    "expire_minutes": 30,
                },
            )

        assert "Jane Smith" in html
        assert "abc123" in html
