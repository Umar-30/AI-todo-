"""
Pydantic Event Schemas for CloudEvents-compliant messaging.

T010-T013: Define event schemas as Pydantic models
These schemas follow the CloudEvents specification for interoperability.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Event Types
class TaskEventType(str, Enum):
    """Task lifecycle event types."""
    CREATED = "task.created"
    UPDATED = "task.updated"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"


class ReminderEventType(str, Enum):
    """Reminder lifecycle event types."""
    SCHEDULED = "reminder.scheduled"
    TRIGGERED = "reminder.triggered"
    CANCELLED = "reminder.cancelled"


class SyncEventType(str, Enum):
    """Real-time sync event types."""
    TASK_CHANGED = "sync.task_changed"


class ChangeType(str, Enum):
    """Types of changes for sync events."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMPLETED = "completed"


# CloudEvents Envelope (T010)
class CloudEventBase(BaseModel):
    """Base CloudEvents envelope following spec v1.0."""
    specversion: str = Field(default="1.0", description="CloudEvents spec version")
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event ID")
    source: str = Field(description="Event source identifier")
    type: str = Field(description="Event type")
    time: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Event timestamp (ISO8601)"
    )
    datacontenttype: str = Field(default="application/json")
    subject: Optional[str] = Field(default=None, description="Subject identifier")
    correlationid: Optional[str] = Field(default=None, description="Correlation ID for tracing")


# Task Event Data Payloads
class RecurrenceData(BaseModel):
    """Recurrence pattern for tasks."""
    pattern: Optional[str] = Field(None, description="daily | weekly | monthly")
    endDate: Optional[str] = Field(None, description="End date for recurrence (ISO8601)")
    nextOccurrence: Optional[str] = Field(None, description="Calculated next occurrence")


class TaskEventData(BaseModel):
    """Payload for task lifecycle events."""
    taskId: str = Field(description="Task UUID")
    userId: str = Field(description="User ID who owns the task")
    title: Optional[str] = Field(None, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[str] = Field(None, description="high | medium | low")
    status: Optional[str] = Field(None, description="pending | completed")
    tags: Optional[List[str]] = Field(default_factory=list, description="Task tags")
    dueDate: Optional[str] = Field(None, description="Due date (ISO8601)")
    reminderTime: Optional[str] = Field(None, description="Reminder time (ISO8601)")
    recurrence: Optional[RecurrenceData] = Field(None, description="Recurrence pattern")
    previousValues: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Changed fields before update (for task.updated events)"
    )


# Task Event (T011)
class TaskEvent(CloudEventBase):
    """
    CloudEvents-compliant task lifecycle event.

    Published to 'task-events' topic for:
    - task.created: New task created
    - task.updated: Task fields modified
    - task.completed: Task marked complete
    - task.deleted: Task deleted
    """
    source: str = Field(default="todo-backend")
    type: TaskEventType
    data: TaskEventData

    @classmethod
    def create(
        cls,
        event_type: TaskEventType,
        task_id: str,
        user_id: str,
        correlation_id: Optional[str] = None,
        **task_data,
    ) -> "TaskEvent":
        """Factory method to create a TaskEvent."""
        return cls(
            type=event_type,
            subject=f"task:{task_id}",
            correlationid=correlation_id,
            data=TaskEventData(
                taskId=task_id,
                userId=user_id,
                **task_data,
            ),
        )


# Reminder Event Data Payloads
class ReminderEventData(BaseModel):
    """Payload for reminder lifecycle events."""
    taskId: str = Field(description="Associated task UUID")
    userId: str = Field(description="User ID to notify")
    taskTitle: str = Field(description="Task title for notification")
    reminderTime: str = Field(description="Scheduled reminder time (ISO8601)")
    reminderType: str = Field(default="before_due", description="before_due | custom")


# Reminder Event (T012)
class ReminderEvent(CloudEventBase):
    """
    CloudEvents-compliant reminder lifecycle event.

    Published to 'reminders' topic for:
    - reminder.scheduled: Reminder created
    - reminder.triggered: Reminder fired
    - reminder.cancelled: Reminder cancelled
    """
    source: str = Field(default="reminder-service")
    type: ReminderEventType
    data: ReminderEventData

    @classmethod
    def create(
        cls,
        event_type: ReminderEventType,
        task_id: str,
        user_id: str,
        task_title: str,
        reminder_time: str,
        correlation_id: Optional[str] = None,
    ) -> "ReminderEvent":
        """Factory method to create a ReminderEvent."""
        return cls(
            type=event_type,
            subject=f"reminder:{task_id}",
            correlationid=correlation_id,
            data=ReminderEventData(
                taskId=task_id,
                userId=user_id,
                taskTitle=task_title,
                reminderTime=reminder_time,
            ),
        )


# Task Update Event Data Payload (for real-time sync)
class TaskObject(BaseModel):
    """Full task object for sync events."""
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    dueDate: Optional[str] = None
    reminderTime: Optional[str] = None
    recurrencePattern: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class TaskUpdateEventData(BaseModel):
    """Payload for real-time sync events."""
    taskId: str = Field(description="Task UUID")
    userId: str = Field(description="User ID for routing")
    changeType: ChangeType = Field(description="Type of change")
    task: Optional[TaskObject] = Field(None, description="Full task object (for create/update)")


# Task Update Event (T013)
class TaskUpdateEvent(CloudEventBase):
    """
    CloudEvents-compliant real-time sync event.

    Published to 'task-updates' topic for pushing changes
    to connected WebSocket clients.
    """
    source: str = Field(default="todo-backend")
    type: SyncEventType = Field(default=SyncEventType.TASK_CHANGED)
    data: TaskUpdateEventData

    @classmethod
    def create(
        cls,
        change_type: ChangeType,
        task_id: str,
        user_id: str,
        task: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> "TaskUpdateEvent":
        """Factory method to create a TaskUpdateEvent."""
        task_obj = None
        if task:
            task_obj = TaskObject(
                id=task.get("id", task_id),
                title=task.get("title", ""),
                description=task.get("description"),
                completed=task.get("completed", False),
                priority=task.get("priority"),
                tags=task.get("tags"),
                dueDate=task.get("due_date") or task.get("dueDate"),
                reminderTime=task.get("reminder_time") or task.get("reminderTime"),
                recurrencePattern=task.get("recurrence_pattern") or task.get("recurrencePattern"),
                createdAt=task.get("created_at") or task.get("createdAt"),
                updatedAt=task.get("updated_at") or task.get("updatedAt"),
            )

        return cls(
            subject=f"task:{task_id}",
            correlationid=correlation_id,
            data=TaskUpdateEventData(
                taskId=task_id,
                userId=user_id,
                changeType=change_type,
                task=task_obj,
            ),
        )
