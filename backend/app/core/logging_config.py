"""Structured logging configuration for production.

Outputs JSON in production for log aggregation (CloudWatch, Datadog, etc.)
and human-readable text in development.
"""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Configure application-wide logging based on environment."""

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.LOG_FORMAT == "json":
        try:
            from pythonjsonlogger import json as jsonlogger

            class CustomJsonFormatter(jsonlogger.JsonFormatter):
                def add_fields(
                    self,
                    log_record: dict,
                    record: logging.LogRecord,
                    message_dict: dict,
                ) -> None:
                    super().add_fields(log_record, record, message_dict)
                    log_record["level"] = record.levelname
                    log_record["service"] = "resume-ai-backend"
                    log_record["env"] = settings.APP_ENV
                    # Preserve request_id if set by middleware
                    if hasattr(record, "request_id"):
                        log_record["request_id"] = record.request_id

            formatter = CustomJsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%SZ",
            )
        except ImportError:
            # Fallback if python-json-logger not installed
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s"
            if False  # request_id is optional in text mode
            else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quieten noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
