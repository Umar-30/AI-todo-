# Tasks: Event-Driven Dapr System

**Input**: Design documents from `/specs/009-event-driven-dapr-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks omitted (can be added on request)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Microservices**: `services/{service-name}/src/`
- **Dapr Components**: `dapr/components/`
- **Kubernetes**: `k8s/manifests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Dapr runtime, and messaging infrastructure

- [ ] T001 Install Dapr CLI and initialize on Minikube cluster
- [ ] T002 [P] Deploy Redpanda single-node cluster using Helm in k8s/manifests/redpanda/
- [ ] T003 [P] Deploy Redis for state store in k8s/manifests/redis/
- [ ] T004 Create Dapr Pub/Sub component in dapr/components/pubsub-redpanda.yaml
- [ ] T005 Create Dapr State Store component in dapr/components/statestore-redis.yaml
- [ ] T006 [P] Create Dapr Secrets component in dapr/components/secrets-local.yaml
- [ ] T007 Create Kafka topics (task-events, reminders, task-updates) in Redpanda
- [ ] T008 Verify Dapr dashboard shows all components healthy

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Event Publishing Infrastructure

- [ ] T009 Create Dapr HTTP client wrapper in backend/src/services/dapr_client.py
- [ ] T010 [P] Define CloudEvents envelope schema in backend/src/events/event_schemas.py
- [ ] T011 [P] Define TaskEvent Pydantic model in backend/src/events/event_schemas.py
- [ ] T012 [P] Define ReminderEvent Pydantic model in backend/src/events/event_schemas.py
- [ ] T013 [P] Define TaskUpdateEvent Pydantic model in backend/src/events/event_schemas.py

### Task Model Enhancements

- [ ] T014 Add tags field (TEXT[]) to Task model in backend/src/models/task.py
- [ ] T015 [P] Add reminder_time field to Task model in backend/src/models/task.py
- [ ] T016 [P] Add recurrence_pattern field to Task model in backend/src/models/task.py
- [ ] T017 [P] Add recurrence_end_date field to Task model in backend/src/models/task.py
- [ ] T018 [P] Add parent_task_id field to Task model in backend/src/models/task.py
- [ ] T019 Create database migration for new Task fields in backend/src/database.py
- [ ] T020 Create AuditRecord model in backend/src/models/audit.py

### Backend Event Publishing

- [ ] T021 Modify task creation to publish task.created event in backend/src/api/tasks.py
- [ ] T022 Modify task update to publish task.updated event in backend/src/api/tasks.py
- [ ] T023 Modify task completion to publish task.completed event in backend/src/api/tasks.py
- [ ] T024 Modify task deletion to publish task.deleted event in backend/src/api/tasks.py
- [ ] T025 Add correlation ID generation for event tracing in backend/src/events/task_events.py
- [ ] T026 Add dual-publish to task-updates topic for realtime sync in backend/src/api/tasks.py

### MCP Tool Updates

- [ ] T027 Update add_task MCP tool to accept priority, tags, recurrence in backend/src/mcp/tools.py
- [ ] T028 Update update_task MCP tool to handle new fields in backend/src/mcp/tools.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recurring Task Management (Priority: P1) 🎯 MVP

**Goal**: Users can create recurring tasks that auto-generate next occurrence when completed

**Independent Test**: Create a daily recurring task, mark complete, verify next occurrence auto-created within 5 seconds

### Recurring Task Service

- [ ] T029 [US1] Create service directory structure for services/recurring-task-service/
- [ ] T030 [US1] Create requirements.txt with FastAPI, httpx, pydantic in services/recurring-task-service/
- [ ] T031 [US1] Create FastAPI app scaffold in services/recurring-task-service/src/main.py
- [ ] T032 [US1] Implement Dapr subscription endpoint for task.completed in services/recurring-task-service/src/main.py
- [ ] T033 [US1] Implement recurrence date calculation logic in services/recurring-task-service/src/recurrence.py
- [ ] T034 [US1] Handle daily recurrence pattern (add 1 day) in services/recurring-task-service/src/recurrence.py
- [ ] T035 [US1] Handle weekly recurrence pattern (add 7 days) in services/recurring-task-service/src/recurrence.py
- [ ] T036 [US1] Handle monthly recurrence pattern with edge cases in services/recurring-task-service/src/recurrence.py
- [ ] T037 [US1] Implement event handler to create next occurrence in services/recurring-task-service/src/handlers.py
- [ ] T038 [US1] Call backend API via Dapr service invocation to create new task in services/recurring-task-service/src/handlers.py
- [ ] T039 [US1] Publish task.created event for new occurrence in services/recurring-task-service/src/handlers.py
- [ ] T040 [US1] Create Dockerfile for recurring-task-service in services/recurring-task-service/Dockerfile
- [ ] T041 [US1] Create K8s deployment with Dapr annotations in k8s/manifests/recurring-task-service.yaml

