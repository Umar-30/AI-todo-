# Feature Specification: Cloud-Native Todo Chatbot - Event-Driven System

**Feature Branch**: `009-event-driven-dapr-system`
**Created**: 2026-02-06
**Status**: Draft
**Input**: Phase V - Cloud-Native Todo Chatbot system build specification for event-driven microservice architecture with Dapr integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Task Management (Priority: P1)

A user wants to create tasks that automatically repeat on a schedule (daily, weekly, or monthly) so they don't have to manually recreate routine tasks. When a recurring task is completed, the next occurrence is automatically generated.

**Why this priority**: Recurring tasks are a fundamental productivity feature that differentiates this from basic todo apps. Users with routine tasks (daily standup, weekly reports, monthly reviews) need this to adopt the chatbot for real work.

**Independent Test**: Can be fully tested by creating a daily recurring task, marking it complete, and verifying the next occurrence is auto-generated. Delivers immediate value for routine task management.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** they create a task with recurrence set to "daily", **Then** the system saves the task with recurrence metadata and schedules the next occurrence
2. **Given** a recurring task exists, **When** the user completes it, **Then** a `task.completed` event is emitted AND a new task instance is created for the next occurrence
3. **Given** a weekly recurring task, **When** the current instance is due, **Then** the reminder service notifies the user at the scheduled time
4. **Given** a recurring task, **When** the user deletes it with "delete all future occurrences", **Then** no new instances are created and the recurrence is cancelled

---

### User Story 2 - Real-Time Task Synchronization (Priority: P1)

A user working across multiple devices expects their task changes to appear instantly on all connected sessions. When they complete a task on their phone, their desktop browser reflects the change within seconds.

**Why this priority**: Real-time sync is essential for a modern chatbot experience. Without it, users may accidentally duplicate work or miss updates, breaking trust in the system.

**Independent Test**: Can be fully tested by opening two browser sessions, creating a task in one, and verifying it appears in the other within 2 seconds.

**Acceptance Scenarios**:

1. **Given** a user has two active sessions, **When** they create a task in session A, **Then** the task appears in session B within 2 seconds without refresh
2. **Given** a user modifies a task (title, priority, due date), **When** the change is saved, **Then** all connected sessions receive and display the update
3. **Given** a user deletes a task, **When** the deletion is confirmed, **Then** all sessions remove the task from their view
4. **Given** a session loses connection, **When** it reconnects, **Then** it synchronizes all changes that occurred during disconnection

---

### User Story 3 - Due Date Reminders (Priority: P2)

A user sets a due date on a task and expects to receive a reminder before the deadline. The reminder should be configurable (e.g., 1 hour before, 1 day before) and delivered through the chatbot interface.

**Why this priority**: Reminders help users meet deadlines and add significant value beyond a basic task list. Without reminders, due dates are merely informational.

**Independent Test**: Can be fully tested by setting a task due date 5 minutes in the future with a reminder, waiting for the reminder notification, and verifying delivery.

**Acceptance Scenarios**:

1. **Given** a task with a due date, **When** the user sets a reminder for "1 hour before", **Then** the system schedules a reminder event
2. **Given** a scheduled reminder, **When** the reminder time arrives, **Then** the user receives a notification through the chatbot
3. **Given** a task is completed before the reminder fires, **When** the reminder time arrives, **Then** no notification is sent (reminder is cancelled)
4. **Given** a task due date is changed, **When** the user modifies the date, **Then** any existing reminders are rescheduled accordingly

---

### User Story 4 - Task Organization with Priorities and Tags (Priority: P2)

A user wants to organize tasks using priorities (High, Medium, Low) and custom tags to categorize and filter their work effectively.

**Why this priority**: Organization features increase the chatbot's utility for users with many tasks. Priorities help with daily planning; tags enable project-level organization.

**Independent Test**: Can be fully tested by creating tasks with different priorities and tags, then filtering to show only "High priority" or tasks tagged "work".

**Acceptance Scenarios**:

1. **Given** a user is creating a task, **When** they set priority to "High", **Then** the task is saved with priority metadata and displayed with visual indication
2. **Given** a task exists, **When** the user adds tags ["work", "urgent"], **Then** the tags are saved and searchable
3. **Given** multiple tasks with various priorities and tags, **When** the user filters by "High priority", **Then** only high-priority tasks are displayed
4. **Given** tasks with tags, **When** the user searches by tag "project-x", **Then** only tasks with that tag are returned

---

### User Story 5 - Search, Filter, and Sort Tasks (Priority: P2)

A user with many tasks wants to quickly find specific tasks by searching text, filtering by status/priority/tags, and sorting by due date, priority, or creation date.

