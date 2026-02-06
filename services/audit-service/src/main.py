"""
Audit Service - FastAPI Application.

T086-T088, T092: FastAPI app with Dapr subscriptions for all task events
and query endpoint for audit history.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request, Response

from .handlers import handle_task_event
from .storage import ensure_table, get_audit_history

# Configure structured JSON logging for Kubernetes
import json as _json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return _json.dumps({
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": "audit-service",
            "logger": record.name,
            "message": record.getMessage(),
        })

_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")
TOPIC_TASK_EVENTS = "task-events"
TOPIC_TASK_UPDATES = "task-updates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Audit Service starting up...")
    ensure_table()
    yield
    logger.info("Audit Service shutting down...")


app = FastAPI(
    title="Audit Service",
    description="Immutable audit trail for all task changes",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "audit-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    T087-T088: Dapr subscriptions for ALL task-events and task-updates.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_EVENTS,
            "route": "/events/task-event",
            "metadata": {"rawPayload": "true"},
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_UPDATES,
            "route": "/events/task-update",
            "metadata": {"rawPayload": "true"},
        },
    ]


@app.post("/events/task-event")
async def handle_task_event_endpoint(request: Request) -> Response:
    """Handle incoming task events from task-events topic."""
    try:
        event_data: Dict[str, Any] = await request.json()
        result = await handle_task_event(event_data)
        logger.info(f"Audit task-event: {result}")
        return Response(status_code=200, content="OK")
    except Exception as e:
        logger.error(f"Error processing task-event: {e}")
        return Response(status_code=200, content="OK")


@app.post("/events/task-update")
async def handle_task_update_endpoint(request: Request) -> Response:
    """Handle incoming task events from task-updates topic."""
    try:
        event_data: Dict[str, Any] = await request.json()
        result = await handle_task_event(event_data)
        logger.info(f"Audit task-update: {result}")
        return Response(status_code=200, content="OK")
    except Exception as e:
        logger.error(f"Error processing task-update: {e}")
        return Response(status_code=200, content="OK")


@app.get("/audit/{task_id}")
async def get_task_audit_history(task_id: str) -> List[Dict[str, Any]]:
    """
    T092: Query endpoint GET /audit/{task_id}.

    Returns chronological audit history for a task.
    """
    try:
        history = get_audit_history(task_id)
        return history
    except Exception as e:
        logger.error(f"Error fetching audit history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit history")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8004")),
        reload=True,
    )
