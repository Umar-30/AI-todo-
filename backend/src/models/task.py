"""
Task model for Todo AI Chatbot.

Represents a todo item belonging to a user.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

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
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date for the task (optional)",
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
