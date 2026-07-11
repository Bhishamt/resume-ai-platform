"""FastAPI application entry point — production-ready configuration.

Phase 10: Added structured logging, request ID middleware, Prometheus
metrics, content security policy, HSTS headers, and request size limiting.
"""

from app.core.logging_config import configure_logging

# Configure structured logging before anything else imports logging
configure_logging()

import logging  # noqa: E402 (must come after configure_logging)

from fastapi import FastAPI, Request, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402

from app.api.v1.api import api_router  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.exceptions import register_exception_handlers  # noqa: E402
from app.middleware.rate_limiter import RateLimiterMiddleware  # noqa: E402
from app.middleware.request_id import RequestIDMiddleware  # noqa: E402

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting %s [env=%s storage=%s email=%s]",
        settings.PROJECT_NAME,
        settings.APP_ENV,
        settings.STORAGE_BACKEND,
        settings.EMAIL_PROVIDER,
    )

    if settings.APP_ENV == "production":
        dangerous_defaults = [
            "placeholder_secret_key_change_in_production",
            "placeholder_jwt_secret_change_in_production",
        ]
        if (
            settings.SECRET_KEY in dangerous_defaults
            or settings.JWT_SECRET in dangerous_defaults
        ):
            raise RuntimeError(
                "FATAL: Placeholder secrets detected in production. "
                "Set SECRET_KEY and JWT_SECRET in environment."
            )

    try:
        from app.core.redis_client import ping_redis
        redis_ok = await ping_redis()
        if redis_ok:
            logger.info("Redis connected successfully")
        else:
            logger.warning("Redis not reachable — caching and rate limiting degraded")
    except Exception as exc:
        logger.warning("Redis connection check failed: %s", exc)
        
    yield
    
    logger.info("Shutting down %s", settings.PROJECT_NAME)
    try:
        from app.core.redis_client import _redis_client
        if _redis_client:
            await _redis_client.aclose()
            logger.info("Redis connection closed")
    except Exception as exc:
        logger.warning("Redis shutdown error: %s", exc)

# ── FastAPI Application ───────────────────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered resume analysis and job matching platform API.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# ── Exception Handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Prometheus Metrics ────────────────────────────────────────────────────────
if settings.ENABLE_METRICS:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=False,
            excluded_handlers=["/api/v1/metrics", "/api/v1/health"],
        ).instrument(app).expose(app, endpoint=f"{settings.API_V1_STR}/metrics")
        logger.info("Prometheus metrics enabled at %s/metrics", settings.API_V1_STR)
    except ImportError:
        logger.warning(
            "prometheus-fastapi-instrumentator not installed — metrics disabled"
        )

# ── Middleware (added in reverse order — last added = outermost) ───────────────

# Request ID — must be outermost for full request tracing
app.add_middleware(RequestIDMiddleware)

# Rate limiter
app.add_middleware(
    RateLimiterMiddleware,
    general_rate=60,
    general_window=60,
    auth_rate=10,
    auth_window=60,
)

# CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ── Security Headers ──────────────────────────────────────────────────────────


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Apply comprehensive security headers to every response."""
    response = await call_next(request)

    # Prevent MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Block clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # Legacy XSS filter
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Permissions policy — disable unused browser features
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        "font-src 'self' fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "connect-src 'self' wss:; "
        "frame-ancestors 'none';"
    )
    # HSTS — enforce HTTPS (production only, 1 year)
    if settings.APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    return response


# ── Request Size Limit ────────────────────────────────────────────────────────


@app.middleware("http")
async def enforce_request_size(request: Request, call_next) -> Response:
    """Reject requests with body exceeding MAX_REQUEST_SIZE."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=413,
            content={
                "success": False,
                "message": f"Request body too large. Maximum is {settings.MAX_REQUEST_SIZE // (1024 * 1024)} MB.",
                "errors": [],
            },
        )
    return await call_next(request)




# ── Router ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)