**Checkpoint**: User Story 1 (Recurring Tasks) is fully functional and testable independently

---

## Phase 4: User Story 2 - Real-Time Task Synchronization (Priority: P1)

**Goal**: Task changes appear on all connected sessions within 2 seconds

**Independent Test**: Open two browser tabs, create task in one, verify appears in other within 2 seconds

### Realtime Sync Service

- [ ] T042 [US2] Create service directory structure for services/realtime-sync-service/
- [ ] T043 [US2] Create requirements.txt with FastAPI, websockets, httpx in services/realtime-sync-service/
- [ ] T044 [US2] Create FastAPI app scaffold with WebSocket support in services/realtime-sync-service/src/main.py
- [ ] T045 [US2] Implement WebSocket connection manager in services/realtime-sync-service/src/websocket.py
- [ ] T046 [US2] Implement user session tracking via Dapr State in services/realtime-sync-service/src/websocket.py
- [ ] T047 [US2] Implement Dapr subscription for task-updates topic in services/realtime-sync-service/src/main.py
- [ ] T048 [US2] Implement event handler to filter by user_id in services/realtime-sync-service/src/handlers.py
- [ ] T049 [US2] Implement broadcast to all user sessions in services/realtime-sync-service/src/handlers.py
- [ ] T050 [US2] Handle connection lifecycle (connect/disconnect/reconnect) in services/realtime-sync-service/src/websocket.py
- [ ] T051 [US2] Buffer updates during brief disconnections in services/realtime-sync-service/src/websocket.py
- [ ] T052 [US2] Create Dockerfile for realtime-sync-service in services/realtime-sync-service/Dockerfile
- [ ] T053 [US2] Create K8s deployment with Dapr annotations in k8s/manifests/realtime-sync-service.yaml

### Frontend WebSocket Integration

- [ ] T054 [US2] Add WebSocket client hook in frontend (location per existing frontend structure)
- [ ] T055 [US2] Handle incoming task create/update/delete messages in frontend
- [ ] T056 [US2] Implement reconnection logic with state sync in frontend
- [ ] T057 [US2] Replace/augment existing SSE with WebSocket in frontend

**Checkpoint**: User Story 2 (Real-Time Sync) is fully functional and testable independently

---

## Phase 5: User Story 3 - Due Date Reminders (Priority: P2)

**Goal**: Users receive reminders before task due dates via chatbot

**Independent Test**: Set task due 5 minutes in future with reminder, verify notification delivered

### Reminder Service

- [ ] T058 [US3] Create service directory structure for services/reminder-service/
- [ ] T059 [US3] Create requirements.txt with FastAPI, httpx, pydantic in services/reminder-service/
- [ ] T060 [US3] Create FastAPI app scaffold in services/reminder-service/src/main.py
- [ ] T061 [US3] Implement Dapr subscription for task.created, task.updated in services/reminder-service/src/main.py
- [ ] T062 [US3] Implement reminder state storage via Dapr State API in services/reminder-service/src/scheduler.py
- [ ] T063 [US3] Create Dapr Cron binding component in dapr/components/cron-reminder.yaml
- [ ] T064 [US3] Implement cron handler endpoint /reminders/check in services/reminder-service/src/main.py
- [ ] T065 [US3] Implement reminder check logic (query due reminders) in services/reminder-service/src/scheduler.py
- [ ] T066 [US3] Publish reminder.triggered event when reminder due in services/reminder-service/src/handlers.py
- [ ] T067 [US3] Cancel reminders when task completed/deleted in services/reminder-service/src/handlers.py
- [ ] T068 [US3] Reschedule reminders when due date changed in services/reminder-service/src/handlers.py
- [ ] T069 [US3] Create Dockerfile for reminder-service in services/reminder-service/Dockerfile
- [ ] T070 [US3] Create K8s deployment with Dapr annotations in k8s/manifests/reminder-service.yaml

