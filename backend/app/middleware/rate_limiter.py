"""Rate limiter middleware — Redis-backed sliding window with in-memory fallback.

Uses Redis for distributed rate limiting across multiple workers.
Falls back to in-memory counters if Redis is unavailable (resilient design).

Limits:
  - General API:  60 requests / 60 seconds per IP
  - Auth routes:  10 requests / 60 seconds per IP
"""

import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

_AUTH_PATHS = frozenset(["/auth/login", "/auth/register", "/auth/forgot-password"])

# In-memory fallback stores
_fallback_general: dict[str, list[float]] = defaultdict(list)
_fallback_auth: dict[str, list[float]] = defaultdict(list)


def _clean(timestamps: list[float], window: int) -> list[float]:
    now = time.time()
    return [ts for ts in timestamps if now - ts < window]


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Distributed rate limiter using Redis; falls back to in-memory counters."""

    def __init__(
        self,
        app,
        general_rate: int = 60,
        general_window: int = 60,
        auth_rate: int = 10,
        auth_window: int = 60,
    ):
        super().__init__(app)
        self.general_rate = general_rate
        self.general_window = general_window
        self.auth_rate = auth_rate
        self.auth_window = auth_window

    def _is_auth_endpoint(self, path: str) -> bool:
        return any(path.endswith(p) for p in _AUTH_PATHS)

    async def _check_redis(self, key: str, limit: int, window: int) -> bool:
        """Check rate limit via Redis. Returns True if request is allowed."""
        from app.core.redis_client import rate_limit_check

        allowed, _ = await rate_limit_check(f"rl:{key}", limit, window)
        return allowed

    def _check_memory(self, store: dict, key: str, limit: int, window: int) -> bool:
        """Fallback in-memory rate check."""
        store[key] = _clean(store[key], window)
        if len(store[key]) >= limit:
            return False
        store[key].append(time.time())
        return True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting during tests
        if settings.APP_ENV == "testing":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        is_auth = self._is_auth_endpoint(path)

        # Try Redis first, fall back to memory
        redis_available = True
        try:
            if is_auth:
                auth_key = f"auth:{client_ip}"
                allowed = await self._check_redis(
                    auth_key, self.auth_rate, self.auth_window
                )
                if not allowed:
                    return _rate_limit_response()

            gen_key = f"gen:{client_ip}"
            allowed = await self._check_redis(
                gen_key, self.general_rate, self.general_window
            )
            if not allowed:
                return _rate_limit_response()

        except Exception:
            redis_available = False

        if not redis_available:
            # Fallback to in-memory
            if is_auth:
                if not self._check_memory(
                    _fallback_auth, client_ip, self.auth_rate, self.auth_window
                ):
                    return _rate_limit_response()
            if not self._check_memory(
                _fallback_general, client_ip, self.general_rate, self.general_window
            ):
                return _rate_limit_response()

        return await call_next(request)


def _rate_limit_response() -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Too many requests. Please try again later.",
            "errors": [],
        },
    )
