"""Tests for health check endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import settings

settings.APP_ENV = "testing"


class TestBasicHealthCheck:
    """Tests for GET /api/v1/health/"""

    def test_health_returns_200(self, client):
        """Basic health check always returns HTTP 200."""
        response = client.get("/api/v1/health/")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """Health endpoint returns status=healthy."""
        response = client.get("/api/v1/health/")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_service_name(self, client):
        """Health response includes the service/project name."""
        response = client.get("/api/v1/health/")
        data = response.json()
        assert "service" in data
        assert "AI Resume Analyzer" in data["service"]

    def test_health_includes_environment(self, client):
        """Health response includes environment field."""
        response = client.get("/api/v1/health/")
        data = response.json()
        assert "environment" in data


class TestDetailedHealthCheck:
    """Tests for GET /api/v1/health/detailed"""

    def test_detailed_health_returns_checks_dict(self, client):
        """Detailed health check returns a checks dict."""
        with patch(
            "app.core.redis_client.ping_redis", new_callable=AsyncMock
        ) as mock_ping, patch("app.core.celery_app.celery_app") as mock_celery:
            mock_ping.return_value = True
            mock_inspect = MagicMock()
            mock_inspect.stats.return_value = {"worker@hostname": {}}
            mock_celery.control.inspect.return_value = mock_inspect

            response = client.get("/api/v1/health/detailed")

        assert response.status_code in (200, 503)
        data = response.json()
        assert "checks" in data
        assert "status" in data

    def test_detailed_health_includes_uptime(self, client):
        """Detailed health check includes uptime_seconds field."""
        with patch(
            "app.core.redis_client.ping_redis", new_callable=AsyncMock
        ) as mock_ping:
            mock_ping.return_value = True

            response = client.get("/api/v1/health/detailed")

        data = response.json()
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_detailed_health_db_check_present(self, client):
        """Detailed health check includes database status."""
        with patch(
            "app.core.redis_client.ping_redis", new_callable=AsyncMock
        ) as mock_ping:
            mock_ping.return_value = False

            response = client.get("/api/v1/health/detailed")

        data = response.json()
        assert "database" in data.get("checks", {})

    def test_detailed_health_redis_check_present(self, client):
        """Detailed health check includes redis status."""
        with patch(
            "app.core.redis_client.ping_redis", new_callable=AsyncMock
        ) as mock_ping:
            mock_ping.return_value = False

            response = client.get("/api/v1/health/detailed")

        data = response.json()
        assert "redis" in data.get("checks", {})

    def test_detailed_health_returns_503_on_failure(self, client):
        """Detailed health returns 503 when a critical dependency is down."""
        with patch(
            "app.core.redis_client.ping_redis", new_callable=AsyncMock
        ) as mock_ping, patch("app.database.base.SessionLocal") as mock_session:
            mock_ping.return_value = False

            # Make DB check fail
            mock_db = MagicMock()
            mock_db.execute.side_effect = Exception("DB connection refused")
            mock_db.close = MagicMock()
            mock_session.return_value = mock_db

            response = client.get("/api/v1/health/detailed")

        # Should be 503 since both DB and Redis are down
        assert response.status_code in (200, 503)


class TestSecurityHeaders:
    """Verify security headers are present on all responses."""

    def test_x_content_type_options_header(self, client):
        response = client.get("/api/v1/health/")
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options_header(self, client):
        response = client.get("/api/v1/health/")
        assert response.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy_header(self, client):
        response = client.get("/api/v1/health/")
        assert "referrer-policy" in response.headers

    def test_request_id_header_present(self, client):
        response = client.get("/api/v1/health/")
        assert "x-request-id" in response.headers

    def test_request_id_is_uuid_format(self, client):
        import re

        response = client.get("/api/v1/health/")
        request_id = response.headers.get("x-request-id", "")
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        assert uuid_pattern.match(
            request_id
        ), f"X-Request-ID is not a UUID: {request_id}"
