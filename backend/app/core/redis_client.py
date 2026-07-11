"""Redis client — singleton connection pool with cache & JWT blacklist helpers.

Usage:
    from app.core.redis_client import get_redis, cache_get, cache_set

The client is lazy-initialized so the app starts cleanly even when Redis
is not yet available (useful for tests that mock Redis).
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    """Return the shared Redis client, creating it on first call."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
    return _redis_client


async def ping_redis() -> bool:
    """Return True if Redis is reachable, False otherwise."""
    try:
        client = get_redis()
        await client.ping()
        return True
    except Exception as exc:
        logger.warning("Redis ping failed: %s", exc)
        return False


# ─── Generic Cache Helpers ────────────────────────────────────────────────────

async def cache_get(key: str) -> Optional[Any]:
    """Retrieve a cached value (JSON-decoded). Returns None on miss or error."""
    try:
        client = get_redis()
        raw = await client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("cache_get failed for key=%s: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> bool:
    """Store a JSON-serialisable value in Redis with the given TTL (seconds)."""
    try:
        client = get_redis()
        await client.set(key, json.dumps(value), ex=ttl)
        return True
    except Exception as exc:
        logger.warning("cache_set failed for key=%s: %s", key, exc)
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from the cache."""
    try:
        client = get_redis()
        await client.delete(key)
        return True
    except Exception as exc:
        logger.warning("cache_delete failed for key=%s: %s", key, exc)
        return False


async def cache_invalidate_prefix(prefix: str) -> int:
    """Delete all keys matching a prefix pattern. Returns count deleted."""
    try:
        client = get_redis()
        pattern = f"{prefix}*"
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
        return 0
    except Exception as exc:
        logger.warning("cache_invalidate_prefix failed for prefix=%s: %s", prefix, exc)
        return 0


# ─── JWT Blacklist ────────────────────────────────────────────────────────────

_JWT_BLACKLIST_PREFIX = "jwt:blacklist:"


async def blacklist_token(jti: str, expires_in_seconds: int) -> bool:
    """Add a JWT token ID to the blacklist until it naturally expires."""
    try:
        client = get_redis()
        key = f"{_JWT_BLACKLIST_PREFIX}{jti}"
        await client.set(key, "1", ex=expires_in_seconds)
        logger.info("JWT token blacklisted: jti=%s", jti)
        return True
    except Exception as exc:
        logger.warning("Failed to blacklist token jti=%s: %s", jti, exc)
        return False


async def is_token_blacklisted(jti: str) -> bool:
    """Return True if this JWT token ID has been blacklisted (logged out)."""
    try:
        client = get_redis()
        key = f"{_JWT_BLACKLIST_PREFIX}{jti}"
        result = await client.exists(key)
        return bool(result)
    except Exception as exc:
        logger.warning("Failed to check blacklist for jti=%s: %s", jti, exc)
        # Fail open — if Redis is down, don't block all requests
        return False


# ─── Redis Rate Limit Helpers ─────────────────────────────────────────────────

async def rate_limit_check(key: str, limit: int, window: int) -> tuple[bool, int]:
    """Sliding window rate limiter using Redis.

    Returns:
        (allowed, current_count) — allowed=False means rate limit exceeded.
    """
    try:
        client = get_redis()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        count = results[0]
        return count <= limit, count
    except Exception as exc:
        logger.warning("rate_limit_check failed for key=%s: %s", key, exc)
        # Fail open — allow request if Redis is unavailable
        return True, 0
