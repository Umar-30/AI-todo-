"""
Recurring Task Service - FastAPI Application.

T031-T032: FastAPI app scaffold with Dapr subscription for task.completed events.
Subscribes to task-events topic and handles recurring task logic.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, Response

from .handlers import handle_task_completed

# Configure structured JSON logging for Kubernetes
import json as _json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return _json.dumps({
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": "recurring-task-service",
            "logger": record.name,
            "message": record.getMessage(),
        })

_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

# Dapr configuration
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")
TOPIC_TASK_EVENTS = "task-events"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Recurring Task Service starting up...")
    yield
    logger.info("Recurring Task Service shutting down...")


app = FastAPI(
    title="Recurring Task Service",
    description="Microservice for handling recurring task auto-generation",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "recurring-task-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription configuration endpoint.

    T032: Implement Dapr subscription endpoint for task.completed.
    Returns the list of Pub/Sub subscriptions this service wants.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_EVENTS,
            "route": "/events/task-completed",
            "metadata": {
                "rawPayload": "true",
            },
        }
    ]


@app.post("/events/task-completed")
async def handle_task_event(request: Request) -> Response:
    """
    Handle incoming task events from Dapr Pub/Sub.

    Filters for task.completed events and processes recurring tasks.
    """
    try:
        # Parse the CloudEvent
        event_data: Dict[str, Any] = await request.json()
        event_type = event_data.get("type", "")

        logger.info(f"Received event: {event_type}")

        # Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring event type: {event_type}")
            return Response(status_code=200, content="OK")

        # Process the completed task
        result = await handle_task_completed(event_data)
        logger.info(f"Processed task.completed: {result}")

        return Response(status_code=200, content="OK")

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # Return 200 to acknowledge the message (prevent redelivery)
        # Log error for investigation
        return Response(status_code=200, content="OK")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),
        reload=True,
    )
