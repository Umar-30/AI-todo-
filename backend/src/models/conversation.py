"""
Conversation model for Todo AI Chatbot.

Represents a chat session belonging to a user.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner's user identifier (required, indexed)
        created_at: Creation timestamp (auto-set, UTC)
        updated_at: Last modification timestamp (auto-update, UTC)
        messages: Related Message entities (one-to-many)
    """
    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier",
    )
    user_id: str = Field(
        index=True,
        description="Owner's user identifier",
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

    # Relationship to Message (one-to-many)
    # Cascade delete configured: deleting conversation deletes all messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
