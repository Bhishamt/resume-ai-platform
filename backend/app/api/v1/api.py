from fastapi import APIRouter

from app.api.v1.endpoints import (admin, ai, analysis, auth, dashboard, health,
                                  job_matching, resumes, users, ws)

api_router = APIRouter()

# ── Observability ─────────────────────────────────────────────────────────────
api_router.include_router(health.router, prefix="/health", tags=["health"])

# ── Authentication & Users ────────────────────────────────────────────────────
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# ── Core Features ─────────────────────────────────────────────────────────────
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(
    job_matching.router, prefix="/job-matching", tags=["job-matching"]
)
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# ── Administration ────────────────────────────────────────────────────────────
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# ── Real-Time ─────────────────────────────────────────────────────────────────
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
