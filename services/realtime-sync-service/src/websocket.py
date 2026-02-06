"""
WebSocket connection manager for real-time sync.

T045-T046, T050-T051: WebSocket connection management with user session tracking.
"""
import asyncio
import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

import httpx
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# Dapr configuration for state store
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATESTORE_NAME = os.getenv("DAPR_STATESTORE_NAME", "statestore-redis")

# Buffer settings
MAX_BUFFER_SIZE = 100
BUFFER_TTL_SECONDS = 60


@dataclass
class UserSession:
    """Represents a WebSocket session for a user."""

    session_id: str
    user_id: str
    websocket: WebSocket
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConnectionManager:
    """
    Manages WebSocket connections for real-time task updates.

    T045: Implement WebSocket connection manager.
    T046: Implement user session tracking via Dapr State.
    T050: Handle connection lifecycle (connect/disconnect/reconnect).
    T051: Buffer updates during brief disconnections.
    """

    def __init__(self):
        # Map user_id -> list of active WebSocket sessions
        self._connections: Dict[str, List[UserSession]] = defaultdict(list)
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        # Update buffers for disconnected users (user_id -> list of events)
        self._buffers: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """
        Accept a new WebSocket connection for a user.

        Args:
            websocket: The WebSocket connection
            user_id: The user's ID

        Returns:
            Session ID for this connection
        """
        await websocket.accept()

        session_id = str(uuid4())
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            websocket=websocket,
        )

        async with self._lock:
            self._connections[user_id].append(session)

        # Save session to Dapr state store for distributed tracking
        await self._save_session_state(session)

        logger.info(f"User {user_id} connected with session {session_id}")

        # Send any buffered updates
        await self._send_buffered_updates(user_id, websocket)

        return session_id

    async def disconnect(self, websocket: WebSocket, user_id: str, session_id: str):
        """
        Handle WebSocket disconnection.

        Args:
            websocket: The disconnected WebSocket
            user_id: The user's ID
            session_id: The session ID
        """
        async with self._lock:
            sessions = self._connections.get(user_id, [])
            self._connections[user_id] = [s for s in sessions if s.session_id != session_id]

            # Clean up empty user entries
            if not self._connections[user_id]:
                del self._connections[user_id]

        # Remove from Dapr state store
        await self._delete_session_state(session_id)

        logger.info(f"User {user_id} disconnected session {session_id}")

    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connections for a user.

        T049: Implement broadcast to all user sessions.

        Args:
            user_id: The user's ID
            message: The message to broadcast
        """
        async with self._lock:
            sessions = self._connections.get(user_id, []).copy()

        if not sessions:
            # Buffer the message for when user reconnects
            await self._buffer_update(user_id, message)
            logger.debug(f"No active sessions for user {user_id}, buffering update")
            return

        message_json = json.dumps(message)
        disconnected_sessions = []

        for session in sessions:
            try:
                await session.websocket.send_text(message_json)
                session.last_activity = datetime.now(timezone.utc)
            except Exception as e:
                logger.warning(f"Failed to send to session {session.session_id}: {e}")
                disconnected_sessions.append(session)

        # Clean up disconnected sessions
        for session in disconnected_sessions:
            await self.disconnect(session.websocket, user_id, session.session_id)

    async def get_active_user_count(self) -> int:
        """Get the number of users with active connections."""
        async with self._lock:
            return len(self._connections)

    async def get_connection_count(self) -> int:
        """Get the total number of active connections."""
        async with self._lock:
            return sum(len(sessions) for sessions in self._connections.values())

    async def _buffer_update(self, user_id: str, update: Dict[str, Any]):
        """
        T051: Buffer updates during brief disconnections.

        Args:
            user_id: The user's ID
            update: The update to buffer
        """
        async with self._lock:
            buffer = self._buffers[user_id]

            # Add timestamp for TTL tracking
            update["_buffered_at"] = datetime.now(timezone.utc).isoformat()
            buffer.append(update)

            # Limit buffer size
            if len(buffer) > MAX_BUFFER_SIZE:
                self._buffers[user_id] = buffer[-MAX_BUFFER_SIZE:]

    async def _send_buffered_updates(self, user_id: str, websocket: WebSocket):
        """
        Send buffered updates to a reconnecting user.

        Args:
            user_id: The user's ID
            websocket: The WebSocket to send to
        """
        async with self._lock:
            buffer = self._buffers.pop(user_id, [])

        if not buffer:
            return

        now = datetime.now(timezone.utc)
        valid_updates = []

        for update in buffer:
            # Filter out expired updates
            buffered_at = update.pop("_buffered_at", None)
            if buffered_at:
                try:
                    buffer_time = datetime.fromisoformat(buffered_at)
                    if (now - buffer_time).total_seconds() <= BUFFER_TTL_SECONDS:
                        valid_updates.append(update)
                except (ValueError, TypeError):
                    valid_updates.append(update)
            else:
                valid_updates.append(update)

        if valid_updates:
            logger.info(f"Sending {len(valid_updates)} buffered updates to user {user_id}")
            for update in valid_updates:
                try:
                    await websocket.send_text(json.dumps(update))
                except Exception as e:
                    logger.error(f"Failed to send buffered update: {e}")
                    break

    async def _save_session_state(self, session: UserSession):
        """
        T046: Save session state to Dapr State Store for distributed tracking.

        Args:
            session: The session to save
        """
        state_key = f"session:{session.session_id}"
        state_value = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "connected_at": session.connected_at.isoformat(),
            "service_instance": os.getenv("HOSTNAME", "local"),
        }

        url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    url,
                    json=[
                        {
                            "key": state_key,
                            "value": state_value,
                            "metadata": {"ttlInSeconds": "3600"},  # 1 hour TTL
                        }
                    ],
                )
        except Exception as e:
            logger.warning(f"Failed to save session state to Dapr: {e}")

    async def _delete_session_state(self, session_id: str):
        """
        Delete session state from Dapr State Store.

        Args:
            session_id: The session ID to delete
        """
        state_key = f"session:{session_id}"
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{state_key}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.delete(url)
        except Exception as e:
            logger.warning(f"Failed to delete session state from Dapr: {e}")


# Global connection manager instance
connection_manager = ConnectionManager()