**Why this priority**: As task volume grows, search and filter become essential. Users should not have to scroll through hundreds of tasks to find what they need.

**Independent Test**: Can be fully tested by creating 10 tasks with varied properties, then searching for a keyword and verifying correct results.

**Acceptance Scenarios**:

1. **Given** tasks with various titles, **When** the user searches for "report", **Then** all tasks containing "report" in title or description are returned
2. **Given** completed and pending tasks, **When** the user filters by "completed", **Then** only completed tasks are shown
3. **Given** tasks with different due dates, **When** the user sorts by "due date ascending", **Then** tasks are ordered from soonest to latest
4. **Given** a combined filter (High priority + tag "work"), **When** applied, **Then** only tasks matching ALL criteria are displayed

---

### User Story 6 - Audit Trail for Task Changes (Priority: P3)

A user or administrator wants to see the history of changes made to a task for accountability and debugging purposes. This includes who changed what and when.

**Why this priority**: While not essential for basic functionality, audit trails support compliance, debugging, and team accountability in professional contexts.

**Independent Test**: Can be fully tested by creating a task, modifying it twice, and viewing the audit history showing both changes.

**Acceptance Scenarios**:

1. **Given** any task event (created, updated, completed, deleted), **When** the event is published, **Then** the audit service persists a record with timestamp, user, and change details
2. **Given** a task with history, **When** a user requests the audit trail, **Then** all recorded changes are returned in chronological order
3. **Given** a deleted task, **When** the audit trail is queried, **Then** the deletion event and all prior history remain accessible

---

### Edge Cases

- What happens when a recurring task's recurrence pattern is invalid (e.g., "monthly on Feb 30")?
  - System normalizes to the last valid day of the month
- How does the system handle WebSocket disconnection during a task update?
  - Changes are queued locally and synced on reconnect; conflicts resolved by "last write wins" with server timestamp
- What happens when the message broker (Redpanda) is temporarily unavailable?
  - Events are buffered locally via Dapr and retried with exponential backoff
- How does the system handle reminder scheduling for tasks created in different timezones?
  - All times stored in UTC; reminders scheduled based on user's timezone preference

## System Architecture *(mandatory)*

### Architecture Overview

The system follows an **event-driven microservice architecture** using **Dapr** as the runtime abstraction layer. All inter-service communication occurs through events published to **Redpanda** (Kafka-compatible) via Dapr Pub/Sub. Direct service-to-service calls use Dapr Service Invocation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Chat UI)                              │
│                         WebSocket + Dapr Service Invocation                  │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API Gateway / Backend                             │
│                   (Task CRUD, Chat Agent, Dapr Sidecar)                      │
└─────┬─────────────────┬─────────────────────────────────────────────────────┘
      │                 │
      │ Dapr Pub/Sub    │ Dapr State
      ▼                 ▼
