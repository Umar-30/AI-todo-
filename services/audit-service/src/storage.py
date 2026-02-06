"""
Audit storage layer.

T089-T090: Append-only storage for audit records.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Session, create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")

_engine = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        _engine = create_engine(db_url, echo=False, pool_pre_ping=True)
    return _engine


def ensure_table():
    """T089: Create audit_records table if not exists."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_name = 'audit_records'
            """))
            if not result.fetchone():
                conn.execute(text("""
                    CREATE TABLE audit_records (
                        id UUID PRIMARY KEY,
                        event_id UUID NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        task_id UUID NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        payload JSONB NOT NULL DEFAULT '{}',
                        correlation_id UUID,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_task_id ON audit_records(task_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_records(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_records(timestamp)"))
                conn.commit()
                logger.info("Created audit_records table")
    except Exception as e:
        logger.error(f"Failed to ensure audit_records table: {e}")


def append_audit_record(
    event_id: str,
    event_type: str,
    task_id: str,
    user_id: str,
    timestamp: str,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> Optional[str]:
    """
    T090: Append-only storage handler. Insert audit record.

    Args:
        event_id: Unique event ID
        event_type: Event type (task.created, task.updated, etc.)
        task_id: The task ID
        user_id: The user ID
        timestamp: Event timestamp ISO8601
        payload: Full event payload
        correlation_id: Optional correlation ID

    Returns:
        Record ID if successful, None otherwise
    """
    record_id = str(uuid4())
    engine = get_engine()

    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO audit_records (id, event_id, event_type, task_id, user_id, timestamp, payload, correlation_id)
                    VALUES (:id, :event_id, :event_type, :task_id, :user_id, :timestamp, :payload::jsonb, :correlation_id)
                """),
                {
                    "id": record_id,
                    "event_id": event_id,
                    "event_type": event_type,
                    "task_id": task_id,
                    "user_id": user_id,
                    "timestamp": timestamp,
                    "payload": str(payload).replace("'", '"') if isinstance(payload, dict) else payload,
                    "correlation_id": correlation_id,
                },
            )
            conn.commit()
            logger.info(f"Stored audit record {record_id} for event {event_type}")
            return record_id
    except Exception as e:
        logger.error(f"Failed to store audit record: {e}")
        return None


def check_duplicate(event_id: str) -> bool:
    """
    T091: Check if event already processed (idempotency).

    Args:
        event_id: The event ID to check

    Returns:
        True if duplicate, False otherwise
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM audit_records WHERE event_id = :event_id LIMIT 1"),
                {"event_id": event_id},
            )
            return result.fetchone() is not None
    except Exception as e:
        logger.error(f"Failed to check duplicate: {e}")
        return False


def get_audit_history(task_id: str) -> List[Dict[str, Any]]:
    """
    T092: Query audit history for a task.

    Args:
        task_id: The task ID

    Returns:
        List of audit records ordered by timestamp
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, event_id, event_type, task_id, user_id, timestamp, payload, correlation_id, created_at
                    FROM audit_records
                    WHERE task_id = :task_id
                    ORDER BY timestamp ASC
                """),
                {"task_id": task_id},
            )
            rows = result.fetchall()
            return [
                {
                    "id": str(row[0]),
                    "event_id": str(row[1]),
                    "event_type": row[2],
                    "task_id": str(row[3]),
                    "user_id": row[4],
                    "timestamp": row[5].isoformat() if row[5] else None,
                    "payload": row[6],
                    "correlation_id": str(row[7]) if row[7] else None,
                    "created_at": row[8].isoformat() if row[8] else None,
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Failed to get audit history: {e}")
        return []
