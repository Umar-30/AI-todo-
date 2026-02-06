"""
Recurrence date calculation logic.

T033-T036: Handle daily, weekly, monthly recurrence patterns.
"""
from datetime import datetime, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta


def calculate_next_occurrence(
    current_due_date: datetime,
    recurrence_pattern: str,
    recurrence_end_date: Optional[datetime] = None,
) -> Optional[datetime]:
    """
    Calculate the next occurrence date based on recurrence pattern.

    Args:
        current_due_date: The current task's due date
        recurrence_pattern: One of 'daily', 'weekly', 'monthly'
        recurrence_end_date: Optional end date for recurrence

    Returns:
        The next occurrence datetime, or None if recurrence has ended
    """
    if not current_due_date:
        return None

    if not recurrence_pattern:
        return None

    pattern = recurrence_pattern.lower()

    # T034: Handle daily recurrence pattern (add 1 day)
    if pattern == "daily":
        next_date = current_due_date + timedelta(days=1)

    # T035: Handle weekly recurrence pattern (add 7 days)
    elif pattern == "weekly":
        next_date = current_due_date + timedelta(days=7)

    # T036: Handle monthly recurrence pattern with edge cases
    elif pattern == "monthly":
        # Use relativedelta to handle month boundaries correctly
        # e.g., Jan 31 -> Feb 28, Mar 31 -> Apr 30
        next_date = current_due_date + relativedelta(months=1)

    else:
        # Unknown pattern
        return None

    # Check if we've exceeded the end date
    if recurrence_end_date and next_date > recurrence_end_date:
        return None

    return next_date


def is_recurring_task(task_data: dict) -> bool:
    """
    Check if a task is a recurring task.

    Args:
        task_data: Task data dictionary

    Returns:
        True if task has a recurrence pattern set
    """
    pattern = task_data.get("recurrence_pattern") or task_data.get("recurrencePattern")
    return bool(pattern)


def should_create_next_occurrence(task_data: dict) -> bool:
    """
    Determine if next occurrence should be created for a completed recurring task.

    Args:
        task_data: Task data dictionary

    Returns:
        True if next occurrence should be created
    """
    if not is_recurring_task(task_data):
        return False

    # Get recurrence end date
    end_date_str = task_data.get("recurrence_end_date") or task_data.get("recurrenceEndDate")
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            if datetime.now(end_date.tzinfo) > end_date:
                return False
        except (ValueError, TypeError):
            pass

    return True
