"""
Event handlers for audit service.

T091: Idempotency check and event processing.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from .storage import append_audit_record, check_duplicate

logger = logging.getLogger(__name__)


async def handle_task_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle any task event and create an audit record.

    T091: Includes idempotency check to prevent duplicate events.

    Args:
        event_data: CloudEvent data

    Returns:
        Result dictionary
    """
    event_id = event_data.get("id", str(uuid4()))
    event_type = event_data.get("type", "unknown")
    correlation_id = event_data.get("correlationid")
    timestamp = event_data.get("time", datetime.now(timezone.utc).isoformat())

    # Extract task and user info from data
    data = event_data.get("data", {})
    task_id = data.get("taskId") or data.get("task_id")
    user_id = data.get("userId") or data.get("user_id")

    if not task_id or not user_id:
        logger.warning(f"Event missing task_id or user_id: {event_type}")
        return {"status": "skipped", "reason": "missing_fields"}

    # T091: Idempotency check
    if check_duplicate(event_id):
        logger.info(f"Duplicate event {event_id} skipped")
        return {"status": "skipped", "reason": "duplicate"}

    # Store the audit record
    record_id = append_audit_record(
        event_id=event_id,
        event_type=event_type,
        task_id=task_id,
        user_id=user_id,
        timestamp=timestamp,
        payload=data,
        correlation_id=correlation_id,
    )

    if record_id:
        return {"status": "stored", "record_id": record_id}

    return {"status": "error", "reason": "storage_failed"}
