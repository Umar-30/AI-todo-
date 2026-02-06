"""
Audit Record model for Task Event Logging.

T020: Create AuditRecord model
Immutable audit log entries for all task events.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AuditRecord(SQLModel, table=True):
    """
    Immutable audit log entry for task events.

    This table is append-only - no UPDATE or DELETE operations allowed.
    All task lifecycle events are recorded for accountability and compliance.

    Attributes:
        id: Unique record identifier (auto-generated)
        event_id: Original event's unique ID
        event_type: Event type (task.created, task.updated, etc.)
        task_id: Associated task's UUID (indexed)
        user_id: Actor who triggered the event (indexed)
        timestamp: When the event occurred (indexed)
        payload: Full event payload as JSONB
        correlation_id: Distributed tracing ID (optional)
        created_at: When this record was created
    """
    __tablename__ = "audit_records"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique audit record identifier",
    )
    event_id: UUID = Field(
        description="Original event's unique ID",
    )
    event_type: str = Field(
        max_length=50,
        description="Event type (e.g., task.created, task.updated)",
    )
    task_id: UUID = Field(
        index=True,
        description="Associated task's UUID",
    )
    user_id: str = Field(
        index=True,
        max_length=255,
        description="Actor who triggered the event",
    )
    timestamp: datetime = Field(
        index=True,
        description="When the event occurred (UTC)",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
        description="Full event payload",
    )
    correlation_id: Optional[UUID] = Field(
        default=None,
        description="Correlation ID for distributed tracing",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this record was created (UTC)",
    )
