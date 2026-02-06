"""
Event handlers for recurring task processing.

T037-T039: Handle task.completed events and create next occurrences.
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

import httpx

from .recurrence import calculate_next_occurrence, should_create_next_occurrence

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
BACKEND_APP_ID = os.getenv("BACKEND_APP_ID", "todo-backend")
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")


async def handle_task_completed(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a task.completed event.

    If the completed task is a recurring task, creates the next occurrence
    via Dapr service invocation to the backend.

    Args:
        event_data: CloudEvent data containing task information

    Returns:
        Result dictionary with status and details
    """
    task_data = event_data.get("data", {})
    task_id = task_data.get("taskId") or task_data.get("task_id")
    user_id = task_data.get("userId") or task_data.get("user_id")
    correlation_id = event_data.get("correlationid")

    logger.info(f"Processing task.completed for task {task_id}, correlation_id={correlation_id}")

    # Check if this is a recurring task that needs next occurrence
    if not should_create_next_occurrence(task_data):
        logger.info(f"Task {task_id} is not recurring or recurrence has ended")
        return {"status": "skipped", "reason": "not_recurring"}

    # Get current due date and recurrence info
    due_date_str = task_data.get("dueDate") or task_data.get("due_date")
    recurrence_pattern = task_data.get("recurrencePattern") or task_data.get("recurrence_pattern")
    recurrence_end_str = task_data.get("recurrenceEndDate") or task_data.get("recurrence_end_date")

    if not due_date_str:
        logger.warning(f"Recurring task {task_id} has no due date, cannot calculate next occurrence")
        return {"status": "error", "reason": "no_due_date"}

    # Parse dates
    try:
        current_due = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        recurrence_end = None
        if recurrence_end_str:
            recurrence_end = datetime.fromisoformat(recurrence_end_str.replace("Z", "+00:00"))
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to parse dates for task {task_id}: {e}")
        return {"status": "error", "reason": "invalid_date"}

    # Calculate next occurrence
    next_due = calculate_next_occurrence(current_due, recurrence_pattern, recurrence_end)

    if not next_due:
        logger.info(f"No next occurrence for task {task_id} (recurrence ended)")
        return {"status": "completed", "reason": "recurrence_ended"}

    # T038: Create new task via Dapr service invocation
    new_task = await create_next_task_occurrence(
        user_id=user_id,
        original_task=task_data,
        next_due_date=next_due,
        parent_task_id=task_id,
        correlation_id=correlation_id,
    )

    if new_task:
        # T039: The backend automatically publishes task.created event
        logger.info(f"Created next occurrence {new_task.get('id')} for recurring task {task_id}")
        return {
            "status": "created",
            "new_task_id": new_task.get("id"),
            "next_due_date": next_due.isoformat(),
        }

    return {"status": "error", "reason": "failed_to_create"}


async def create_next_task_occurrence(
    user_id: str,
    original_task: Dict[str, Any],
    next_due_date: datetime,
    parent_task_id: str,
    correlation_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Create the next occurrence of a recurring task via Dapr service invocation.

    Args:
        user_id: User ID for the task
        original_task: Original task data to copy from
        next_due_date: Due date for the new occurrence
        parent_task_id: ID of the parent recurring task
        correlation_id: Correlation ID for distributed tracing

    Returns:
        Created task data or None if failed
    """
    # Build the new task payload
    new_task_data = {
        "user_id": user_id,
        "title": original_task.get("title"),
        "description": original_task.get("description"),
        "priority": original_task.get("priority"),
        "tags": original_task.get("tags"),
        "due_date": next_due_date.isoformat(),
        "reminder_time": None,  # Reset reminder for new occurrence
        "recurrence_pattern": original_task.get("recurrencePattern") or original_task.get("recurrence_pattern"),
        "recurrence_end_date": original_task.get("recurrenceEndDate") or original_task.get("recurrence_end_date"),
    }

    # Calculate new reminder time if original had one relative to due date
    original_reminder = original_task.get("reminderTime") or original_task.get("reminder_time")
    original_due = original_task.get("dueDate") or original_task.get("due_date")
    if original_reminder and original_due:
        try:
            orig_reminder_dt = datetime.fromisoformat(original_reminder.replace("Z", "+00:00"))
            orig_due_dt = datetime.fromisoformat(original_due.replace("Z", "+00:00"))
            reminder_offset = orig_due_dt - orig_reminder_dt
            new_reminder = next_due_date - reminder_offset
            new_task_data["reminder_time"] = new_reminder.isoformat()
        except (ValueError, TypeError):
            pass

    # Invoke backend via Dapr service invocation
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/tasks/create"

    headers = {"Content-Type": "application/json"}
    if correlation_id:
        headers["x-correlation-id"] = correlation_id

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=new_task_data, headers=headers)

            if response.status_code == 200 or response.status_code == 201:
                return response.json()

            logger.error(f"Failed to create task occurrence: {response.status_code} - {response.text}")
            return None

    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to backend via Dapr: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error creating task occurrence: {e}")
        return None
