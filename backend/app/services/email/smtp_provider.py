"""SMTP email provider using aiosmtplib for async delivery.

Supports STARTTLS (port 587) and SSL/TLS (port 465).
A console provider is also provided for development / testing.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings
from app.services.email.email_service import BaseEmailProvider

logger = logging.getLogger(__name__)


class SMTPProvider(BaseEmailProvider):
    """Async SMTP email provider."""

    async def send(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an email via SMTP with TLS support."""
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Plain text fallback (strip HTML tags naively)
        plain_text = html_body.replace("<br>", "\n").replace("<p>", "\n")
        message.attach(MIMEText(plain_text, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER or None,
                password=settings.SMTP_PASSWORD or None,
                use_tls=False,          # STARTTLS is negotiated below
                start_tls=settings.SMTP_USE_TLS,
                timeout=30,
            )
            logger.info("SMTP email sent: to=%s subject=%s", to_email, subject)
            return True
        except aiosmtplib.SMTPException as exc:
            logger.error("SMTP send failed: to=%s subject=%s error=%s", to_email, subject, exc)
            return False
        except Exception as exc:
            logger.error("Unexpected SMTP error: to=%s error=%s", to_email, exc)
            return False


class ConsoleProvider(BaseEmailProvider):
    """Development email provider — prints to stdout instead of sending.

    Use EMAIL_PROVIDER=console in development to see email content without
    needing a real SMTP server.
    """

    async def send(self, to_email: str, subject: str, html_body: str) -> bool:
        """Print email details to stdout for development inspection."""
        separator = "─" * 70
        print(f"\n{separator}")
        print(f"📧 [CONSOLE EMAIL PROVIDER]")
        print(f"  To:      {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body:    (HTML — {len(html_body)} chars)")
        print(separator)
        logger.debug("Console email: to=%s subject=%s", to_email, subject)
        return True
