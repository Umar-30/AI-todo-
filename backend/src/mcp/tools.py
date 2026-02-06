"""
MCP tools for task operations.

Provides stateless task management operations that read/write directly to the database.
All operations require a user_id for data isolation.
Publishes real-time events when tasks change.

Enhanced with recurring tasks, tags, priorities, and Dapr event publishing (Phase V).
T027: Update add_task MCP tool to accept priority, tags, recurrence
T028: Update update_task MCP tool to handle new fields
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..database import get_engine
from ..models.task import Task
from ..events import (
    task_event_manager,
    TaskEvent,
    TaskEventType,
    publish_task_event_sync,
    publish_task_update_sync,
)


class TaskNotFoundError(Exception):
    """Raised when a task is not found or doesn't belong to the user."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def _get_session() -> Session:
    """Get a new database session."""
    return Session(get_engine())


def _validate_user_id(user_id: str) -> None:
    """Validate that user_id is provided and not empty."""
    if not user_id or not user_id.strip():
        raise ValidationError("user_id is required and cannot be empty")


def _validate_task_id(task_id: str) -> UUID:
    """Validate and convert task_id string to UUID."""
    try:
        return UUID(task_id)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid task_id format: {task_id}")


def _get_user_task(session: Session, user_id: str, task_id: UUID) -> Task:
    """
    Get a task that belongs to the specified user.

    Raises TaskNotFoundError if task doesn't exist or doesn't belong to user.
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found for user {user_id}")
    return task


def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    recurrence_pattern: Optional[str] = None,
    recurrence_end_date: Optional[str] = None,
) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: Owner's user identifier (required)
        title: Task title (required)
        description: Task description (optional)
        priority: Priority level - high, medium, low (optional)
        tags: List of tags, max 10 items (optional)
        due_date: Due date in ISO8601 format (optional)
        reminder_time: Reminder time in ISO8601 format (optional)
        recurrence_pattern: Recurrence - daily, weekly, monthly (optional)
        recurrence_end_date: End date for recurrence in ISO8601 format (optional)

    Returns:
        dict with created task details

    Raises:
        ValidationError: If required parameters are missing or invalid
    """
    _validate_user_id(user_id)

    if not title or not title.strip():
        raise ValidationError("title is required and cannot be empty")

    # Validate priority
    if priority is not None:
        priority = priority.strip().lower()
        if priority not in ("high", "medium", "low"):
            raise ValidationError("priority must be 'high', 'medium', or 'low'")

    # Validate tags
    if tags is not None:
        if len(tags) > 10:
            raise ValidationError("tags cannot exceed 10 items")
        tags = [t.strip() for t in tags if t.strip()]

    # Validate recurrence_pattern
    if recurrence_pattern is not None:
        recurrence_pattern = recurrence_pattern.strip().lower()
        if recurrence_pattern not in ("daily", "weekly", "monthly"):
            raise ValidationError("recurrence_pattern must be 'daily', 'weekly', or 'monthly'")

    # Parse dates
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            raise ValidationError(f"Invalid due_date format: {due_date}")

    parsed_reminder_time = None
    if reminder_time:
        try:
            parsed_reminder_time = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))
        except ValueError:
            raise ValidationError(f"Invalid reminder_time format: {reminder_time}")

    parsed_recurrence_end = None
    if recurrence_end_date:
        try:
            parsed_recurrence_end = datetime.fromisoformat(recurrence_end_date.replace("Z", "+00:00"))
        except ValueError:
            raise ValidationError(f"Invalid recurrence_end_date format: {recurrence_end_date}")

    task = Task(
        user_id=user_id.strip(),
        title=title.strip(),
        description=description.strip() if description else None,
        priority=priority,
        tags=tags if tags else None,
        due_date=parsed_due_date,
        reminder_time=parsed_reminder_time,
        recurrence_pattern=recurrence_pattern,
        recurrence_end_date=parsed_recurrence_end,
    )

    with _get_session() as session:
        session.add(task)
        session.commit()
        session.refresh(task)

        task_data = {
            "id": str(task.id),
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "category": task.category,
            "tags": task.tags,
            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
            "recurrence_pattern": task.recurrence_pattern,
            "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Create event for publishing
        event = TaskEvent(
            event_type=TaskEventType.TASK_CREATED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        )

        # Publish real-time SSE event
        task_event_manager.publish_sync(event)

        # Publish to Dapr Pub/Sub (task-events and task-updates topics)
        publish_task_event_sync(event)
        publish_task_update_sync(event)

        return task_data


def list_tasks(user_id: str) -> list[dict]:
    """
    Get all tasks for a user.

    Args:
        user_id: Owner's user identifier (required)

    Returns:
        list of task dicts, empty list if no tasks

    Raises:
        ValidationError: If user_id is missing or invalid
    """
    _validate_user_id(user_id)

    with _get_session() as session:
        statement = select(Task).where(Task.user_id == user_id.strip())
        tasks = session.exec(statement).all()

        return [
            {
                "id": str(task.id),
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority,
                "category": task.category,
                "tags": task.tags,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "recurrence_pattern": task.recurrence_pattern,
                "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]


def search_tasks(
    user_id: str,
    query: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> list[dict]:
    """
    Search, filter, and sort tasks for a user.

    T077-T082: Text search, filter by status/priority/tags, sort by various fields.

    Args:
        user_id: Owner's user identifier (required)
        query: Text search in title/description (optional)
        status: Filter by status - 'pending' or 'completed' (optional)
        priority: Filter by priority - 'high', 'medium', 'low' (optional)
        tags: Filter by tags - tasks must have at least one matching tag (optional)
        sort_by: Sort field - 'due_date', 'priority', 'created_at', 'updated_at', 'title' (optional)
        sort_order: Sort direction - 'asc' or 'desc' (optional, default 'asc')

    Returns:
        list of matching task dicts
    """
    _validate_user_id(user_id)

    with _get_session() as session:
        statement = select(Task).where(Task.user_id == user_id.strip())

        # T077: Text search on title/description
        if query:
            search_term = f"%{query.strip()}%"
            statement = statement.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        # T078: Filter by status
        if status:
            if status.lower() == "completed":
                statement = statement.where(Task.completed == True)
            elif status.lower() == "pending":
                statement = statement.where(Task.completed == False)

        # Filter by priority
        if priority:
            statement = statement.where(Task.priority == priority.lower())

        # Sorting
        order = sort_order.lower() if sort_order else "asc"

        if sort_by:
            sort_field = sort_by.lower()
            if sort_field == "due_date":
                col = Task.due_date
            elif sort_field == "priority":
                col = Task.priority
            elif sort_field == "created_at":
                col = Task.created_at
            elif sort_field == "updated_at":
                col = Task.updated_at
            elif sort_field == "title":
                col = Task.title
            else:
                col = Task.created_at

            if order == "desc":
                statement = statement.order_by(col.desc())
            else:
                statement = statement.order_by(col.asc())

        tasks = session.exec(statement).all()

        # Post-query tag filtering (ARRAY overlap not supported in all SQLModel versions)
        if tags:
            tag_set = set(t.lower() for t in tags)
            tasks = [
                t for t in tasks
                if t.tags and tag_set.intersection(tag.lower() for tag in t.tags)
            ]

        return [
            {
                "id": str(task.id),
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority,
                "category": task.category,
                "tags": task.tags,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "recurrence_pattern": task.recurrence_pattern,
                "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]


def complete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: Owner's user identifier (required)
        task_id: Task identifier (required)

    Returns:
        dict with updated task details

    Raises:
        ValidationError: If parameters are missing or invalid
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
    """
    _validate_user_id(user_id)
    task_uuid = _validate_task_id(task_id)

    with _get_session() as session:
        task = _get_user_task(session, user_id.strip(), task_uuid)
        task.completed = True
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        task_data = {
            "id": str(task.id),
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "category": task.category,
            "tags": task.tags,
            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
            "recurrence_pattern": task.recurrence_pattern,
            "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Create event for publishing
        event = TaskEvent(
            event_type=TaskEventType.TASK_COMPLETED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        )

        # Publish real-time SSE event
        task_event_manager.publish_sync(event)

        # Publish to Dapr Pub/Sub (task-events and task-updates topics)
        publish_task_event_sync(event)
        publish_task_update_sync(event)

        return task_data


def uncomplete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as not completed (pending).

    Args:
        user_id: Owner's user identifier (required)
        task_id: Task identifier (required)

    Returns:
        dict with updated task details

    Raises:
        ValidationError: If parameters are missing or invalid
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
    """
    _validate_user_id(user_id)
    task_uuid = _validate_task_id(task_id)

    with _get_session() as session:
        task = _get_user_task(session, user_id.strip(), task_uuid)
        task.completed = False
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        task_data = {
            "id": str(task.id),
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "category": task.category,
            "tags": task.tags,
            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
            "recurrence_pattern": task.recurrence_pattern,
            "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Create event for publishing
        event = TaskEvent(
            event_type=TaskEventType.TASK_UNCOMPLETED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        )

        # Publish real-time SSE event
        task_event_manager.publish_sync(event)

        # Publish to Dapr Pub/Sub (task-events and task-updates topics)
        publish_task_event_sync(event)
        publish_task_update_sync(event)

        return task_data


def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    recurrence_pattern: Optional[str] = None,
    recurrence_end_date: Optional[str] = None,
) -> dict:
    """
    Update task details. Only provided fields are updated.

    Args:
        user_id: Owner's user identifier (required)
        task_id: Task identifier (required)
        title: New title (optional)
        description: New description (optional)
        priority: Priority level - high, medium, low, or None to clear (optional)
        tags: List of tags, max 10 items, or empty list to clear (optional)
        due_date: Due date in ISO8601 format, or empty string to clear (optional)
        reminder_time: Reminder time in ISO8601 format, or empty string to clear (optional)
        recurrence_pattern: Recurrence - daily, weekly, monthly, or empty to clear (optional)
        recurrence_end_date: End date for recurrence in ISO8601, or empty to clear (optional)

    Returns:
        dict with updated task details

    Raises:
        ValidationError: If required parameters are missing or invalid
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
    """
    _validate_user_id(user_id)
    task_uuid = _validate_task_id(task_id)

    with _get_session() as session:
        task = _get_user_task(session, user_id.strip(), task_uuid)

        if title is not None:
            if not title.strip():
                raise ValidationError("title cannot be empty if provided")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip() if description else None

        # Handle priority update
        if priority is not None:
            if priority == "":
                task.priority = None
            else:
                priority = priority.strip().lower()
                if priority not in ("high", "medium", "low"):
                    raise ValidationError("priority must be 'high', 'medium', or 'low'")
                task.priority = priority

        # Handle tags update
        if tags is not None:
            if len(tags) == 0:
                task.tags = None
            else:
                if len(tags) > 10:
                    raise ValidationError("tags cannot exceed 10 items")
                task.tags = [t.strip() for t in tags if t.strip()]

        # Handle due_date update
        if due_date is not None:
            if due_date == "":
                task.due_date = None
            else:
                try:
                    task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except ValueError:
                    raise ValidationError(f"Invalid due_date format: {due_date}")

        # Handle reminder_time update
        if reminder_time is not None:
            if reminder_time == "":
                task.reminder_time = None
            else:
                try:
                    task.reminder_time = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))
                except ValueError:
                    raise ValidationError(f"Invalid reminder_time format: {reminder_time}")

        # Handle recurrence_pattern update
        if recurrence_pattern is not None:
            if recurrence_pattern == "":
                task.recurrence_pattern = None
            else:
                recurrence_pattern = recurrence_pattern.strip().lower()
                if recurrence_pattern not in ("daily", "weekly", "monthly"):
                    raise ValidationError("recurrence_pattern must be 'daily', 'weekly', or 'monthly'")
                task.recurrence_pattern = recurrence_pattern

        # Handle recurrence_end_date update
        if recurrence_end_date is not None:
            if recurrence_end_date == "":
                task.recurrence_end_date = None
            else:
                try:
                    task.recurrence_end_date = datetime.fromisoformat(recurrence_end_date.replace("Z", "+00:00"))
                except ValueError:
                    raise ValidationError(f"Invalid recurrence_end_date format: {recurrence_end_date}")

        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        task_data = {
            "id": str(task.id),
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "category": task.category,
            "tags": task.tags,
            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
            "recurrence_pattern": task.recurrence_pattern,
            "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Create event for publishing
        event = TaskEvent(
            event_type=TaskEventType.TASK_UPDATED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        )

        # Publish real-time SSE event
        task_event_manager.publish_sync(event)

        # Publish to Dapr Pub/Sub (task-events and task-updates topics)
        publish_task_event_sync(event)
        publish_task_update_sync(event)

        return task_data


def delete_task(user_id: str, task_id: str) -> dict:
    """
    Permanently delete a task.

    Args:
        user_id: Owner's user identifier (required)
        task_id: Task identifier (required)

    Returns:
        dict confirming deletion with task_id

    Raises:
        ValidationError: If parameters are missing or invalid
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
    """
    _validate_user_id(user_id)
    task_uuid = _validate_task_id(task_id)

    with _get_session() as session:
        task = _get_user_task(session, user_id.strip(), task_uuid)
        task_user_id = task.user_id  # Save before delete
        session.delete(task)
        session.commit()

        # Create event for publishing
        event = TaskEvent(
            event_type=TaskEventType.TASK_DELETED,
            user_id=task_user_id,
            task_id=str(task_uuid),
            task_data=None,
        )

        # Publish real-time SSE event
        task_event_manager.publish_sync(event)

        # Publish to Dapr Pub/Sub (task-events and task-updates topics)
        publish_task_event_sync(event)
        publish_task_update_sync(event)

        return {
            "deleted": True,
            "task_id": str(task_uuid),
        }
