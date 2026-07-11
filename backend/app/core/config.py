"""Application settings — single source of truth for all configuration.

All values are read from environment variables or .env file.
Never hardcode secrets. Never commit .env files.
"""

import json
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Project ──────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "AI Resume Analyzer & Job Match Platform"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "placeholder_secret_key_change_in_production"
    JWT_SECRET: str = "placeholder_jwt_secret_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, str):
            return json.loads(v)
        return v

    # ── AI Provider ───────────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""

    # ── File Upload ───────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    MAX_REQUEST_SIZE: int = 20 * 1024 * 1024  # 20 MB (multipart overhead)

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes default cache TTL
    REDIS_DASHBOARD_CACHE_TTL: int = 60  # 1 minute for dashboard data
    REDIS_SESSION_TTL: int = 86400  # 24 hours for session cache

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = False  # Set True in testing

    # ── Email ─────────────────────────────────────────────────────────────────
    EMAIL_PROVIDER: str = "smtp"  # smtp | sendgrid | console
    EMAIL_ENABLED: bool = False  # Toggle email sending

    # SMTP settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@resumeai.com"
    SMTP_FROM_NAME: str = "AI Resume Analyzer"
    SMTP_USE_TLS: bool = True

    # SendGrid settings
    SENDGRID_API_KEY: str = ""

    # ── Cloud Storage ─────────────────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"  # local | s3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_ENDPOINT_URL: str = ""  # For MinIO / LocalStack

    # ── Observability ─────────────────────────────────────────────────────────
    ENABLE_METRICS: bool = True
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
    }


settings = Settings()
