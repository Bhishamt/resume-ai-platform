"""Abstract email service with provider selection.

Usage:
    from app.services.email.email_service import get_email_service

    service = get_email_service()
    await service.send_welcome(to_email="user@example.com", full_name="Alice")

The provider is selected from EMAIL_PROVIDER env var:
  - smtp       : aiosmtplib SMTP provider
  - sendgrid   : SendGrid HTTP API provider
  - console    : Prints to stdout (development / testing)
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)

# Jinja2 environment for HTML email templates
_TEMPLATE_DIR = Path(__file__).parent / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 email template with the given context."""
    template = _jinja_env.get_template(template_name)
    return template.render(**context, settings=settings)


class BaseEmailProvider(ABC):
    """Abstract base for email providers."""

    @abstractmethod
    async def send(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an email. Returns True on success, False on failure."""
        ...


class EmailService:
    """High-level email service that delegates to a concrete provider."""

    def __init__(self, provider: BaseEmailProvider) -> None:
        self._provider = provider

    async def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Generic send. Returns True if email was dispatched successfully."""
        if not settings.EMAIL_ENABLED:
            logger.debug(
                "Email disabled — skipping send to %s (subject: %s)", to_email, subject
            )
            return True
        try:
            return await self._provider.send(to_email, subject, html_body)
        except Exception as exc:
            logger.error("EmailService.send_email failed to=%s: %s", to_email, exc)
            return False

    # ── Typed send methods ────────────────────────────────────────────────────

    async def send_welcome(self, to_email: str, full_name: str) -> bool:
        html = render_template(
            "welcome.html",
            {
                "full_name": full_name,
                "login_url": f"{settings.FRONTEND_URL}/login",
                "dashboard_url": f"{settings.FRONTEND_URL}/dashboard",
            },
        )
        return await self.send_email(
            to_email, "Welcome to AI Resume Analyzer! 🎉", html
        )

    async def send_verification(
        self, to_email: str, full_name: str, token: str
    ) -> bool:
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        html = render_template(
            "verify_email.html",
            {
                "full_name": full_name,
                "verify_url": verify_url,
            },
        )
        return await self.send_email(to_email, "Verify your email address", html)

    async def send_password_reset(
        self, to_email: str, full_name: str, token: str
    ) -> bool:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        html = render_template(
            "password_reset.html",
            {
                "full_name": full_name,
                "reset_url": reset_url,
                "expire_minutes": settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
            },
        )
        return await self.send_email(to_email, "Reset your password", html)

    async def send_analysis_complete(
        self,
        to_email: str,
        full_name: str,
        resume_title: str,
        ats_score: float,
        resume_id: str,
    ) -> bool:
        report_url = f"{settings.FRONTEND_URL}/dashboard/resumes/{resume_id}"
        html = render_template(
            "analysis_complete.html",
            {
                "full_name": full_name,
                "resume_title": resume_title,
                "ats_score": round(ats_score, 1),
                "report_url": report_url,
            },
        )
        return await self.send_email(
            to_email, f"Your resume analysis is ready — {resume_title}", html
        )

    async def send_job_match_complete(
        self,
        to_email: str,
        full_name: str,
        job_title: str,
        match_score: float,
        match_id: str,
    ) -> bool:
        match_url = f"{settings.FRONTEND_URL}/dashboard/matches/{match_id}"
        html = render_template(
            "job_match_complete.html",
            {
                "full_name": full_name,
                "job_title": job_title,
                "match_score": round(match_score, 1),
                "match_url": match_url,
            },
        )
        return await self.send_email(
            to_email,
            f"Job match results ready — {match_score:.0f}% match with {job_title}",
            html,
        )

    async def send_weekly_summary(
        self, to_email: str, full_name: str, summary_data: dict
    ) -> bool:
        html = render_template(
            "weekly_summary.html",
            {
                "full_name": full_name,
                "dashboard_url": f"{settings.FRONTEND_URL}/dashboard",
                **summary_data,
            },
        )
        return await self.send_email(to_email, "Your weekly career summary 📊", html)


# ── Factory ───────────────────────────────────────────────────────────────────

_email_service_instance: EmailService | None = None


def get_email_service() -> EmailService:
    """Return the singleton EmailService configured by EMAIL_PROVIDER."""
    global _email_service_instance
    if _email_service_instance is not None:
        return _email_service_instance

    provider_name = settings.EMAIL_PROVIDER.lower()

    if provider_name == "sendgrid":
        from app.services.email.sendgrid_provider import SendGridProvider

        provider = SendGridProvider()
    elif provider_name == "console":
        from app.services.email.smtp_provider import ConsoleProvider

        provider = ConsoleProvider()
    else:
        # Default: SMTP
        from app.services.email.smtp_provider import SMTPProvider

        provider = SMTPProvider()

    _email_service_instance = EmailService(provider)
    return _email_service_instance
