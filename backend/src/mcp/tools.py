"""
MCP tools for task operations.

Provides stateless task management operations that read/write directly to the database.
All operations require a user_id for data isolation.
Publishes real-time events when tasks change.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from ..database import get_engine
from ..models.task import Task
from ..events import task_event_manager, TaskEvent, TaskEventType


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


def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: Owner's user identifier (required)
        title: Task title (required)
        description: Task description (optional)

    Returns:
        dict with created task details

    Raises:
        ValidationError: If required parameters are missing or invalid
    """
    _validate_user_id(user_id)

    if not title or not title.strip():
        raise ValidationError("title is required and cannot be empty")

    task = Task(
        user_id=user_id.strip(),
        title=title.strip(),
        description=description.strip() if description else None,
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
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Publish real-time event
        task_event_manager.publish_sync(TaskEvent(
            event_type=TaskEventType.TASK_CREATED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        ))

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
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Publish real-time event
        task_event_manager.publish_sync(TaskEvent(
            event_type=TaskEventType.TASK_COMPLETED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        ))

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
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Publish real-time event
        task_event_manager.publish_sync(TaskEvent(
            event_type=TaskEventType.TASK_UNCOMPLETED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        ))

        return task_data


def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Update task details. Only provided fields are updated.

    Args:
        user_id: Owner's user identifier (required)
        task_id: Task identifier (required)
        title: New title (optional)
        description: New description (optional)

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
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Publish real-time event
        task_event_manager.publish_sync(TaskEvent(
            event_type=TaskEventType.TASK_UPDATED,
            user_id=task.user_id,
            task_id=str(task.id),
            task_data=task_data,
        ))

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

        # Publish real-time event
        task_event_manager.publish_sync(TaskEvent(
            event_type=TaskEventType.TASK_DELETED,
            user_id=task_user_id,
            task_id=str(task_uuid),
            task_data=None,
        ))

        return {
            "deleted": True,
            "task_id": str(task_uuid),
        }
