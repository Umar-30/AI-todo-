"""
Event handlers for realtime sync processing.

T048: Implement event handler to filter by user_id.
"""
import logging
from typing import Any, Dict

from .websocket import connection_manager

logger = logging.getLogger(__name__)


async def handle_task_update(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming task update events from Dapr Pub/Sub.

    T048: Filter events by user_id and broadcast to appropriate sessions.

    Args:
        event_data: CloudEvent data containing task update information

    Returns:
        Result dictionary with status and details
    """
    # Extract data from CloudEvent
    data = event_data.get("data", {})
    event_type = event_data.get("type", "unknown")
    correlation_id = event_data.get("correlationid")

    # Get user_id for routing
    user_id = data.get("userId") or data.get("user_id")

    if not user_id:
        logger.warning(f"Task update event missing user_id, skipping: {event_type}")
        return {"status": "skipped", "reason": "no_user_id"}

    # Get change type and task data
    change_type = data.get("changeType", "updated")
    task_data = data.get("task")
    task_id = data.get("taskId") or data.get("task_id")

    logger.info(
        f"Processing task update: type={change_type}, task_id={task_id}, "
        f"user_id={user_id}, correlation_id={correlation_id}"
    )

    # Build WebSocket message
    ws_message = {
        "type": f"task.{change_type}",
        "taskId": task_id,
        "task": task_data,
        "correlationId": correlation_id,
        "timestamp": event_data.get("time"),
    }

    # Broadcast to all user sessions
    await connection_manager.broadcast_to_user(user_id, ws_message)

    return {
        "status": "broadcast",
        "user_id": user_id,
        "task_id": task_id,
        "change_type": change_type,
    }
