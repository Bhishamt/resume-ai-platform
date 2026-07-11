"""WebSocket endpoint for real-time notifications.

Clients connect to:
    ws://<host>/api/v1/ws/notifications?token=<jwt_access_token>

Events pushed to clients:
    { "type": "task_progress", "task_id": "...", "status": "...", "progress": 0-100 }
    { "type": "analysis_complete", "resume_id": "...", "ats_score": 87.5 }
    { "type": "job_match_complete", "match_id": "...", "match_score": 72.0 }
    { "type": "ai_ready", "feedback_id": "...", "request_type": "review" }
    { "type": "system", "message": "...", "level": "info|warning|error" }

The ConnectionManager is a module-level singleton used by Celery task callbacks
to push updates after long-running jobs complete.
"""

import json
import logging
from typing import Dict, List
from uuid import UUID

import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.utils.jwt_utils import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections, keyed by user_id."""

    def __init__(self) -> None:
        # user_id (str) → list of active WebSocket connections
        self._active: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        if user_id not in self._active:
            self._active[user_id] = []
        self._active[user_id].append(websocket)
        logger.info("WS connected: user=%s total_connections=%d", user_id, self.total_connections)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        if user_id in self._active:
            try:
                self._active[user_id].remove(websocket)
            except ValueError:
                pass
            if not self._active[user_id]:
                del self._active[user_id]
        logger.info("WS disconnected: user=%s total_connections=%d", user_id, self.total_connections)

    async def send_to_user(self, user_id: str, payload: dict) -> None:
        """Send a JSON message to all connections for a given user."""
        connections = self._active.get(user_id, [])
        dead: List[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, user_id)

    async def broadcast(self, payload: dict) -> None:
        """Send a JSON message to every connected client (admin broadcasts)."""
        for user_id in list(self._active.keys()):
            await self.send_to_user(user_id, payload)

    @property
    def total_connections(self) -> int:
        return sum(len(conns) for conns in self._active.values())

    @property
    def connected_users(self) -> int:
        return len(self._active)


# Module-level singleton — importable by Celery task callbacks
manager = ConnectionManager()


def _authenticate_token(token: str) -> str | None:
    """Decode JWT and return user_id string, or None on failure."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """WebSocket endpoint for real-time user notifications.

    Authentication is performed via ?token= query parameter since WebSocket
    upgrade requests cannot carry custom headers in browser environments.
    """
    user_id = _authenticate_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized: invalid or expired token")
        logger.warning("WS rejected: invalid token")
        return

    await manager.connect(websocket, user_id)

    # Send welcome handshake
    await websocket.send_text(json.dumps({
        "type": "connected",
        "message": "Real-time notifications active",
        "user_id": user_id,
    }))

    try:
        while True:
            # Keep alive — receive pings or client messages
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass  # Ignore malformed messages

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as exc:
        logger.error("WS error for user %s: %s", user_id, exc)
        manager.disconnect(websocket, user_id)