┌─────────────┐  ┌─────────────────┐
│  Redpanda   │  │  State Store    │
│  (Kafka)    │  │  (Redis/Postgres)│
└──────┬──────┘  └─────────────────┘
       │
       │ Events (task-events, reminders, task-updates)
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       ▼                  ▼                  ▼                  ▼
┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌───────────────┐
│  Recurring   │  │  Reminder     │  │  Audit Log   │  │  Realtime     │
│  Task Svc    │  │  Service      │  │  Service     │  │  Sync Svc     │
└──────────────┘  └───────────────┘  └──────────────┘  └───────────────┘
```

### Service Boundaries

| Service                     | Responsibility                              | Subscribes To                      | Publishes To                  |
|-----------------------------|---------------------------------------------|-----------------------------------|-------------------------------|
| **API Backend**             | Task CRUD, user auth, chat agent integration | N/A (origin)                      | `task-events`                 |
| **Recurring Task Service**  | Generate next task instances on completion  | `task-events` (completed)         | `task-events` (created)       |
| **Reminder Service**        | Schedule and deliver task reminders         | `task-events` (created, updated)  | `reminders`                   |
| **Audit Log Service**       | Persist immutable audit records             | `task-events` (all), `task-updates` | N/A (sink)                   |
| **Realtime Sync Service**   | Push updates to connected WebSocket clients | `task-updates`                    | N/A (WebSocket)               |

## Event Definitions *(mandatory)*

### Topics

| Topic          | Purpose                                      | Producers                       | Consumers                    |
|----------------|----------------------------------------------|--------------------------------|------------------------------|
| `task-events`  | Core task lifecycle events                   | API Backend, Recurring Task Svc | All services                 |
| `reminders`    | Scheduled reminder delivery                  | Reminder Service                | Notification handlers        |
| `task-updates` | Lightweight change notifications for sync    | API Backend                     | Realtime Sync Service        |

### Event Schemas (JSON)

#### TaskEvent (task-events topic)

```json
{
  "eventId": "uuid",
  "eventType": "task.created | task.updated | task.completed | task.deleted",
  "timestamp": "ISO8601",
  "userId": "string",
  "correlationId": "uuid (for tracing)",
  "payload": {
    "taskId": "uuid",
    "title": "string",
    "description": "string | null",
    "priority": "high | medium | low",
    "status": "pending | completed",
    "dueDate": "ISO8601 | null",
    "tags": ["string"],
    "recurrence": {
      "pattern": "daily | weekly | monthly | null",
      "nextOccurrence": "ISO8601 | null"
    },
    "previousValues": { "...changed fields before update..." }
  }
}
```

#### ReminderEvent (reminders topic)

```json
{
  "eventId": "uuid",
  "eventType": "reminder.scheduled | reminder.triggered | reminder.cancelled",
  "timestamp": "ISO8601",
  "userId": "string",
  "payload": {
    "taskId": "uuid",
    "taskTitle": "string",
    "reminderTime": "ISO8601",
    "reminderType": "before_due | custom"
  }
}
```

#### TaskUpdateEvent (task-updates topic)

```json
{
  "eventId": "uuid",
  "eventType": "sync.task_changed",
  "timestamp": "ISO8601",
  "userId": "string",
  "payload": {
    "taskId": "uuid",
    "changeType": "created | updated | deleted | completed",
    "task": { "...full task object for create/update..." }
  }
}
```

## Microservice Specifications *(mandatory)*

### Recurring Task Service

**Purpose**: Automatically generate the next occurrence of a recurring task when the current instance is completed.

**Responsibilities**:
- Subscribe to `task.completed` events on `task-events` topic
- Check if completed task has recurrence pattern
- Calculate next occurrence date based on pattern
- Publish `task.created` event for new task instance
- Handle edge cases (month-end dates, timezone boundaries)

**Dapr Components Used**:
- Pub/Sub: Subscribe to `task-events`, publish to `task-events`
- State: Store recurrence schedules (optional, for complex patterns)

**Not Responsible For**: Task CRUD, reminder scheduling, user notifications

---

### Notification / Reminder Service

**Purpose**: Schedule reminders for tasks with due dates and deliver notifications when triggered.

**Responsibilities**:
- Subscribe to `task.created` and `task.updated` events
- Extract due date and reminder preferences
- Schedule reminder using Dapr Cron binding or timer
- Publish `reminder.triggered` event when reminder fires
- Cancel reminders when tasks are completed or deleted
- Reschedule reminders when due dates change

**Dapr Components Used**:
- Pub/Sub: Subscribe to `task-events`, publish to `reminders`
- Bindings: Cron binding for scheduled reminder checks
- State: Store pending reminder schedules

**Not Responsible For**: Delivering notifications to specific channels (that's a separate notification gateway concern)

---

### Audit Log Service

**Purpose**: Maintain an immutable record of all task changes for accountability and compliance.

**Responsibilities**:
- Subscribe to ALL events on `task-events` topic
- Subscribe to `task-updates` topic
- Persist events to append-only storage
- Provide query interface for audit history by task ID
- Ensure no event is lost (at-least-once processing)

**Dapr Components Used**:
- Pub/Sub: Subscribe to `task-events` and `task-updates`
- State or binding to persistent storage (database)

**Not Responsible For**: Modifying tasks, enforcing business rules, real-time sync

---

### Realtime Sync Service

**Purpose**: Push task changes to connected clients in real-time via WebSocket connections.

**Responsibilities**:
- Maintain WebSocket connections for active user sessions
- Subscribe to `task-updates` topic
- Filter events by user ID
- Broadcast changes to all sessions for that user
- Handle connection lifecycle (connect, disconnect, reconnect)
- Buffer updates during brief disconnections

**Dapr Components Used**:
- Pub/Sub: Subscribe to `task-updates`
- State: Track active WebSocket sessions per user

**Not Responsible For**: Task persistence, business logic, reminder scheduling

## Dapr Integration Requirements *(mandatory)*

### Required Dapr Building Blocks

| Building Block        | Component Type                              | Purpose                                    |
|-----------------------|--------------------------------------------|-------------------------------------------|
| **Pub/Sub**           | `pubsub.kafka` (Redpanda)                  | All event publishing and subscription     |
| **State Management**  | `state.redis` or `state.postgresql`        | Task state, conversation state, sessions  |
| **Service Invocation**| Built-in                                   | Frontend to backend communication         |
| **Bindings**          | `bindings.cron`                            | Scheduled reminder checks (every minute)  |
| **Secrets**           | `secretstores.kubernetes` or `local.file` | API keys, database credentials            |

### Dapr Component Configurations (High-Level)

**pubsub-redpanda.yaml**:
- Type: `pubsub.kafka`
- Brokers: Redpanda cluster addresses
- Consumer group per service
- Auto-create topics disabled (explicit topic creation)

**statestore.yaml**:
- Type: `state.redis` (recommended for low-latency)
- Actor state store support for Reminder Service
- TTL support for session state

**cron-binding.yaml**:
- Type: `bindings.cron`
- Schedule: `@every 1m` (check for due reminders)
- Route: `/reminders/check`

### Constraint: No Direct Kafka Clients

All services MUST interact with Redpanda exclusively through Dapr HTTP APIs:

- Publish: `POST /v1.0/publish/<pubsub-name>/<topic>`
- Subscribe: Dapr calls service endpoint with event payload
- No `kafka-js`, `confluent-kafka`, or similar libraries allowed

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST emit a `task.created` event when a new task is created
- **FR-002**: System MUST emit a `task.updated` event when any task field is modified
- **FR-003**: System MUST emit a `task.completed` event when a task is marked complete
- **FR-004**: System MUST emit a `task.deleted` event when a task is deleted
- **FR-005**: System MUST support recurring tasks with daily, weekly, and monthly patterns
- **FR-006**: System MUST automatically create the next occurrence when a recurring task is completed
- **FR-007**: System MUST allow users to set task priorities (High, Medium, Low)
- **FR-008**: System MUST allow users to add multiple tags to a task
- **FR-009**: System MUST support search by task title and description
- **FR-010**: System MUST support filtering by status, priority, and tags
- **FR-011**: System MUST support sorting by due date, priority, and creation date
- **FR-012**: System MUST allow users to set due dates with optional reminders
- **FR-013**: System MUST deliver reminders at the scheduled time via the chatbot
- **FR-014**: System MUST push task changes to all connected sessions in real-time
- **FR-015**: System MUST persist audit records for all task events
- **FR-016**: All inter-service messaging MUST use Dapr Pub/Sub (no direct Kafka clients)
- **FR-017**: System MUST use Dapr State Management for task and conversation state
- **FR-018**: System MUST use Dapr Secrets for all sensitive configuration

### Key Entities

- **Task**: Represents a todo item with id, title, description, status, priority, dueDate, tags, recurrence, userId, createdAt, updatedAt
- **RecurrencePattern**: Defines repetition (pattern: daily/weekly/monthly, nextOccurrence, endDate)
- **Reminder**: Scheduled notification (taskId, userId, reminderTime, status)
- **AuditRecord**: Immutable log entry (eventId, eventType, taskId, userId, timestamp, payload)
- **UserSession**: Active WebSocket connection (sessionId, userId, connectedAt, lastActivity)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Task changes appear on all connected sessions within 2 seconds of the originating action
- **SC-002**: Recurring task next occurrence is created within 5 seconds of completing the current instance
- **SC-003**: Reminders are delivered within 1 minute of the scheduled time
- **SC-004**: System handles 100 concurrent users with real-time sync without degradation
- **SC-005**: Search queries return results within 500ms for users with up to 1000 tasks
- **SC-006**: 100% of task events are captured in the audit log (no data loss)
- **SC-007**: All services recover gracefully from Redpanda unavailability (retry with backoff, no data loss)
- **SC-008**: Users can filter and sort tasks with response times under 300ms

## Assumptions and Constraints *(mandatory)*

### Assumptions

- Dapr is available as a sidecar for all services in the deployment environment
- Redpanda cluster is pre-provisioned and accessible to Dapr
- Users are authenticated and userId is available in all requests (auth system exists)
- Frontend can establish WebSocket connections to the Realtime Sync Service
- UTC is used for all internal timestamps; user timezone is stored as a preference

### Constraints

- **No direct Kafka client libraries** - all messaging via Dapr HTTP APIs only
- Dapr version 1.12+ required for stable Pub/Sub and State features
- Services must be stateless (all state via Dapr State Management)
- Event ordering is per-partition (not global) - design for eventual consistency
- WebSocket connections may be interrupted; clients must handle reconnection

### Out of Scope

- User authentication and authorization (assumed to exist)
- Push notification delivery to mobile devices (only chatbot notifications)
- Complex recurrence patterns (e.g., "every 2nd Tuesday") - only daily/weekly/monthly
- Task sharing or collaboration features
- Offline-first mobile app support
- Email or SMS notification channels

## Dependencies

- **Dapr Runtime** (v1.12+): Core abstraction layer
- **Redpanda**: Kafka-compatible message broker
- **Redis** (recommended) or **PostgreSQL**: State store backend
- **Existing Chat Backend**: For task CRUD operations (from previous phases)
- **Existing Frontend**: For WebSocket integration (from previous phases)
