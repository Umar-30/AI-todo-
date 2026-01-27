"""
Conversation service for database operations.

Provides stateless database operations for conversations and messages.
All state is loaded fresh from the database per request.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from ..database import get_engine
from ..models.conversation import Conversation
from ..models.message import Message


class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found."""
    pass


class ConversationAccessDeniedError(Exception):
    """Raised when user doesn't own the conversation."""
    pass


def _get_session() -> Session:
    """Get a new database session."""
    return Session(get_engine())


def get_conversation_with_messages(
    conversation_id: UUID,
    user_id: str
) -> tuple[Conversation, list[Message]]:
    """
    Load a conversation with all its messages from the database.

    Args:
        conversation_id: The conversation's unique identifier
        user_id: The user's unique identifier for ownership validation

    Returns:
        Tuple of (Conversation, list of Messages ordered by created_at)

    Raises:
        ConversationNotFoundError: If conversation doesn't exist
        ConversationAccessDeniedError: If user doesn't own the conversation
    """
    with _get_session() as session:
        # Load conversation
        statement = select(Conversation).where(Conversation.id == conversation_id)
        conversation = session.exec(statement).first()

        if not conversation:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found"
            )

        # Validate ownership
        if conversation.user_id != user_id:
            raise ConversationAccessDeniedError(
                f"Access denied to conversation {conversation_id}"
            )

        # Load messages ordered by created_at
        msg_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = list(session.exec(msg_statement).all())

        return conversation, messages


def create_conversation(user_id: str) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        user_id: The user's unique identifier

    Returns:
        Newly created Conversation with generated ID
    """
    conversation = Conversation(user_id=user_id)

    with _get_session() as session:
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation


def create_message(
    user_id: str,
    conversation_id: UUID,
    role: str,
    content: str
) -> Message:
    """
    Create a new message in a conversation.

    Also updates the conversation's updated_at timestamp.

    Args:
        user_id: The user's unique identifier
        conversation_id: The parent conversation's ID
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Newly created Message
    """
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    with _get_session() as session:
        # Add the message
        session.add(message)

        # Update conversation timestamp
        statement = select(Conversation).where(Conversation.id == conversation_id)
        conversation = session.exec(statement).first()
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)

        session.commit()
        session.refresh(message)

        return message


def get_conversation(conversation_id: UUID) -> Optional[Conversation]:
    """
    Get a conversation by ID without messages.

    Args:
        conversation_id: The conversation's unique identifier

    Returns:
        Conversation if found, None otherwise
    """
    with _get_session() as session:
        statement = select(Conversation).where(Conversation.id == conversation_id)
        return session.exec(statement).first()
