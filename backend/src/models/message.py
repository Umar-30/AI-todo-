"""
Message model for Todo AI Chatbot.

Represents a single message within a conversation.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message entity representing a single message in a conversation.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner's user identifier (required)
        conversation_id: Parent conversation (foreign key, required)
        role: Sender type - "user" or "assistant" (required)
        content: Message content (required)
        created_at: Creation timestamp (auto-set, UTC)
        conversation: Parent Conversation entity (relationship)
    """
    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier",
    )
    user_id: str = Field(
        description="Owner's user identifier",
    )
    conversation_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Parent conversation identifier",
    )
    role: str = Field(
        description="Sender type: 'user' or 'assistant'",
    )
    content: str = Field(
        description="Message content",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp (UTC)",
    )

    # Relationship to Conversation (many-to-one)
    conversation: Optional["Conversation"] = Relationship(
        back_populates="messages",
    )
