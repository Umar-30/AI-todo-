"""
ChatKit Store implementation using existing SQLModel models.

Maps ChatKit thread/message concepts to our Conversation/Message entities.
"""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from ..database import get_engine
from ..models import Conversation, Message


class ChatKitStore:
    """
    ChatKit store implementation that persists threads and messages
    to the database using existing SQLModel models.

    ChatKit concepts mapping:
    - Thread → Conversation
    - Message → Message
    """

    def __init__(self, user_id: str = "demo-user"):
        """
        Initialize the ChatKit store.

        Args:
            user_id: Default user ID for operations (auth out of scope)
        """
        self.user_id = user_id

    def get_thread(self, thread_id: str) -> dict[str, Any] | None:
        """
        Get a thread (conversation) by ID.

        Args:
            thread_id: The thread/conversation UUID

        Returns:
            Thread data dict or None if not found
        """
        try:
            uuid_id = UUID(thread_id)
        except ValueError:
            return None

        engine = get_engine()
        with Session(engine) as session:
            conversation = session.get(Conversation, uuid_id)
            if not conversation:
                return None

            return {
                "id": str(conversation.id),
                "user_id": conversation.user_id,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
            }

    def create_thread(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Create a new thread (conversation).

        Args:
            user_id: Optional user ID override

        Returns:
            Created thread data dict
        """
        engine = get_engine()
        with Session(engine) as session:
            conversation = Conversation(
                user_id=user_id or self.user_id,
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

            return {
                "id": str(conversation.id),
                "user_id": conversation.user_id,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
            }

    def get_messages(self, thread_id: str) -> list[dict[str, Any]]:
        """
        Get all messages for a thread in chronological order.

        Args:
            thread_id: The thread/conversation UUID

        Returns:
            List of message data dicts
        """
        try:
            uuid_id = UUID(thread_id)
        except ValueError:
            return []

        engine = get_engine()
        with Session(engine) as session:
            statement = (
                select(Message)
                .where(Message.conversation_id == uuid_id)
                .order_by(Message.created_at)
            )
            messages = session.exec(statement).all()

            return [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ]

    def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Add a message to a thread.

        Args:
            thread_id: The thread/conversation UUID
            role: Message role ("user" or "assistant")
            content: Message content

        Returns:
            Created message data dict
        """
        uuid_id = UUID(thread_id)

        engine = get_engine()
        with Session(engine) as session:
            # Create the message
            message = Message(
                conversation_id=uuid_id,
                user_id=self.user_id,
                role=role,
                content=content,
            )
            session.add(message)

            # Update conversation's updated_at
            conversation = session.get(Conversation, uuid_id)
            if conversation:
                conversation.updated_at = datetime.now(timezone.utc)
                session.add(conversation)

            session.commit()
            session.refresh(message)

            return {
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }

    def thread_exists(self, thread_id: str) -> bool:
        """
        Check if a thread exists.

        Args:
            thread_id: The thread/conversation UUID

        Returns:
            True if thread exists, False otherwise
        """
        return self.get_thread(thread_id) is not None

    def validate_thread_ownership(self, thread_id: str, user_id: str) -> bool:
        """
        Validate that a thread belongs to a user.

        Args:
            thread_id: The thread/conversation UUID
            user_id: User ID to check ownership

        Returns:
            True if user owns the thread, False otherwise
        """
        thread = self.get_thread(thread_id)
        if not thread:
            return False
        return thread["user_id"] == user_id
