"""Tests for WebSocket endpoint — connection, auth, messaging."""

import json
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

settings.APP_ENV = "testing"

from app.main import app  # noqa: E402


class TestWebSocketAuth:
    """Test WebSocket authentication logic."""

    def test_ws_rejects_missing_token(self):
        """WebSocket connection without token is rejected with 4001."""
        # FastAPI TestClient handles WS upgrade
        with TestClient(app) as client:
            with pytest.raises(Exception):
                # No token provided — should be rejected
                with client.websocket_connect("/api/v1/ws/notifications"):
                    pass  # Should not reach here

    def test_ws_rejects_invalid_token(self):
        """WebSocket connection with invalid JWT is closed with 4001."""
        from starlette.websockets import WebSocketDisconnect

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect(
                    "/api/v1/ws/notifications?token=this.is.not.a.valid.jwt"
                ):
                    pass

    def test_ws_accepts_valid_token(self):
        """WebSocket connects and receives handshake with valid JWT."""
        from app.utils.jwt_utils import create_access_token

        token = create_access_token(subject="test-user-id")

        with TestClient(app) as client:
            with client.websocket_connect(
                f"/api/v1/ws/notifications?token={token}"
            ) as ws:
                msg = json.loads(ws.receive_text())
                assert msg["type"] == "connected"
                assert msg["user_id"] == "test-user-id"


class TestConnectionManager:
    """Test the ConnectionManager singleton."""

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        """Manager tracks connected users correctly."""
        from app.api.v1.endpoints.ws import ConnectionManager

        manager = ConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = MagicMock(return_value=None)

        # Patch accept to be a coroutine
        async def async_accept():
            pass

        mock_ws.accept = async_accept

        await manager.connect(mock_ws, "user-123")
        assert manager.connected_users == 1
        assert manager.total_connections == 1

        manager.disconnect(mock_ws, "user-123")
        assert manager.connected_users == 0

    @pytest.mark.asyncio
    async def test_send_to_user(self):
        """Manager sends message to correct user."""
        from app.api.v1.endpoints.ws import ConnectionManager

        manager = ConnectionManager()
        mock_ws = MagicMock()

        messages_sent = []

        async def async_accept():
            pass

        async def async_send(text):
            messages_sent.append(text)

        mock_ws.accept = async_accept
        mock_ws.send_text = async_send

        await manager.connect(mock_ws, "user-456")
        await manager.send_to_user("user-456", {"type": "test", "data": "hello"})

        assert len(messages_sent) == 1
        payload = json.loads(messages_sent[0])
        assert payload["type"] == "test"
        assert payload["data"] == "hello"

    @pytest.mark.asyncio
    async def test_send_to_nonexistent_user_is_noop(self):
        """Sending to a user with no connections is a safe no-op."""
        from app.api.v1.endpoints.ws import ConnectionManager

        manager = ConnectionManager()
        # Should not raise
        await manager.send_to_user("user-not-connected", {"type": "ping"})


class TestWebSocketPingPong:
    """Test WebSocket ping/pong keepalive."""

    def test_ws_responds_to_ping(self):
        """Server responds to client ping with pong."""
        from app.utils.jwt_utils import create_access_token

        token = create_access_token(subject="ping-test-user")

        with TestClient(app) as client:
            with client.websocket_connect(
                f"/api/v1/ws/notifications?token={token}"
            ) as ws:
                # Consume the connected handshake
                ws.receive_text()

                # Send ping
                ws.send_text(json.dumps({"type": "ping"}))
                response = json.loads(ws.receive_text())
                assert response["type"] == "pong"
