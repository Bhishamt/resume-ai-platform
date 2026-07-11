"""Health check endpoints for liveness and readiness probes.

GET /health          — basic liveness (always 200 if process is running)
GET /health/detailed — readiness (checks DB, Redis, Celery connectivity)
"""

import logging
import time
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

_start_time = time.time()


@router.get(
    "/",
    summary="Basic liveness probe",
    tags=["observability"],
)
async def health_check() -> dict:
    """Minimal liveness check — returns 200 if the process is alive."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@router.get(
    "/detailed",
    summary="Detailed readiness probe",
    tags=["observability"],
)
async def health_detailed() -> JSONResponse:
    """Comprehensive health check — verifies DB, Redis, and Celery connectivity.

    Returns HTTP 200 if all checks pass, 503 if any dependency is unavailable.
    """
    checks: dict[str, Any] = {}
    overall_healthy = True

    # ── Database ──────────────────────────────────────────────────────────────
    try:
        import sqlalchemy

        from app.database.base import SessionLocal

        db = SessionLocal()
        db.execute(sqlalchemy.text("SELECT 1"))
        db.close()
        checks["database"] = {"status": "healthy", "backend": "postgresql"}
    except Exception as exc:
        checks["database"] = {"status": "unhealthy", "error": str(exc)}
        overall_healthy = False
        logger.warning("Health check — DB unreachable: %s", exc)

    # ── Redis ─────────────────────────────────────────────────────────────────
    try:
        from app.core.redis_client import ping_redis

        redis_ok = await ping_redis()
        if redis_ok:
            checks["redis"] = {"status": "healthy"}
        else:
            checks["redis"] = {"status": "unhealthy", "error": "ping failed"}
            overall_healthy = False
    except Exception as exc:
        checks["redis"] = {"status": "unhealthy", "error": str(exc)}
        overall_healthy = False
        logger.warning("Health check — Redis unreachable: %s", exc)

    # ── Celery ────────────────────────────────────────────────────────────────
    try:
        from app.core.celery_app import celery_app

        inspect = celery_app.control.inspect(timeout=2.0)
        stats = inspect.stats()
        worker_count = len(stats) if stats else 0
        checks["celery"] = {
            "status": "healthy" if worker_count > 0 else "degraded",
            "workers": worker_count,
        }
        if worker_count == 0:
            checks["celery"]["note"] = "No workers online — tasks will queue"
    except Exception as exc:
        checks["celery"] = {"status": "degraded", "error": str(exc)}
        logger.warning("Health check — Celery inspect failed: %s", exc)

    # ── Storage ───────────────────────────────────────────────────────────────
    try:
        from pathlib import Path

        backend = settings.STORAGE_BACKEND
        if backend == "local":
            upload_dir = Path(settings.UPLOAD_DIR)
            upload_dir.mkdir(parents=True, exist_ok=True)
            checks["storage"] = {"status": "healthy", "backend": "local"}
        else:
            checks["storage"] = {"status": "healthy", "backend": backend}
    except Exception as exc:
        checks["storage"] = {"status": "unhealthy", "error": str(exc)}
        overall_healthy = False

    uptime_seconds = round(time.time() - _start_time, 2)

    payload = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "uptime_seconds": uptime_seconds,
        "checks": checks,
    }

    status_code = 200 if overall_healthy else 503
    return JSONResponse(content=payload, status_code=status_code)
