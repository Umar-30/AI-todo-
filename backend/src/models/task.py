"""
Task model for Todo AI Chatbot.

Represents a todo item belonging to a user.
Enhanced with recurring tasks, tags, and reminder support (Phase V).
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ARRAY, String
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task entity representing a todo item.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner's user identifier (required, indexed)
        title: Task title (required, max 255 chars)
        description: Detailed task description (optional)
        completed: Completion status (default: False)
        priority: Priority level - high, medium, low (optional)
        category: User-defined category (optional)
        tags: Array of user-defined tags (T014)
        due_date: Task deadline (optional)
        reminder_time: When to send reminder (T015)
        recurrence_pattern: daily, weekly, monthly (T016)
        recurrence_end_date: When recurrence stops (T017)
        parent_task_id: Links recurring instances (T018)
        created_at: Creation timestamp (auto-set, UTC)
        updated_at: Last modification timestamp (auto-update, UTC)
    """
    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier",
    )
    user_id: str = Field(
        index=True,
        description="Owner's user identifier",
    )
    title: str = Field(
        max_length=255,
        description="Task title",
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed task description",
    )
    completed: bool = Field(
        default=False,
        description="Completion status",
    )
    priority: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Priority level: high, medium, low (optional)",
    )
    category: Optional[str] = Field(
        default=None,
        max_length=50,
        description="User-defined category (optional)",
    )
    # T014: Tags field (array of strings)
    tags: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(String), nullable=True),
        description="Array of user-defined tags (max 10 items)",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date for the task (optional)",
    )
    # T015: Reminder time field
    reminder_time: Optional[datetime] = Field(
        default=None,
        description="When to send reminder (UTC, optional)",
    )
    # T016: Recurrence pattern field
    recurrence_pattern: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Recurrence pattern: daily, weekly, monthly (optional)",
    )
    # T017: Recurrence end date field
    recurrence_end_date: Optional[datetime] = Field(
        default=None,
        description="When recurrence stops (UTC, optional)",
    )
    # T018: Parent task ID for recurring instances
    parent_task_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tasks.id",
        description="Links recurring task instances to original task",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        description="Last modification timestamp (UTC)",
    )
