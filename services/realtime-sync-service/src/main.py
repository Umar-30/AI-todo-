"""
Realtime Sync Service - FastAPI Application with WebSocket support.

T044, T047: FastAPI app scaffold with WebSocket support and Dapr subscription.
Subscribes to task-updates topic and broadcasts changes via WebSocket.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import jwt
from fastapi import FastAPI, Query, Request, Response, WebSocket, WebSocketDisconnect

from .handlers import handle_task_update
from .websocket import connection_manager

# Configure structured JSON logging for Kubernetes
import json as _json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return _json.dumps({
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": "realtime-sync-service",
            "logger": record.name,
            "message": record.getMessage(),
        })

_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

# Configuration
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")
TOPIC_TASK_UPDATES = "task-updates"
JWT_SECRET = os.getenv("JWT_SECRET", "todo-ai-chatbot-secret")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return user data."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.JWTError as e:
        logger.warning(f"Token validation failed: {e}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Realtime Sync Service starting up...")
    yield
    logger.info("Realtime Sync Service shutting down...")


app = FastAPI(
    title="Realtime Sync Service",
    description="WebSocket-based real-time task synchronization service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    user_count = await connection_manager.get_active_user_count()
    conn_count = await connection_manager.get_connection_count()
    return {
        "status": "healthy",
        "service": "realtime-sync-service",
        "active_users": user_count,
        "connections": conn_count,
    }


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription configuration endpoint.

    T047: Implement Dapr subscription for task-updates topic.
    Returns the list of Pub/Sub subscriptions this service wants.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_UPDATES,
            "route": "/events/task-update",
            "metadata": {
                "rawPayload": "true",
            },
        }
    ]


@app.post("/events/task-update")
async def handle_task_update_event(request: Request) -> Response:
    """
    Handle incoming task update events from Dapr Pub/Sub.

    Receives sync.task_changed events and broadcasts to connected WebSocket clients.
    """
    try:
        event_data: Dict[str, Any] = await request.json()
        event_type = event_data.get("type", "")

        logger.info(f"Received event: {event_type}")

        # Process the task update
        result = await handle_task_update(event_data)
        logger.debug(f"Processed task update: {result}")

        return Response(status_code=200, content="OK")

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # Return 200 to acknowledge the message (prevent redelivery)
        return Response(status_code=200, content="OK")


@app.websocket("/ws/tasks")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time task updates.

    Clients connect with their JWT token as a query parameter.
    Receives task updates for the authenticated user.
    """
    # Validate token
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return

    user_data = verify_token(token)
    if not user_data:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = user_data.get("sub")
    if not user_id:
        await websocket.close(code=4001, reason="Invalid user")
        return

    # Connect and track session
    session_id = await connection_manager.connect(websocket, user_id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "sessionId": session_id,
            "userId": user_id,
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages (ping/pong, etc.)
                data = await websocket.receive_text()

                # Handle ping
                if data == "ping":
                    await websocket.send_text("pong")

            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")

    finally:
        await connection_manager.disconnect(websocket, user_id, session_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8002")),
        reload=True,
    )
