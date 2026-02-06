# Implementation Plan: Event-Driven Dapr System

**Branch**: `009-event-driven-dapr-system` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Phase V - Cloud-Native Todo Chatbot system build specification for event-driven microservice architecture with Dapr integration

## Summary

This plan details the implementation of an event-driven microservice architecture for the Todo Chatbot using Dapr as the runtime abstraction layer. The system adds recurring tasks, due dates/reminders, priorities, tags, search/filter, audit logging, and real-time sync across multiple sessions. All inter-service communication uses Dapr Pub/Sub with Redpanda (Kafka-compatible) - no direct Kafka client libraries allowed.

## Technical Context

**Language/Version**: Python 3.11 (existing backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, Dapr Python SDK, SQLModel, Pydantic
**Storage**: Neon PostgreSQL (existing), Redis (Dapr state store), Redpanda (event streaming)
**Testing**: pytest, pytest-asyncio, contract tests
**Target Platform**: Minikube (local Kubernetes), cloud-ready architecture
**Project Type**: Web application (frontend + backend + microservices)
**Performance Goals**: 2s real-time sync, 500ms search, 100 concurrent users
**Constraints**: No direct Kafka clients, Dapr HTTP APIs only, stateless services
**Scale/Scope**: 4 new microservices, 3 event topics, 18 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| VII. Non-Implementation (Phase IV) | N/A | This is Phase V - new feature development |
| VIII. AI-First Tooling | COMPLIANT | Will use Docker AI, kubectl-ai where available |
| IX. Local-Only Deployment | COMPLIANT | Targeting Minikube first |
| X. Spec-Driven Infrastructure | COMPLIANT | Dapr components defined as YAML specs |
| XI. Beginner-Friendly Simplicity | COMPLIANT | Clear service boundaries, standard patterns |
| XII. Structured Output | COMPLIANT | Event schemas, API contracts defined |
| XIII. AIOps Alignment | COMPLIANT | Dapr enables observability, automation |
| I. MCP-Compliant Architecture | COMPLIANT | Events supplement MCP tools, not replace |
| II. Database as Source of Truth | COMPLIANT | PostgreSQL remains primary; Redis for state |
| III. Stateless Agent Design | COMPLIANT | All services stateless via Dapr |

**Gate Status**: PASSED

## Project Structure

### Documentation (this feature)

```text
specs/009-event-driven-dapr-system/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── task-events.schema.json
│   ├── reminder-events.schema.json
│   └── dapr-components.yaml
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py           # Enhanced with recurrence, tags, reminders
│   │   └── audit.py          # NEW: Audit record model
│   ├── events/
│   │   ├── task_events.py    # MODIFIED: Dapr Pub/Sub integration
│   │   └── event_schemas.py  # NEW: Pydantic event schemas
│   ├── api/
│   │   ├── tasks.py          # MODIFIED: Add event publishing
│   │   └── audit.py          # NEW: Audit query endpoint
│   └── services/
│       └── dapr_client.py    # NEW: Dapr HTTP client wrapper
├── tests/
│   ├── contract/
│   │   └── test_events.py    # Event schema validation
│   └── integration/
│       └── test_pubsub.py    # Dapr Pub/Sub integration tests

services/
├── recurring-task-service/
│   ├── src/
│   │   ├── main.py           # FastAPI app with Dapr subscription
│   │   ├── handlers.py       # Event handlers
│   │   └── recurrence.py     # Date calculation logic
│   ├── Dockerfile
│   └── requirements.txt
├── reminder-service/
│   ├── src/
│   │   ├── main.py           # FastAPI app with Dapr subscription
│   │   ├── handlers.py       # Event handlers
│   │   └── scheduler.py      # Reminder scheduling logic
│   ├── Dockerfile
│   └── requirements.txt
├── audit-service/
│   ├── src/
│   │   ├── main.py           # FastAPI app with Dapr subscription
│   │   ├── handlers.py       # Event handlers
│   │   └── storage.py        # Audit persistence
│   ├── Dockerfile
│   └── requirements.txt
└── realtime-sync-service/
    ├── src/
    │   ├── main.py           # FastAPI app with WebSocket + Dapr
    │   ├── handlers.py       # Event handlers
    │   └── websocket.py      # WebSocket connection manager
    ├── Dockerfile
    └── requirements.txt

dapr/
├── components/
│   ├── pubsub-redpanda.yaml  # Kafka Pub/Sub component
│   ├── statestore-redis.yaml # Redis state store
│   ├── cron-reminder.yaml    # Cron binding for reminders
│   └── secrets-local.yaml    # Local secrets store
└── config/
    └── config.yaml           # Dapr configuration

k8s/
├── manifests/
│   ├── redpanda/             # NEW: Redpanda deployment
│   ├── redis/                # NEW: Redis deployment
│   └── dapr/                 # NEW: Dapr component manifests
└── helm/
    └── todo-chatbot/
        └── values.yaml       # MODIFIED: Add new services
```

**Structure Decision**: Microservices follow monorepo pattern under `services/` directory. Each service is independently deployable with its own Dockerfile. Dapr components stored in `dapr/` directory at repo root.

---

## Phase 0: Research

### Research Tasks

1. **Dapr Python SDK patterns for Pub/Sub** - How to subscribe and publish using HTTP API
2. **Redpanda deployment on Minikube** - Lightweight Kafka-compatible broker setup
3. **WebSocket + Dapr integration** - Bridging Dapr events to WebSocket clients
4. **Cron binding for scheduled tasks** - Dapr binding configuration for reminders
5. **Event schema versioning** - Best practices for evolving event schemas

### Findings

*(To be populated during research phase)*

---

## Phase 1: Implementation Plan (Step-by-Step)

### Stage 1: Infrastructure Setup (Days 1-2)

**Objective**: Deploy Dapr, Redpanda, and Redis on Minikube

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 1.1 | Install Dapr CLI and initialize on Minikube | Minikube running | Dapr runtime installed |
| 1.2 | Deploy Redpanda cluster (single-node for dev) | Step 1.1 | Redpanda pods running |
| 1.3 | Deploy Redis for state store | Step 1.1 | Redis pod running |
| 1.4 | Create Dapr Pub/Sub component (pubsub-redpanda.yaml) | Steps 1.2 | Component registered |
| 1.5 | Create Dapr State Store component (statestore-redis.yaml) | Step 1.3 | Component registered |
| 1.6 | Create Dapr Secrets component (local file for dev) | Step 1.1 | Component registered |
| 1.7 | Verify Dapr dashboard shows all components | Steps 1.4-1.6 | Dashboard accessible |

**Verification**: `dapr components -k` shows all 3 components healthy

---

### Stage 2: Backend Event Publishing (Days 3-4)

**Objective**: Modify existing backend to publish task events via Dapr

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 2.1 | Create Dapr HTTP client wrapper (`dapr_client.py`) | Stage 1 | Reusable publish function |
| 2.2 | Define event schemas as Pydantic models | None | `event_schemas.py` |
| 2.3 | Modify task creation to publish `task.created` event | Steps 2.1, 2.2 | Events published on create |
| 2.4 | Modify task update to publish `task.updated` event | Steps 2.1, 2.2 | Events published on update |
| 2.5 | Modify task completion to publish `task.completed` event | Steps 2.1, 2.2 | Events published on complete |
| 2.6 | Modify task deletion to publish `task.deleted` event | Steps 2.1, 2.2 | Events published on delete |
| 2.7 | Add correlation ID tracking for event tracing | Step 2.2 | Events include correlation ID |
| 2.8 | Write contract tests for event schema validation | Step 2.2 | Tests pass |

**Event Flow**:
```
User Action → API Backend → Dapr Sidecar → Redpanda (task-events topic)
```

---

### Stage 3: Task Model Enhancements (Days 5-6)

**Objective**: Extend Task model with recurring, priority, tags, reminder fields

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 3.1 | Add `priority` field to Task model (high/medium/low) | None | DB migration |
| 3.2 | Add `tags` field to Task model (array of strings) | None | DB migration |
| 3.3 | Add `recurrence_pattern` field (daily/weekly/monthly/null) | None | DB migration |
| 3.4 | Add `recurrence_end_date` field (optional) | None | DB migration |
| 3.5 | Add `reminder_time` field (datetime, optional) | None | DB migration |
| 3.6 | Update MCP tools to handle new fields | Steps 3.1-3.5 | Tools accept new params |
| 3.7 | Update API endpoints for new fields | Steps 3.1-3.5 | REST API updated |
| 3.8 | Add search/filter/sort query parameters | Steps 3.1-3.2 | Query params working |

**Model Changes**:
```python
# New fields on Task model
priority: Optional[str]  # "high" | "medium" | "low"
tags: Optional[List[str]]  # ["work", "urgent"]
recurrence_pattern: Optional[str]  # "daily" | "weekly" | "monthly"
recurrence_end_date: Optional[datetime]
reminder_time: Optional[datetime]
```

---

### Stage 4: Recurring Task Service (Days 7-8)

**Objective**: Build service that creates next task instance when recurring task completes

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 4.1 | Create service scaffold (FastAPI + Dapr subscription) | Stage 1 | Service skeleton |
| 4.2 | Implement Dapr subscription endpoint for `task.completed` | Step 4.1 | Receives events |
| 4.3 | Implement recurrence date calculation logic | None | `recurrence.py` |
| 4.4 | Implement next occurrence creation via Dapr service invocation | Steps 4.2, 4.3 | Creates new tasks |
| 4.5 | Publish `task.created` event for new occurrence | Step 4.4 | Event chain works |
| 4.6 | Handle edge cases (month-end, Feb 30) | Step 4.3 | Edge cases covered |
| 4.7 | Write unit tests for recurrence logic | Step 4.3 | Tests pass |
| 4.8 | Create Dockerfile and K8s deployment | Step 4.1 | Deployable |

**Event Flow**:
```
task-events (completed) → Recurring Service → Dapr Service Invocation → Backend API
                                           → task-events (created)
```

---

### Stage 5: Reminder Service (Days 9-10)

**Objective**: Build service that schedules and triggers reminders

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 5.1 | Create service scaffold with Dapr subscription | Stage 1 | Service skeleton |
| 5.2 | Implement subscription for `task.created`, `task.updated` | Step 5.1 | Receives events |
| 5.3 | Implement reminder state storage via Dapr State API | Step 5.1 | Reminders persisted |
| 5.4 | Create Dapr Cron binding (every 1 minute) | Stage 1 | Cron triggers |
| 5.5 | Implement reminder check handler (on cron trigger) | Steps 5.3, 5.4 | Checks due reminders |
| 5.6 | Publish `reminder.triggered` event when reminder due | Step 5.5 | Events published |
| 5.7 | Cancel reminders when task completed/deleted | Step 5.2 | Cleanup works |
| 5.8 | Reschedule reminders when due date changed | Step 5.2 | Updates work |
| 5.9 | Write integration tests | Steps 5.1-5.8 | Tests pass |
| 5.10 | Create Dockerfile and K8s deployment | Step 5.1 | Deployable |

**Event Flow**:
```
task-events → Reminder Service → Dapr State (store schedule)
Cron Binding → Reminder Service → reminders topic (triggered)
```

---

### Stage 6: Audit Log Service (Days 11-12)

**Objective**: Build service that persists all task events to audit log

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 6.1 | Create service scaffold with Dapr subscription | Stage 1 | Service skeleton |
| 6.2 | Create AuditRecord model (Pydantic) | None | Model defined |
| 6.3 | Implement subscription for ALL events on `task-events` | Step 6.1 | Receives all events |
| 6.4 | Implement subscription for `task-updates` topic | Step 6.1 | Receives updates |
| 6.5 | Implement append-only storage (PostgreSQL table) | Step 6.2 | Events persisted |
| 6.6 | Implement query endpoint (by task_id) | Step 6.5 | History retrievable |
| 6.7 | Ensure at-least-once processing (idempotency) | Steps 6.3-6.4 | No duplicates |
| 6.8 | Write integration tests | Steps 6.1-6.7 | Tests pass |
| 6.9 | Create Dockerfile and K8s deployment | Step 6.1 | Deployable |

**Event Flow**:
```
task-events → Audit Service → PostgreSQL (append-only)
task-updates → Audit Service → PostgreSQL (append-only)
```

---

### Stage 7: Realtime Sync Service (Days 13-14)

**Objective**: Build WebSocket service that pushes updates to connected clients

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 7.1 | Create service scaffold with WebSocket support | Stage 1 | Service skeleton |
| 7.2 | Implement WebSocket connection manager | Step 7.1 | Tracks connections |
| 7.3 | Implement user session state via Dapr State API | Step 7.1 | Sessions tracked |
| 7.4 | Implement Dapr subscription for `task-updates` | Step 7.1 | Receives events |
| 7.5 | Filter events by user_id and broadcast to sessions | Steps 7.2-7.4 | User gets updates |
| 7.6 | Handle connection lifecycle (connect/disconnect/reconnect) | Step 7.2 | Lifecycle managed |
| 7.7 | Buffer updates during brief disconnections | Steps 7.3, 7.6 | No lost updates |
| 7.8 | Write integration tests | Steps 7.1-7.7 | Tests pass |
| 7.9 | Create Dockerfile and K8s deployment | Step 7.1 | Deployable |

**Event Flow**:
```
task-updates → Realtime Service → WebSocket → Frontend Client(s)
```

---

### Stage 8: Backend Dual Publishing (Day 15)

**Objective**: Backend publishes to both `task-events` and `task-updates` topics

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 8.1 | Add `task-updates` publishing for real-time sync | Stage 2 | Dual publish |
| 8.2 | Ensure `task-updates` contains full task object | Step 8.1 | Full data for sync |
| 8.3 | Verify end-to-end flow: Backend → Redpanda → Realtime → Client | Steps 7.9, 8.1 | Flow works |

---

### Stage 9: Frontend WebSocket Integration (Days 16-17)

**Objective**: Connect frontend to Realtime Sync Service

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 9.1 | Add WebSocket client to frontend | Stage 7 | Client connects |
| 9.2 | Handle incoming task updates (create/update/delete) | Step 9.1 | UI updates |
| 9.3 | Implement reconnection logic with state sync | Step 9.1 | Reconnects cleanly |
| 9.4 | Replace/augment existing SSE with WebSocket | Step 9.2 | Migration complete |
| 9.5 | Test multi-session sync (2 browser tabs) | Steps 9.1-9.3 | Sync works |

---

### Stage 10: Integration Testing & Hardening (Days 18-19)

**Objective**: End-to-end testing and error handling

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 10.1 | Test recurring task full flow | Stages 4, 8 | Flow verified |
| 10.2 | Test reminder full flow | Stages 5, 8 | Flow verified |
| 10.3 | Test audit logging full flow | Stage 6 | Flow verified |
| 10.4 | Test real-time sync full flow | Stages 7, 9 | Flow verified |
| 10.5 | Test Redpanda unavailability recovery | All | Retry works |
| 10.6 | Load test with 100 concurrent users | All | Performance OK |
| 10.7 | Document troubleshooting runbook | All | Runbook written |

---

### Stage 11: Documentation & Cleanup (Day 20)

**Objective**: Complete documentation and prepare for deployment

| Step | Description | Dependencies | Outputs |
|------|-------------|--------------|---------|
| 11.1 | Update README with architecture diagram | All | README updated |
| 11.2 | Document Dapr component configurations | Stage 1 | Docs complete |
| 11.3 | Write quickstart guide for local development | All | Quickstart ready |
| 11.4 | Create Helm chart values for new services | Stages 4-7 | Helm ready |
| 11.5 | Tag release and create PR | All | PR created |

---

## Service Dependencies Matrix

```
                    ┌──────────────┐
                    │   Backend    │
                    │   (origin)   │
                    └──────┬───────┘
                           │ publishes
                           ▼
              ┌────────────────────────┐
              │     task-events        │
              │     task-updates       │
              └────────────┬───────────┘
                           │ consumed by
        ┌──────────────────┼──────────────────┬─────────────────┐
        ▼                  ▼                  ▼                 ▼
┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌───────────────┐
│  Recurring   │  │   Reminder    │  │    Audit     │  │   Realtime    │
│    Task      │  │   Service     │  │   Service    │  │     Sync      │
└──────────────┘  └───────────────┘  └──────────────┘  └───────────────┘
       │                  │                                    │
       │ service invoke   │ publishes                          │ WebSocket
       ▼                  ▼                                    ▼
   Backend API       reminders topic                      Frontend
```

## Dapr Components Summary

| Component | Type | Configuration |
|-----------|------|---------------|
| `pubsub-redpanda` | `pubsub.kafka` | Brokers: redpanda:9092 |
| `statestore-redis` | `state.redis` | Host: redis:6379 |
| `cron-reminder` | `bindings.cron` | Schedule: @every 1m |
| `secrets-local` | `secretstores.local.file` | Path: /secrets/secrets.json |

## Complexity Tracking

*No constitution violations requiring justification.*

---

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Create feature branch from `009-event-driven-dapr-system`
3. Begin Stage 1: Infrastructure Setup
