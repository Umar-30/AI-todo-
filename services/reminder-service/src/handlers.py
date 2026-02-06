"""
Event handlers for reminder service.

T066-T068: Publish reminder events, cancel/reschedule reminders.
"""
import logging
import os
from typing import Any, Dict

import httpx

from .scheduler import (
    add_to_active_list,
    cancel_reminder,
    remove_from_active_list,
    save_reminder,
)

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")
TOPIC_REMINDERS = "reminders"


async def handle_task_created(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle task.created event - schedule reminder if reminder_time is set.

    Args:
        event_data: CloudEvent data

    Returns:
        Result dictionary
    """
    data = event_data.get("data", {})
    task_id = data.get("taskId") or data.get("task_id")
    user_id = data.get("userId") or data.get("user_id")
    reminder_time = data.get("reminderTime") or data.get("reminder_time")
    task_title = data.get("title") or data.get("taskTitle", "Task")

    if not reminder_time:
        return {"status": "skipped", "reason": "no_reminder_time"}

    # Save reminder state
    saved = await save_reminder(task_id, user_id, reminder_time, task_title)
    if saved:
        await add_to_active_list(task_id)
        logger.info(f"Scheduled reminder for task {task_id} at {reminder_time}")
        return {"status": "scheduled", "task_id": task_id}

    return {"status": "error", "reason": "save_failed"}


async def handle_task_updated(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    T068: Handle task.updated event - reschedule reminder if due date changed.

    Args:
        event_data: CloudEvent data

    Returns:
        Result dictionary
    """
    data = event_data.get("data", {})
    task_id = data.get("taskId") or data.get("task_id")
    user_id = data.get("userId") or data.get("user_id")
    reminder_time = data.get("reminderTime") or data.get("reminder_time")
    task_title = data.get("title") or data.get("taskTitle", "Task")

    if not reminder_time:
        # Reminder cleared - cancel existing
        await cancel_reminder(task_id)
        await remove_from_active_list(task_id)
        logger.info(f"Cancelled reminder for task {task_id} (reminder cleared)")
        return {"status": "cancelled", "task_id": task_id}

    # Reschedule: cancel old and create new
    await cancel_reminder(task_id)
    saved = await save_reminder(task_id, user_id, reminder_time, task_title)
    if saved:
        await add_to_active_list(task_id)
        logger.info(f"Rescheduled reminder for task {task_id} at {reminder_time}")
        return {"status": "rescheduled", "task_id": task_id}

    return {"status": "error", "reason": "reschedule_failed"}


async def handle_task_completed(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    T067: Cancel reminders when task completed.

    Args:
        event_data: CloudEvent data

    Returns:
        Result dictionary
    """
    data = event_data.get("data", {})
    task_id = data.get("taskId") or data.get("task_id")

    await cancel_reminder(task_id)
    await remove_from_active_list(task_id)
    logger.info(f"Cancelled reminder for completed task {task_id}")
    return {"status": "cancelled", "task_id": task_id, "reason": "task_completed"}


async def handle_task_deleted(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    T067: Cancel reminders when task deleted.

    Args:
        event_data: CloudEvent data

    Returns:
        Result dictionary
    """
    data = event_data.get("data", {})
    task_id = data.get("taskId") or data.get("task_id")

    await cancel_reminder(task_id)
    await remove_from_active_list(task_id)
    logger.info(f"Cancelled reminder for deleted task {task_id}")
    return {"status": "cancelled", "task_id": task_id, "reason": "task_deleted"}


async def publish_reminder_triggered(task_id: str, user_id: str, task_title: str) -> bool:
    """
    T066: Publish reminder.triggered event when reminder is due.

    Args:
        task_id: The task ID
        user_id: The user ID
        task_title: The task title

    Returns:
        True if published successfully
    """
    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_REMINDERS}"

    event_data = {
        "type": "reminder.triggered",
        "source": "reminder-service",
        "data": {
            "taskId": task_id,
            "userId": user_id,
            "taskTitle": task_title,
            "message": f"Reminder: '{task_title}' is due soon!",
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=event_data, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            logger.info(f"Published reminder.triggered for task {task_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to publish reminder.triggered: {e}")
        return False
