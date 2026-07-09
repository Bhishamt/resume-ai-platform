"""In-memory rate limiter middleware using a token bucket algorithm per IP.

Provides protection against brute-force attacks on auth endpoints.
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


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiter using a sliding window counter per client IP."""

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
        self._general_requests: dict[str, list[float]] = defaultdict(list)
        self._auth_requests: dict[str, list[float]] = defaultdict(list)

    def _is_auth_endpoint(self, path: str) -> bool:
        """Check if the request path is an authentication endpoint."""
        auth_paths = ["/auth/login", "/auth/register", "/auth/forgot-password"]
        return any(path.endswith(p) for p in auth_paths)

    def _clean_old_requests(self, timestamps: list[float], window: int) -> list[float]:
        """Remove timestamps outside the sliding window."""
        now = time.time()
        return [ts for ts in timestamps if now - ts < window]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if settings.APP_ENV == "testing":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        now = time.time()

        # Check auth-specific rate limit
        if self._is_auth_endpoint(path):
            self._auth_requests[client_ip] = self._clean_old_requests(
                self._auth_requests[client_ip], self.auth_window
            )
            if len(self._auth_requests[client_ip]) >= self.auth_rate:
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": "Too many requests. Please try again later.",
                        "errors": [],
                    },
                )
            self._auth_requests[client_ip].append(now)

        # Check general rate limit
        self._general_requests[client_ip] = self._clean_old_requests(
            self._general_requests[client_ip], self.general_window
        )
        if len(self._general_requests[client_ip]) >= self.general_rate:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Too many requests. Please try again later.",
                    "errors": [],
                },
            )
        self._general_requests[client_ip].append(now)

        response = await call_next(request)
        return response
