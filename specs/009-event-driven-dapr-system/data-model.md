# Data Model: Event-Driven Dapr System

**Feature**: 009-event-driven-dapr-system
**Date**: 2026-02-06
**Spec**: [spec.md](./spec.md)

## Entity Definitions

### Task (Enhanced)

Extends existing Task model with new fields for recurring tasks, priorities, tags, and reminders.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key, auto-generated |
| user_id | string | Yes | Owner's identifier (indexed) |
| title | string | Yes | Task title (max 255 chars) |
| description | string | No | Detailed description |
| completed | boolean | Yes | Completion status (default: false) |
| priority | enum | No | "high" \| "medium" \| "low" |
| category | string | No | Legacy field, kept for compatibility |
| tags | string[] | No | Array of user-defined tags |
| due_date | datetime | No | Task deadline (UTC) |
| reminder_time | datetime | No | When to send reminder (UTC) |
| recurrence_pattern | enum | No | "daily" \| "weekly" \| "monthly" |
| recurrence_end_date | datetime | No | When recurrence stops |
| parent_task_id | UUID | No | Links recurring instances to original |
| created_at | datetime | Yes | Creation timestamp (UTC) |
| updated_at | datetime | Yes | Last modification (UTC) |

**Validation Rules**:
- `title` must be non-empty, max 255 characters
- `priority` must be one of: high, medium, low (or null)
- `recurrence_pattern` must be one of: daily, weekly, monthly (or null)
- `reminder_time` must be before `due_date` if both set
- `recurrence_end_date` must be after `created_at` if set
- `tags` array max 10 items, each max 50 characters

**State Transitions**:
```
pending → completed (via complete action)
completed → pending (via uncomplete action)
any → deleted (via delete action)
```

---

### RecurrencePattern (Value Object)

Embedded within Task, not a separate table.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pattern | enum | Yes | "daily" \| "weekly" \| "monthly" |
| end_date | datetime | No | Optional end date for recurrence |
| next_occurrence | datetime | No | Calculated next occurrence date |

**Calculation Rules**:
- Daily: Add 1 day to current due_date
- Weekly: Add 7 days to current due_date
- Monthly: Add 1 month, normalize to last day if overflow

---

### Reminder (Dapr State)

Stored in Dapr State Store (Redis), not database.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| reminder_id | string | Yes | Composite key: `{user_id}:{task_id}` |
| task_id | UUID | Yes | Associated task |
| user_id | string | Yes | Task owner |
| reminder_time | datetime | Yes | When to trigger (UTC) |
| task_title | string | Yes | Cached for notification |
| status | enum | Yes | "pending" \| "triggered" \| "cancelled" |

**Key Format**: `reminder:{user_id}:{task_id}`

**TTL**: Automatically expire 1 hour after `reminder_time`

---

### AuditRecord (Append-Only)

Immutable audit log entry stored in PostgreSQL.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key, auto-generated |
| event_id | UUID | Yes | Original event's ID |
| event_type | string | Yes | e.g., "task.created", "task.updated" |
| task_id | UUID | Yes | Associated task (indexed) |
| user_id | string | Yes | Actor who triggered event |
| timestamp | datetime | Yes | When event occurred (UTC) |
| payload | jsonb | Yes | Full event payload |
| correlation_id | UUID | No | For distributed tracing |

**Indexes**:
- `task_id` - For querying task history
- `user_id` - For querying user activity
- `timestamp` - For time-range queries

**Constraints**:
- Table is append-only (no UPDATE/DELETE)
- Retention: 90 days (configurable)

---

### UserSession (Dapr State)

Tracks active WebSocket connections in Dapr State Store.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Unique session identifier |
| user_id | string | Yes | Associated user |
| connected_at | datetime | Yes | Connection timestamp |
| last_activity | datetime | Yes | Last message/heartbeat |
| connection_info | object | No | Metadata (IP, user-agent) |

**Key Format**: `session:{user_id}:{session_id}`

