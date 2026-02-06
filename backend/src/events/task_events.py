"""
Task event manager for real-time updates.

Implements a simple pub/sub pattern for broadcasting task changes
to connected SSE clients, with Dapr Pub/Sub integration (Phase V).

T025: Add correlation ID generation for event tracing
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Dict, Optional, Set
from datetime import datetime, timezone
from uuid import uuid4

logger = logging.getLogger(__name__)


class TaskEventType(str, Enum):
    """Types of task events."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_UNCOMPLETED = "task.uncompleted"
    TASK_DELETED = "task.deleted"


def generate_correlation_id() -> str:
    """T025: Generate a unique correlation ID for distributed tracing."""
    return str(uuid4())


@dataclass
class TaskEvent:
    """Represents a task event."""
    event_type: TaskEventType
    user_id: str
    task_id: str
    task_data: dict | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: Optional[str] = field(default_factory=generate_correlation_id)

    def to_sse(self) -> str:
        """Convert event to SSE format."""
        data = {
            "type": self.event_type.value,
            "task_id": self.task_id,
            "task": self.task_data,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
        }
        return f"event: {self.event_type.value}\ndata: {json.dumps(data)}\n\n"

    def to_cloudevent(self) -> dict:
        """Convert to CloudEvents format for Dapr Pub/Sub."""
        return {
            "specversion": "1.0",
            "type": self.event_type.value,
            "source": "todo-backend",
            "id": str(uuid4()),
            "time": self.timestamp,
            "datacontenttype": "application/json",
            "subject": f"task:{self.task_id}",
            "correlationid": self.correlation_id,
            "data": {
                "taskId": self.task_id,
                "userId": self.user_id,
                **(self.task_data or {}),
            },
        }


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


# Dapr Pub/Sub integration functions (T021-T024, T026)
async def publish_task_event_to_dapr(event: TaskEvent) -> bool:
    """
    Publish a task event to Dapr Pub/Sub (task-events topic).

    T021-T024: Publish task lifecycle events via Dapr.
    """
    try:
        from ..services.dapr_client import publish_event, TOPIC_TASK_EVENTS

        cloudevent = event.to_cloudevent()
        return await publish_event(
            topic=TOPIC_TASK_EVENTS,
            data=cloudevent,
            correlation_id=event.correlation_id,
        )
    except ImportError:
        logger.warning("Dapr client not available, skipping Pub/Sub publish")
        return False
    except Exception as e:
        logger.error(f"Failed to publish event to Dapr: {e}")
        return False


async def publish_task_update_to_dapr(event: TaskEvent) -> bool:
    """
    Publish a task update event to Dapr Pub/Sub (task-updates topic).

    T026: Dual-publish to task-updates topic for realtime sync.
    This event contains the full task object for client sync.
    """
    try:
        from ..services.dapr_client import publish_event, TOPIC_TASK_UPDATES
        from .event_schemas import ChangeType

        # Map event type to change type
        change_type_map = {
            TaskEventType.TASK_CREATED: ChangeType.CREATED,
            TaskEventType.TASK_UPDATED: ChangeType.UPDATED,
            TaskEventType.TASK_COMPLETED: ChangeType.COMPLETED,
            TaskEventType.TASK_UNCOMPLETED: ChangeType.UPDATED,
            TaskEventType.TASK_DELETED: ChangeType.DELETED,
        }

        change_type = change_type_map.get(event.event_type, ChangeType.UPDATED)

        sync_event = {
            "specversion": "1.0",
            "type": "sync.task_changed",
            "source": "todo-backend",
            "id": str(uuid4()),
            "time": event.timestamp,
            "datacontenttype": "application/json",
            "subject": f"task:{event.task_id}",
            "correlationid": event.correlation_id,
            "data": {
                "taskId": event.task_id,
                "userId": event.user_id,
                "changeType": change_type.value,
                "task": event.task_data,
            },
        }

        return await publish_event(
            topic=TOPIC_TASK_UPDATES,
            data=sync_event,
            correlation_id=event.correlation_id,
        )
    except ImportError:
        logger.warning("Dapr client not available, skipping task-updates publish")
        return False
    except Exception as e:
        logger.error(f"Failed to publish task update to Dapr: {e}")
        return False


def publish_task_event_sync(event: TaskEvent) -> bool:
    """
    Synchronous wrapper for publishing task events to Dapr.
    Falls back gracefully if Dapr is not available.
    """
    try:
        from ..services.dapr_client import publish_event_sync, TOPIC_TASK_EVENTS

        cloudevent = event.to_cloudevent()
        return publish_event_sync(
            topic=TOPIC_TASK_EVENTS,
            data=cloudevent,
            correlation_id=event.correlation_id,
        )
    except ImportError:
        logger.debug("Dapr client not available (sync)")
        return False
    except Exception as e:
        logger.warning(f"Failed to publish event to Dapr (sync): {e}")
        return False


def publish_task_update_sync(event: TaskEvent) -> bool:
    """
    Synchronous wrapper for publishing task updates to Dapr.
    """
    try:
        from ..services.dapr_client import publish_event_sync, TOPIC_TASK_UPDATES
        from .event_schemas import ChangeType

        change_type_map = {
            TaskEventType.TASK_CREATED: ChangeType.CREATED,
            TaskEventType.TASK_UPDATED: ChangeType.UPDATED,
            TaskEventType.TASK_COMPLETED: ChangeType.COMPLETED,
            TaskEventType.TASK_UNCOMPLETED: ChangeType.UPDATED,
            TaskEventType.TASK_DELETED: ChangeType.DELETED,
        }

        change_type = change_type_map.get(event.event_type, ChangeType.UPDATED)

        sync_event = {
            "specversion": "1.0",
            "type": "sync.task_changed",
            "source": "todo-backend",
            "id": str(uuid4()),
            "time": event.timestamp,
            "datacontenttype": "application/json",
            "subject": f"task:{event.task_id}",
            "correlationid": event.correlation_id,
            "data": {
                "taskId": event.task_id,
                "userId": event.user_id,
                "changeType": change_type.value,
                "task": event.task_data,
            },
        }

        return publish_event_sync(
            topic=TOPIC_TASK_UPDATES,
            data=sync_event,
            correlation_id=event.correlation_id,
        )
    except ImportError:
        logger.debug("Dapr client not available for task-updates (sync)")
        return False
    except Exception as e:
        logger.warning(f"Failed to publish task update to Dapr (sync): {e}")
        return False
