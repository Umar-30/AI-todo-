"""
Reminder scheduling and state management.

T062, T065: Reminder state storage via Dapr State API and check logic.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATESTORE_NAME = os.getenv("DAPR_STATESTORE_NAME", "statestore-redis")


async def save_reminder(task_id: str, user_id: str, reminder_time: str, task_title: str) -> bool:
    """
    Save a reminder to Dapr State Store.

    Args:
        task_id: The task ID
        user_id: The user ID
        reminder_time: ISO8601 reminder time
        task_title: Task title for the notification message

    Returns:
        True if saved successfully
    """
    state_key = f"reminder:{task_id}"
    state_value = {
        "task_id": task_id,
        "user_id": user_id,
        "reminder_time": reminder_time,
        "task_title": task_title,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=[{"key": state_key, "value": state_value}])
            response.raise_for_status()
            logger.info(f"Saved reminder for task {task_id} at {reminder_time}")
            return True
    except Exception as e:
        logger.error(f"Failed to save reminder for task {task_id}: {e}")
        return False


async def cancel_reminder(task_id: str) -> bool:
    """
    Cancel a reminder by deleting it from Dapr State Store.

    Args:
        task_id: The task ID whose reminder to cancel

    Returns:
        True if deleted successfully
    """
    state_key = f"reminder:{task_id}"
    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{state_key}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(url)
            response.raise_for_status()
            logger.info(f"Cancelled reminder for task {task_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to cancel reminder for task {task_id}: {e}")
        return False


async def get_reminder(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a reminder from Dapr State Store.

    Args:
        task_id: The task ID

    Returns:
        Reminder data or None
    """
    state_key = f"reminder:{task_id}"
    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{state_key}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 204 or not response.content:
                return None
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get reminder for task {task_id}: {e}")
        return None


async def get_due_reminders() -> List[Dict[str, Any]]:
    """
    T065: Query all reminders that are due now.

    Uses Dapr State Store query API to find pending reminders
    whose reminder_time has passed.

    Returns:
        List of due reminder data
    """
    # Dapr state store query (for Redis, uses SCAN)
    # Since basic state stores don't support queries well,
    # we use a tracking key that lists all active reminder keys
    tracker_key = "reminder:active_list"
    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{tracker_key}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 204 or not response.content:
                return []

            active_keys = response.json()
            if not isinstance(active_keys, list):
                return []

        now = datetime.now(timezone.utc)
        due_reminders = []

        for key in active_keys:
            reminder = await get_reminder(key)
            if reminder and reminder.get("status") == "pending":
                try:
                    reminder_time = datetime.fromisoformat(
                        reminder["reminder_time"].replace("Z", "+00:00")
                    )
                    if reminder_time <= now:
                        due_reminders.append(reminder)
                except (ValueError, KeyError):
                    continue

        return due_reminders

    except Exception as e:
        logger.error(f"Failed to query due reminders: {e}")
        return []


async def add_to_active_list(task_id: str) -> bool:
    """Add a task_id to the active reminders tracking list."""
    tracker_key = "reminder:active_list"
    url_get = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{tracker_key}"
    url_save = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get current list
            response = await client.get(url_get)
            active_list = []
            if response.status_code != 204 and response.content:
                active_list = response.json()
                if not isinstance(active_list, list):
                    active_list = []

            # Add task_id if not already present
            if task_id not in active_list:
                active_list.append(task_id)

            # Save updated list
            await client.post(url_save, json=[{"key": tracker_key, "value": active_list}])
            return True
    except Exception as e:
        logger.error(f"Failed to add {task_id} to active list: {e}")
        return False


async def remove_from_active_list(task_id: str) -> bool:
    """Remove a task_id from the active reminders tracking list."""
    tracker_key = "reminder:active_list"
    url_get = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{tracker_key}"
    url_save = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url_get)
            active_list = []
            if response.status_code != 204 and response.content:
                active_list = response.json()
                if not isinstance(active_list, list):
                    active_list = []

            if task_id in active_list:
                active_list.remove(task_id)

            await client.post(url_save, json=[{"key": tracker_key, "value": active_list}])
            return True
    except Exception as e:
        logger.error(f"Failed to remove {task_id} from active list: {e}")
        return False