**TTL**: 30 minutes after `last_activity` (extended on each heartbeat)

---

## Event Schemas

### TaskEvent (task-events topic)

CloudEvents-compliant envelope for all task lifecycle events.

```json
{
  "specversion": "1.0",
  "type": "task.created | task.updated | task.completed | task.deleted",
  "source": "todo-backend",
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "time": "2026-02-06T10:30:00.000Z",
  "datacontenttype": "application/json",
  "subject": "task:3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "data": {
    "taskId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "userId": "user-123",
    "title": "Complete project report",
    "description": "Finish Q1 report for management",
    "priority": "high",
    "status": "pending",
    "tags": ["work", "urgent"],
    "dueDate": "2026-02-10T17:00:00.000Z",
    "reminderTime": "2026-02-10T09:00:00.000Z",
    "recurrence": {
      "pattern": "weekly",
      "endDate": "2026-03-31T00:00:00.000Z"
    },
    "previousValues": {
      "title": "Complete report"
    }
  },
  "correlationid": "abc123"
}
```

**Event Types**:
| Type | When Emitted | Payload Includes |
|------|--------------|------------------|
| task.created | New task created | Full task data |
| task.updated | Any field modified | Full task + previousValues |
| task.completed | completed=true | Full task data |
| task.deleted | Task deleted | taskId, userId only |

---

### ReminderEvent (reminders topic)

Events related to reminder lifecycle.

```json
{
  "specversion": "1.0",
  "type": "reminder.scheduled | reminder.triggered | reminder.cancelled",
  "source": "reminder-service",
  "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
  "time": "2026-02-06T10:30:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "taskId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "userId": "user-123",
    "taskTitle": "Complete project report",
    "reminderTime": "2026-02-10T09:00:00.000Z",
    "reminderType": "before_due"
  }
}
```

---

### TaskUpdateEvent (task-updates topic)

Lightweight event for real-time sync (full task included).

```json
{
  "specversion": "1.0",
  "type": "sync.task_changed",
  "source": "todo-backend",
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "time": "2026-02-06T10:30:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "taskId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "userId": "user-123",
    "changeType": "created | updated | deleted | completed",
    "task": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "Complete project report",
      "completed": false,
      "priority": "high",
      "tags": ["work", "urgent"],
      "dueDate": "2026-02-10T17:00:00.000Z"
    }
  }
}
```

---

## Relationships

```
User (1) ──────────< (N) Task
                         │
                         │ parent_task_id (self-reference)
                         ▼
                    Task (recurring parent)

Task (1) ──────────< (N) AuditRecord

Task (1) ──────────< (1) Reminder (Dapr State)

User (1) ──────────< (N) UserSession (Dapr State)
```

## Migration Strategy

### Database Migrations

1. **Add new columns to tasks table**:
   ```sql
   ALTER TABLE tasks ADD COLUMN tags TEXT[];
   ALTER TABLE tasks ADD COLUMN reminder_time TIMESTAMP WITH TIME ZONE;
   ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20);
   ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE;
   ALTER TABLE tasks ADD COLUMN parent_task_id UUID REFERENCES tasks(id);
   ```

2. **Create audit_records table**:
   ```sql
   CREATE TABLE audit_records (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     event_id UUID NOT NULL,
     event_type VARCHAR(50) NOT NULL,
     task_id UUID NOT NULL,
     user_id VARCHAR(255) NOT NULL,
     timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
     payload JSONB NOT NULL,
     correlation_id UUID,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   CREATE INDEX idx_audit_task_id ON audit_records(task_id);
   CREATE INDEX idx_audit_user_id ON audit_records(user_id);
   CREATE INDEX idx_audit_timestamp ON audit_records(timestamp);
   ```

### Backward Compatibility

- All new fields are optional (nullable)
- Existing API responses include new fields with null/empty defaults
- Existing MCP tools continue to work without modification
- New fields only populated when explicitly set by user
