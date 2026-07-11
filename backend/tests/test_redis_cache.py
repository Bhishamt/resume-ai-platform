"""Tests for Redis cache helpers and JWT blacklist."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCacheHelpers:
    """Test generic cache get/set/delete operations."""

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """cache_set stores a value; cache_get retrieves it."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(return_value=True)
        mock_client.get = AsyncMock(return_value='{"key": "value"}')

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import cache_get, cache_set

            result = await cache_set("test:key", {"key": "value"}, ttl=60)
            assert result is True

            value = await cache_get("test:key")
            assert value == {"key": "value"}

    @pytest.mark.asyncio
    async def test_cache_get_miss(self):
        """cache_get returns None on cache miss."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=None)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import cache_get

            result = await cache_get("nonexistent:key")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_delete(self):
        """cache_delete calls Redis delete command."""
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=1)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import cache_delete

            result = await cache_delete("test:key")
            assert result is True
            mock_client.delete.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_cache_set_redis_error_returns_false(self):
        """cache_set returns False when Redis raises an exception."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(side_effect=Exception("Redis connection refused"))

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import cache_set

            result = await cache_set("test:key", "value")
            assert result is False

    @pytest.mark.asyncio
    async def test_cache_invalidate_prefix(self):
        """cache_invalidate_prefix deletes all keys matching a prefix."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(return_value=["cache:user:1", "cache:user:2"])
        mock_client.delete = AsyncMock(return_value=2)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import cache_invalidate_prefix

            count = await cache_invalidate_prefix("cache:user:")
            assert count == 2


class TestJWTBlacklist:
    """Test JWT token blacklist operations."""

    @pytest.mark.asyncio
    async def test_blacklist_token(self):
        """blacklist_token stores jti in Redis with correct TTL."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(return_value=True)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import blacklist_token

            result = await blacklist_token("test-jti-123", expires_in_seconds=1800)
            assert result is True
            mock_client.set.assert_called_once_with(
                "jwt:blacklist:test-jti-123", "1", ex=1800
            )

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_true(self):
        """is_token_blacklisted returns True for blacklisted jti."""
        mock_client = AsyncMock()
        mock_client.exists = AsyncMock(return_value=1)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import is_token_blacklisted

            result = await is_token_blacklisted("blacklisted-jti")
            assert result is True

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_false(self):
        """is_token_blacklisted returns False for valid jti."""
        mock_client = AsyncMock()
        mock_client.exists = AsyncMock(return_value=0)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import is_token_blacklisted

            result = await is_token_blacklisted("valid-jti")
            assert result is False

    @pytest.mark.asyncio
    async def test_blacklist_redis_failure_returns_false(self):
        """blacklist_token returns False on Redis failure (fail-open)."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(side_effect=Exception("connection error"))

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import blacklist_token

            result = await blacklist_token("some-jti", 1800)
            assert result is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_redis_failure_returns_false(self):
        """is_token_blacklisted returns False on Redis failure (fail-open — don't block)."""
        mock_client = AsyncMock()
        mock_client.exists = AsyncMock(side_effect=Exception("timeout"))

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import is_token_blacklisted

            result = await is_token_blacklisted("any-jti")
            assert result is False


class TestRateLimitCheck:
    """Test Redis-backed rate limit helper."""

    @pytest.mark.asyncio
    async def test_rate_limit_allows_under_limit(self):
        """Returns allowed=True when count is under limit."""
        mock_client = AsyncMock()
        mock_pipe = AsyncMock()
        mock_pipe.incr = MagicMock()
        mock_pipe.expire = MagicMock()
        mock_pipe.execute = AsyncMock(return_value=[5, True])  # count=5
        mock_client.pipeline = MagicMock(return_value=mock_pipe)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import rate_limit_check

            allowed, count = await rate_limit_check("rl:127.0.0.1", limit=10, window=60)
            assert allowed is True
            assert count == 5

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_over_limit(self):
        """Returns allowed=False when count exceeds limit."""
        mock_client = AsyncMock()
        mock_pipe = AsyncMock()
        mock_pipe.incr = MagicMock()
        mock_pipe.expire = MagicMock()
        mock_pipe.execute = AsyncMock(return_value=[11, True])  # count=11 > limit=10
        mock_client.pipeline = MagicMock(return_value=mock_pipe)

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import rate_limit_check

            allowed, count = await rate_limit_check("rl:127.0.0.1", limit=10, window=60)
            assert allowed is False
            assert count == 11

    @pytest.mark.asyncio
    async def test_rate_limit_fails_open(self):
        """Returns allowed=True on Redis failure (fail-open for resilience)."""
        mock_client = AsyncMock()
        mock_client.pipeline = MagicMock(side_effect=Exception("Redis down"))

        with patch("app.core.redis_client.get_redis", return_value=mock_client):
            from app.core.redis_client import rate_limit_check

            allowed, count = await rate_limit_check("rl:127.0.0.1", limit=10, window=60)
            assert allowed is True
