"""SendGrid email provider via REST API.

Uses the sendgrid SDK for reliable transactional email delivery with
built-in retry, bounce tracking, and analytics.
"""

import logging

from app.core.config import settings
from app.services.email.email_service import BaseEmailProvider

logger = logging.getLogger(__name__)


class SendGridProvider(BaseEmailProvider):
    """SendGrid HTTP API email provider."""

    def __init__(self) -> None:
        if not settings.SENDGRID_API_KEY:
            raise ValueError(
                "SENDGRID_API_KEY must be set when EMAIL_PROVIDER=sendgrid"
            )
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail

            self._sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            self._Mail = Mail
        except ImportError as exc:
            raise RuntimeError(
                "sendgrid package is required for SendGridProvider. "
                "Install it with: pip install sendgrid"
            ) from exc

    async def send(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an email via the SendGrid API.

        Note: sendgrid SDK is synchronous; we run it in a thread executor
        to avoid blocking the event loop.
        """
        import asyncio

        def _blocking_send():
            message = self._Mail(
                from_email=(settings.SMTP_FROM_EMAIL, settings.SMTP_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_body,
            )
            response = self._sg.send(message)
            return response.status_code

        try:
            loop = asyncio.get_event_loop()
            status_code = await loop.run_in_executor(None, _blocking_send)

            if status_code in (200, 202):
                logger.info(
                    "SendGrid email sent: to=%s subject=%s status=%d",
                    to_email,
                    subject,
                    status_code,
                )
                return True
            else:
                logger.error(
                    "SendGrid returned non-success status: to=%s status=%d",
                    to_email,
                    status_code,
                )
                return False

        except Exception as exc:
            logger.error("SendGrid send failed: to=%s error=%s", to_email, exc)
            return False
