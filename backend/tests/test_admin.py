"""Tests for Phase 9 — Enterprise Admin Panel.

Tests cover:
- RBAC enforcement (non-admin blocked, admin allowed)
- Dashboard stats endpoint
- User list, update, delete
- Audit log retrieval
- System settings read/write
- Notifications create & list
- System health endpoint
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_admin_user, get_current_user, get_db
from app.main import app
from app.models.user import User

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_user(role: str = "user", is_active: bool = True) -> User:
    return User(
        id=uuid.uuid4(),
        full_name="Test User",
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hashed",
        role=role,
        is_active=is_active,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture()
def admin_user() -> User:
    return _make_user(role="admin")


@pytest.fixture()
def regular_user() -> User:
    return _make_user(role="user")


@pytest.fixture()
def mock_db() -> MagicMock:
    """A mock DB session — prevents real DB calls in unit tests."""
    return MagicMock()


@pytest.fixture()
def client_as_admin(admin_user: User, mock_db: MagicMock) -> TestClient:
    """TestClient with admin dependency overrides."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_admin_user] = lambda: admin_user
    app.dependency_overrides[get_current_user] = lambda: admin_user
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_as_user(regular_user: User, mock_db: MagicMock) -> TestClient:
    """TestClient with regular-user dependency overrides (no admin access)."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: regular_user
    # Intentionally do NOT override get_admin_user → real check fires
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_unauthenticated() -> TestClient:
    """TestClient with no auth overrides."""
    app.dependency_overrides.clear()
    return TestClient(app)


# ---------------------------------------------------------------------------
# RBAC Tests
# ---------------------------------------------------------------------------


class TestRBAC:
    """Verify that admin routes are protected and reject non-admin users."""

    def test_admin_dashboard_requires_auth(self, client_unauthenticated: TestClient):
        """Unauthenticated request must return 401 or 422."""
        resp = client_unauthenticated.get("/api/v1/admin/dashboard")
        assert resp.status_code in (401, 422)

    def test_admin_dashboard_blocks_regular_user(self, client_as_user: TestClient):
        """Regular user must receive 403 Forbidden."""
        resp = client_as_user.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": "Bearer faketoken"},
        )
        assert resp.status_code == 403

    def test_admin_users_blocks_regular_user(self, client_as_user: TestClient):
        resp = client_as_user.get(
            "/api/v1/admin/users",
            headers={"Authorization": "Bearer faketoken"},
        )
        assert resp.status_code == 403

    def test_admin_logs_blocks_regular_user(self, client_as_user: TestClient):
        resp = client_as_user.get(
            "/api/v1/admin/logs",
            headers={"Authorization": "Bearer faketoken"},
        )
        assert resp.status_code == 403

    def test_admin_settings_blocks_regular_user(self, client_as_user: TestClient):
        resp = client_as_user.get(
            "/api/v1/admin/settings",
            headers={"Authorization": "Bearer faketoken"},
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class TestDashboard:
    def test_dashboard_returns_stats(
        self, client_as_admin: TestClient, admin_user: User
    ):
        with patch(
            "app.api.v1.endpoints.admin.analytics_service.get_dashboard_stats"
        ) as mock_stats:
            from app.schemas.admin import DashboardStats

            mock_stats.return_value = DashboardStats(
                total_users=100,
                active_users=90,
                new_users_today=5,
                new_users_this_month=30,
                total_resumes=250,
                resumes_today=10,
                total_analysis_reports=400,
                total_job_matches=150,
                total_ai_requests=600,
                ai_requests_today=20,
                total_tokens_used=1_200_000,
                avg_response_time_ms=340.5,
            )

            resp = client_as_admin.get("/api/v1/admin/dashboard")
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["data"]["total_users"] == 100
            assert body["data"]["active_users"] == 90
            assert body["data"]["total_ai_requests"] == 600


# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------


class TestUserManagement:
    def test_list_users_returns_paginated_data(self, client_as_admin: TestClient):
        with patch(
            "app.api.v1.endpoints.admin.user_management.list_users"
        ) as mock_list:
            from app.schemas.admin import AdminUserListResponse, PaginatedMeta

            mock_list.return_value = AdminUserListResponse(
                users=[],
                meta=PaginatedMeta(total=0, page=1, per_page=20, pages=0),
            )
            resp = client_as_admin.get("/api/v1/admin/users")
            assert resp.status_code == 200
            body = resp.json()
            assert "users" in body["data"]
            assert "meta" in body["data"]

    def test_update_user_role(self, client_as_admin: TestClient, admin_user: User):
        target_id = str(uuid.uuid4())
        with patch(
            "app.api.v1.endpoints.admin.user_management.update_user"
        ) as mock_update:
            from app.schemas.admin import AdminUserResponse

            mock_update.return_value = AdminUserResponse(
                id=uuid.UUID(target_id),
                full_name="Jane Doe",
                email="jane@example.com",
                role="admin",
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
            )

            resp = client_as_admin.put(
                f"/api/v1/admin/users/{target_id}",
                json={"role": "admin"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["data"]["role"] == "admin"

    def test_delete_user(self, client_as_admin: TestClient):
        target_id = str(uuid.uuid4())
        with patch(
            "app.api.v1.endpoints.admin.user_management.delete_user"
        ) as mock_delete:
            mock_delete.return_value = None
            resp = client_as_admin.delete(f"/api/v1/admin/users/{target_id}")
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True

    def test_cannot_update_own_account(
        self, client_as_admin: TestClient, admin_user: User
    ):
        """Admin endpoint should reject self-modification."""
        with patch(
            "app.api.v1.endpoints.admin.user_management.update_user",
            side_effect=__import__(
                "app.core.exceptions", fromlist=["BadRequestError"]
            ).BadRequestError("Admins cannot modify their own account."),
        ):
            resp = client_as_admin.put(
                f"/api/v1/admin/users/{admin_user.id}",
                json={"role": "user"},
            )
            assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------


class TestAuditLogs:
    def test_get_logs_returns_list(self, client_as_admin: TestClient):
        with patch("app.api.v1.endpoints.admin.log_service.get_logs") as mock_logs:
            from app.schemas.admin import AdminLogListResponse, PaginatedMeta

            mock_logs.return_value = AdminLogListResponse(
                logs=[],
                meta=PaginatedMeta(total=0, page=1, per_page=50, pages=0),
            )
            resp = client_as_admin.get("/api/v1/admin/logs")
            assert resp.status_code == 200
            body = resp.json()
            assert "logs" in body["data"]
            assert body["data"]["meta"]["page"] == 1

    def test_logs_support_action_filter(self, client_as_admin: TestClient):
        with patch("app.api.v1.endpoints.admin.log_service.get_logs") as mock_logs:
            from app.schemas.admin import AdminLogListResponse, PaginatedMeta

            mock_logs.return_value = AdminLogListResponse(
                logs=[],
                meta=PaginatedMeta(total=0, page=1, per_page=50, pages=0),
            )
            resp = client_as_admin.get(
                "/api/v1/admin/logs?action=change_role&entity=user"
            )
            assert resp.status_code == 200
            _, kwargs = mock_logs.call_args
            assert kwargs.get("action") == "change_role"
            assert kwargs.get("entity") == "user"


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class TestSettings:
    def test_get_settings(self, client_as_admin: TestClient):
        with patch("app.api.v1.endpoints.admin.settings_service.get_all") as mock_get:
            from app.schemas.admin import SettingsListResponse

            mock_get.return_value = SettingsListResponse(settings=[])
            resp = client_as_admin.get("/api/v1/admin/settings")
            assert resp.status_code == 200

    def test_update_settings(self, client_as_admin: TestClient):
        with patch(
            "app.api.v1.endpoints.admin.settings_service.bulk_update"
        ) as mock_update:
            from app.schemas.admin import SettingsListResponse

            mock_update.return_value = SettingsListResponse(settings=[])
            resp = client_as_admin.put(
                "/api/v1/admin/settings",
                json={
                    "settings": [
                        {
                            "key": "maintenance_mode",
                            "value": "true",
                            "description": "Enable maintenance",
                        }
                    ]
                },
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True

    def test_settings_validates_payload(self, client_as_admin: TestClient):
        """Empty settings list should fail validation."""
        resp = client_as_admin.put(
            "/api/v1/admin/settings",
            json={"settings": []},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


class TestNotifications:
    def test_get_notifications(self, client_as_admin: TestClient, admin_user: User):
        with patch(
            "app.api.v1.endpoints.admin.notification_service.list_notifications"
        ) as mock_list:
            from app.schemas.admin import (NotificationListResponse,
                                           PaginatedMeta)

            mock_list.return_value = NotificationListResponse(
                notifications=[],
                unread_count=0,
                meta=PaginatedMeta(total=0, page=1, per_page=50, pages=0),
            )
            resp = client_as_admin.get("/api/v1/admin/notifications")
            assert resp.status_code == 200

    def test_create_notification(self, client_as_admin: TestClient):
        target_user_id = uuid.uuid4()
        with patch(
            "app.api.v1.endpoints.admin.notification_service.create_notification"
        ) as mock_create:
            from app.schemas.admin import NotificationResponse

            mock_create.return_value = NotificationResponse(
                id=uuid.uuid4(),
                user_id=target_user_id,
                title="Test",
                message="Hello",
                type="info",
                is_read=False,
                created_at=datetime.now(timezone.utc),
            )
            resp = client_as_admin.post(
                "/api/v1/admin/notifications",
                json={
                    "user_id": str(target_user_id),
                    "title": "Test",
                    "message": "Hello",
                    "type": "info",
                },
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["data"]["title"] == "Test"


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------


class TestSystemHealth:
    def test_system_health_returns_expected_fields(
        self, client_as_admin: TestClient, mock_db: MagicMock
    ):
        # Mock the db.execute call used for the health probe
        mock_db.execute.return_value = True

        resp = client_as_admin.get("/api/v1/admin/system")
        assert resp.status_code == 200
        body = resp.json()
        data = body["data"]
        assert "api_status" in data
        assert data["api_status"] == "healthy"
        assert "database_status" in data
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data
        assert "uptime_seconds" in data
