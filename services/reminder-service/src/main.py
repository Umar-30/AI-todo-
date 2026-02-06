"""
Reminder Service - FastAPI Application.

T060-T061, T064: FastAPI app with Dapr subscriptions and cron handler.
Subscribes to task-events topic for scheduling reminders.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, Response

from .handlers import (
    handle_task_completed,
    handle_task_created,
    handle_task_deleted,
    handle_task_updated,
    publish_reminder_triggered,
)
from .scheduler import cancel_reminder, get_due_reminders, remove_from_active_list

# Configure structured JSON logging for Kubernetes
import json as _json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return _json.dumps({
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": "reminder-service",
            "logger": record.name,
            "message": record.getMessage(),
        })

_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")
TOPIC_TASK_EVENTS = "task-events"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Reminder Service starting up...")
    yield
    logger.info("Reminder Service shutting down...")


app = FastAPI(
    title="Reminder Service",
    description="Microservice for due date reminders and notifications",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "reminder-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    T061: Dapr subscription for task.created, task.updated, task.completed, task.deleted.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_EVENTS,
            "route": "/events/task-event",
            "metadata": {
                "rawPayload": "true",
            },
        }
    ]


@app.post("/events/task-event")
async def handle_task_event(request: Request) -> Response:
    """
    Handle incoming task events from Dapr Pub/Sub.
    Routes to appropriate handler based on event type.
    """
    try:
        event_data: Dict[str, Any] = await request.json()
        event_type = event_data.get("type", "")

        logger.info(f"Received event: {event_type}")

        if event_type == "task.created":
            result = await handle_task_created(event_data)
        elif event_type == "task.updated":
            result = await handle_task_updated(event_data)
        elif event_type == "task.completed":
            result = await handle_task_completed(event_data)
        elif event_type == "task.deleted":
            result = await handle_task_deleted(event_data)
        else:
            logger.debug(f"Ignoring event type: {event_type}")
            return Response(status_code=200, content="OK")

        logger.info(f"Processed {event_type}: {result}")
        return Response(status_code=200, content="OK")

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return Response(status_code=200, content="OK")


@app.post("/reminders/check")
async def check_reminders(request: Request) -> Response:
    """
    T064: Cron handler endpoint - checks for due reminders.

    Called by Dapr Cron binding on a schedule (e.g., every minute).
    Queries all pending reminders and fires those that are due.
    """
    logger.info("Running reminder check...")

    try:
        due_reminders = await get_due_reminders()

        if not due_reminders:
            logger.debug("No due reminders found")
            return Response(status_code=200, content="OK")

        logger.info(f"Found {len(due_reminders)} due reminders")

        for reminder in due_reminders:
            task_id = reminder.get("task_id")
            user_id = reminder.get("user_id")
            task_title = reminder.get("task_title", "Task")

            # Publish reminder.triggered event
            published = await publish_reminder_triggered(task_id, user_id, task_title)

            if published:
                # Mark as triggered by removing
                await cancel_reminder(task_id)
                await remove_from_active_list(task_id)
                logger.info(f"Triggered reminder for task {task_id}")

        return Response(status_code=200, content="OK")

    except Exception as e:
        logger.error(f"Error checking reminders: {e}")
        return Response(status_code=200, content="OK")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8003")),
        reload=True,
    )
