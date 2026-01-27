"""
Task event manager for real-time updates.

Implements a simple pub/sub pattern for broadcasting task changes
to connected SSE clients.
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Dict, Set
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TaskEventType(str, Enum):
    """Types of task events."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_UNCOMPLETED = "task.uncompleted"
    TASK_DELETED = "task.deleted"


@dataclass
class TaskEvent:
    """Represents a task event."""
    event_type: TaskEventType
    user_id: str
    task_id: str
    task_data: dict | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_sse(self) -> str:
        """Convert event to SSE format."""
        data = {
            "type": self.event_type.value,
            "task_id": self.task_id,
            "task": self.task_data,
            "timestamp": self.timestamp,
        }
        return f"event: {self.event_type.value}\ndata: {json.dumps(data)}\n\n"


class TaskEventManager:
    """
    Manages task event subscriptions and broadcasting.

    Allows multiple SSE clients to subscribe to task updates for a specific user.
    Events are broadcast to all subscribers when tasks change.
    """

    def __init__(self):
        # Map user_id -> set of asyncio.Queue instances
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: str) -> AsyncGenerator[str, None]:
        """
        Subscribe to task events for a user.

        Yields SSE-formatted event strings when tasks change.
        """
        queue: asyncio.Queue = asyncio.Queue()

        async with self._lock:
            if user_id not in self._subscribers:
                self._subscribers[user_id] = set()
            self._subscribers[user_id].add(queue)

        logger.info(f"Client subscribed to task events for user {user_id}")

        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'user_id': user_id})}\n\n"

            while True:
                try:
                    # Wait for events with timeout to send keepalive
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event
                except asyncio.TimeoutError:
                    # Send keepalive comment to maintain connection
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            logger.info(f"Client unsubscribed from task events for user {user_id}")
            raise
        finally:
            async with self._lock:
                if user_id in self._subscribers:
                    self._subscribers[user_id].discard(queue)
                    if not self._subscribers[user_id]:
                        del self._subscribers[user_id]

    async def publish(self, event: TaskEvent) -> None:
        """
        Publish a task event to all subscribers for the user.
        """
        async with self._lock:
            subscribers = self._subscribers.get(event.user_id, set()).copy()

        if not subscribers:
            logger.debug(f"No subscribers for user {event.user_id}")
            return

        sse_data = event.to_sse()
        logger.info(f"Publishing {event.event_type.value} to {len(subscribers)} subscribers")

        for queue in subscribers:
            try:
                await queue.put(sse_data)
            except Exception as e:
                logger.error(f"Error publishing event: {e}")

    def publish_sync(self, event: TaskEvent) -> None:
        """
        Synchronous wrapper for publishing events.

        Uses a simple approach: directly put event data into subscriber queues.
        This avoids async/await complexity in sync context.
        """
        # Get subscribers without async lock (read-only snapshot)
        subscribers = self._subscribers.get(event.user_id, set()).copy()

        if not subscribers:
            logger.debug(f"No subscribers for user {event.user_id}")
            return

        sse_data = event.to_sse()
        logger.info(f"Publishing {event.event_type.value} to {len(subscribers)} subscribers (sync)")

        for queue in subscribers:
            try:
                # put_nowait is thread-safe for asyncio.Queue
                queue.put_nowait(sse_data)
            except Exception as e:
                logger.error(f"Error publishing event: {e}")


# Global event manager instance
task_event_manager = TaskEventManager()