**Checkpoint**: User Story 3 (Reminders) is fully functional and testable independently

---

## Phase 6: User Story 4 - Task Organization with Priorities and Tags (Priority: P2)

**Goal**: Users can set priorities (High/Medium/Low) and tags on tasks

**Independent Test**: Create tasks with different priorities and tags, filter by each

### API Enhancements

- [ ] T071 [US4] Add priority parameter to task creation endpoint in backend/src/api/tasks.py
- [ ] T072 [US4] Add tags parameter to task creation endpoint in backend/src/api/tasks.py
- [ ] T073 [US4] Add priority/tags to task update endpoint in backend/src/api/tasks.py
- [ ] T074 [US4] Add filter by priority query parameter in backend/src/api/tasks.py
- [ ] T075 [US4] Add filter by tags query parameter in backend/src/api/tasks.py
- [ ] T076 [US4] Update API response schemas to include priority/tags in backend/src/api/schemas.py

**Checkpoint**: User Story 4 (Priorities/Tags) is fully functional and testable independently

---

## Phase 7: User Story 5 - Search, Filter, and Sort Tasks (Priority: P2)

**Goal**: Users can search text, filter by status/priority/tags, sort by various fields

**Independent Test**: Create 10 tasks with varied properties, search by keyword, verify correct results

### Search and Sort API

- [ ] T077 [US5] Add text search parameter (title/description) in backend/src/api/tasks.py
- [ ] T078 [US5] Add filter by status (pending/completed) in backend/src/api/tasks.py
- [ ] T079 [US5] Add sort by due_date parameter in backend/src/api/tasks.py
- [ ] T080 [US5] Add sort by priority parameter in backend/src/api/tasks.py
- [ ] T081 [US5] Add sort by created_at parameter in backend/src/api/tasks.py
- [ ] T082 [US5] Implement combined filter logic (AND multiple criteria) in backend/src/api/tasks.py
- [ ] T083 [US5] Optimize database queries with proper indexes in backend/src/database.py

**Checkpoint**: User Story 5 (Search/Filter/Sort) is fully functional and testable independently

---

## Phase 8: User Story 6 - Audit Trail for Task Changes (Priority: P3)

**Goal**: All task changes are logged with timestamp, user, and change details

**Independent Test**: Create task, modify twice, query audit history showing all changes

### Audit Service

- [ ] T084 [US6] Create service directory structure for services/audit-service/
- [ ] T085 [US6] Create requirements.txt with FastAPI, httpx, sqlalchemy in services/audit-service/
- [ ] T086 [US6] Create FastAPI app scaffold in services/audit-service/src/main.py
- [ ] T087 [US6] Implement Dapr subscription for ALL task-events in services/audit-service/src/main.py
- [ ] T088 [US6] Implement Dapr subscription for task-updates topic in services/audit-service/src/main.py
- [ ] T089 [US6] Create audit_records table migration in services/audit-service/src/storage.py
- [ ] T090 [US6] Implement append-only storage handler in services/audit-service/src/storage.py
- [ ] T091 [US6] Implement idempotency check (prevent duplicate events) in services/audit-service/src/handlers.py
- [ ] T092 [US6] Implement query endpoint GET /audit/{task_id} in services/audit-service/src/main.py
- [ ] T093 [US6] Create Dockerfile for audit-service in services/audit-service/Dockerfile
- [ ] T094 [US6] Create K8s deployment with Dapr annotations in k8s/manifests/audit-service.yaml

### Backend Audit API

- [ ] T095 [US6] Add audit history endpoint in backend API in backend/src/api/audit.py
- [ ] T096 [US6] Register audit router in backend main.py in backend/src/main.py

**Checkpoint**: User Story 6 (Audit Trail) is fully functional and testable independently

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Helm Chart Updates

