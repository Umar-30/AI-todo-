"""
Events module for real-time task updates and Dapr Pub/Sub integration.
"""
from .task_events import (
    task_event_manager,
    TaskEvent,
    TaskEventType,
    publish_task_event_sync,
    publish_task_update_sync,
    publish_task_event_to_dapr,
    publish_task_update_to_dapr,
)
from .event_schemas import (
    TaskEventType as TaskEventTypeSchema,
    ReminderEventType,
    SyncEventType,
    ChangeType,
    TaskEvent as TaskEventSchema,
    ReminderEvent,
    TaskUpdateEvent,
)

__all__ = [
    # Task event manager and types
    "task_event_manager",
    "TaskEvent",
    "TaskEventType",
    # Dapr publishing functions
    "publish_task_event_sync",
    "publish_task_update_sync",
    "publish_task_event_to_dapr",
    "publish_task_update_to_dapr",
    # Event schemas (CloudEvents)
    "TaskEventTypeSchema",
    "ReminderEventType",
    "SyncEventType",
    "ChangeType",
    "TaskEventSchema",
    "ReminderEvent",
    "TaskUpdateEvent",
]