- [ ] T097 [P] Add recurring-task-service to Helm values in k8s/helm/todo-chatbot/values.yaml
- [ ] T098 [P] Add reminder-service to Helm values in k8s/helm/todo-chatbot/values.yaml
- [ ] T099 [P] Add audit-service to Helm values in k8s/helm/todo-chatbot/values.yaml
- [ ] T100 [P] Add realtime-sync-service to Helm values in k8s/helm/todo-chatbot/values.yaml

### Documentation

- [ ] T101 [P] Update README with architecture diagram
- [ ] T102 [P] Document Dapr component configurations in docs/dapr-setup.md
- [ ] T103 Validate quickstart.md instructions work end-to-end
- [ ] T104 Create troubleshooting runbook in docs/troubleshooting.md

### Error Handling & Resilience

- [ ] T105 Add retry logic for Dapr publish failures in backend/src/services/dapr_client.py
- [ ] T106 Add circuit breaker for service invocation in backend/src/services/dapr_client.py
- [ ] T107 Add health check endpoints to all microservices

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Recurring Tasks | P1 | Phase 2 only | US2, US4, US5, US6 |
| US2 - Real-Time Sync | P1 | Phase 2 only | US1, US3, US4, US5, US6 |
| US3 - Reminders | P2 | Phase 2 only | US1, US2, US4, US5, US6 |
| US4 - Priorities/Tags | P2 | Phase 2 only | US1, US2, US3, US5, US6 |
| US5 - Search/Filter | P2 | Phase 2 only | US1, US2, US3, US4, US6 |
| US6 - Audit Trail | P3 | Phase 2 only | US1, US2, US3, US4, US5 |

### Within Each User Story

1. Service scaffold before handlers
2. Handlers before event publishing
3. Dockerfile before K8s deployment
4. Backend changes can parallel with service development

---

## Parallel Execution Examples

### Phase 1 Parallel Tasks
```bash
# These can run simultaneously:
T002: Deploy Redpanda
T003: Deploy Redis
T006: Create Dapr Secrets component
```

### Phase 2 Parallel Tasks
```bash
# Event schemas (different sections of same file, but independent):
T010: CloudEvents envelope schema
T011: TaskEvent model
T012: ReminderEvent model
T013: TaskUpdateEvent model

# Task model fields (different fields):
T015: reminder_time field
T016: recurrence_pattern field
T017: recurrence_end_date field
T018: parent_task_id field
```

### User Story Parallel Development
```bash
# With 3 developers after Phase 2:
Developer A: US1 (Recurring Tasks) - T029-T041
Developer B: US2 (Real-Time Sync) - T042-T057
Developer C: US4 (Priorities/Tags) - T071-T076
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (Infrastructure)
2. Complete Phase 2: Foundational (Event publishing, model enhancements)
3. Complete Phase 3: User Story 1 - Recurring Tasks
4. Complete Phase 4: User Story 2 - Real-Time Sync
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready (MVP delivered!)

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1 (Recurring) → Test → Deploy (Milestone 1)
3. Add US2 (Real-Time) → Test → Deploy (Milestone 2, MVP complete)
4. Add US3 (Reminders) → Test → Deploy (Milestone 3)
5. Add US4+US5 (Organization) → Test → Deploy (Milestone 4)
6. Add US6 (Audit) → Test → Deploy (Milestone 5, Feature complete)

### Suggested MVP Scope

**Minimum**: US1 (Recurring Tasks) + US2 (Real-Time Sync)
- Both are P1 priority
- Demonstrates event-driven architecture end-to-end
- Most impactful for user experience

---

## Summary

| Category | Count |
|----------|-------|
| **Total Tasks** | 107 |
| Phase 1 (Setup) | 8 |
| Phase 2 (Foundational) | 20 |
| Phase 3 (US1 - Recurring) | 13 |
| Phase 4 (US2 - Real-Time) | 16 |
| Phase 5 (US3 - Reminders) | 13 |
| Phase 6 (US4 - Priorities) | 6 |
| Phase 7 (US5 - Search) | 7 |
| Phase 8 (US6 - Audit) | 13 |
| Phase 9 (Polish) | 11 |
| **Parallel Opportunities** | 35 tasks marked [P] |

---

## Notes

- [P] tasks = different files, no dependencies between them
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All microservices follow same pattern: scaffold → handlers → Dockerfile → K8s
