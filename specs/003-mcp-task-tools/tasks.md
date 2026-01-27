# Tasks: MCP Task Tools

**Input**: Design documents from `/specs/003-mcp-task-tools/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Not explicitly requested in spec - manual verification approach per plan.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/` for source code
- **MCP module**: `backend/src/mcp/` for MCP server and tools

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: MCP module initialization and basic structure

- [x] T001 Create MCP module directory structure at backend/src/mcp/
- [x] T002 Create __init__.py with module exports in backend/src/mcp/__init__.py
- [x] T003 Install Official MCP SDK dependency in backend/pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core MCP server infrastructure that MUST be complete before ANY tool can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create MCP server initialization with database connection in backend/src/mcp/server.py
- [x] T005 [P] Create tools module structure with helper functions in backend/src/mcp/tools.py
- [x] T006 [P] Implement error handling utilities for task-not-found and validation errors in backend/src/mcp/tools.py
- [x] T007 Configure MCP server to use existing database.py session management in backend/src/mcp/server.py

**Checkpoint**: Foundation ready - MCP server can start and connect to database, tool implementation can now begin

---

## Phase 3: User Story 1 - Add New Task via MCP (Priority: P1) 🎯 MVP

**Goal**: AI assistant can create new tasks by calling add_task MCP tool with user_id and title

**Independent Test**: Call add_task with a user_id and title, verify task appears in database with completed=False and proper timestamps

### Implementation for User Story 1

- [x] T008 [US1] Implement add_task tool accepting user_id, title, optional description in backend/src/mcp/tools.py
- [x] T009 [US1] Add input validation for required parameters (user_id, title) in add_task tool
- [x] T010 [US1] Register add_task tool with MCP server in backend/src/mcp/server.py
- [x] T011 [US1] Add error response for invalid user_id in add_task tool

**Checkpoint**: User Story 1 complete - AI assistants can create tasks via MCP

---

## Phase 4: User Story 2 - List User Tasks via MCP (Priority: P1)

**Goal**: AI assistant can retrieve all tasks for a user by calling list_tasks MCP tool

**Independent Test**: Call list_tasks with a user_id, verify all tasks for that user are returned in structured format

### Implementation for User Story 2

- [x] T012 [US2] Implement list_tasks tool accepting user_id in backend/src/mcp/tools.py
- [x] T013 [US2] Add query to fetch all tasks for specified user_id with proper filtering
- [x] T014 [US2] Register list_tasks tool with MCP server in backend/src/mcp/server.py
- [x] T015 [US2] Return empty list response when user has no tasks

**Checkpoint**: User Stories 1 AND 2 complete - AI assistants can create and list tasks via MCP

---

## Phase 5: User Story 3 - Complete Task via MCP (Priority: P2)

**Goal**: AI assistant can mark a task as completed by calling complete_task MCP tool

**Independent Test**: Call complete_task with user_id and task_id, verify task completed status updates to true

### Implementation for User Story 3

- [x] T016 [US3] Implement complete_task tool accepting user_id, task_id in backend/src/mcp/tools.py
- [x] T017 [US3] Add task ownership validation (task belongs to specified user_id)
- [x] T018 [US3] Update task completed status and updated_at timestamp in database
- [x] T019 [US3] Register complete_task tool with MCP server in backend/src/mcp/server.py
- [x] T020 [US3] Add error response for task-not-found scenario

**Checkpoint**: User Stories 1, 2, AND 3 complete - AI assistants can create, list, and complete tasks

---

## Phase 6: User Story 4 - Update Task Details via MCP (Priority: P3)

**Goal**: AI assistant can modify task title/description by calling update_task MCP tool

**Independent Test**: Call update_task with user_id, task_id, and updated fields, verify only specified fields change

### Implementation for User Story 4

- [x] T021 [US4] Implement update_task tool accepting user_id, task_id, optional title, optional description in backend/src/mcp/tools.py
- [x] T022 [US4] Add partial update logic to modify only provided fields
- [x] T023 [US4] Add task ownership validation (task belongs to specified user_id)
- [x] T024 [US4] Register update_task tool with MCP server in backend/src/mcp/server.py
- [x] T025 [US4] Add error response for task-not-found scenario

**Checkpoint**: User Stories 1-4 complete - Full CRUD except delete available via MCP

---

## Phase 7: User Story 5 - Delete Task via MCP (Priority: P3)

**Goal**: AI assistant can permanently remove a task by calling delete_task MCP tool

**Independent Test**: Call delete_task with user_id and task_id, verify task is removed from database

### Implementation for User Story 5

- [x] T026 [US5] Implement delete_task tool accepting user_id, task_id in backend/src/mcp/tools.py
- [x] T027 [US5] Add task ownership validation (task belongs to specified user_id)
- [x] T028 [US5] Register delete_task tool with MCP server in backend/src/mcp/server.py
- [x] T029 [US5] Add error response for task-not-found scenario

**Checkpoint**: All user stories complete - Full CRUD operations available via MCP

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T030 [P] Add MCP server startup entry point in backend/src/mcp/__init__.py
- [x] T031 [P] Verify all 5 tools are accessible via MCP server inspection
- [x] T032 Validate response times <2 seconds for all tools per SC-003
- [x] T033 Manual end-to-end test of complete task lifecycle (create → list → update → complete → delete)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority - can proceed in parallel
  - US3 (P2) can start after Foundational - independent
  - US4 and US5 (P3) can start after Foundational - independent
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational - Requires task to exist (depends on US1 for testing)
- **User Story 4 (P3)**: Can start after Foundational - Requires task to exist (depends on US1 for testing)
- **User Story 5 (P3)**: Can start after Foundational - Requires task to exist (depends on US1 for testing)

### Within Each User Story

- Implement tool logic first
- Add validation and error handling
- Register tool with MCP server
- Verify independently

### Parallel Opportunities

- T002, T003 can run in parallel (Setup phase)
- T005, T006 can run in parallel (Foundational phase)
- Once Foundational is complete, US1 and US2 can proceed in parallel
- T030, T031 can run in parallel (Polish phase)

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational tasks in parallel:
Task: "Create tools module structure with helper functions in backend/src/mcp/tools.py"
Task: "Implement error handling utilities for task-not-found and validation errors in backend/src/mcp/tools.py"
```

## Parallel Example: User Stories 1 & 2

```bash
# Both P1 stories can start after Foundational:
Task: "Implement add_task tool in backend/src/mcp/tools.py"
Task: "Implement list_tasks tool in backend/src/mcp/tools.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (add_task)
4. Complete Phase 4: User Story 2 (list_tasks)
5. **STOP and VALIDATE**: Test add/list cycle independently
6. Deploy/demo if ready - users can create and view tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test independently → Deploy/Demo (complete tasks)
4. Add User Story 4 + 5 → Test independently → Deploy/Demo (full CRUD)
5. Each story adds value without breaking previous stories

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 33 |
| Setup Tasks | 3 |
| Foundational Tasks | 4 |
| US1 Tasks (add_task) | 4 |
| US2 Tasks (list_tasks) | 4 |
| US3 Tasks (complete_task) | 5 |
| US4 Tasks (update_task) | 5 |
| US5 Tasks (delete_task) | 4 |
| Polish Tasks | 4 |
| Parallel Opportunities | 8 tasks marked [P] |
| MVP Scope | US1 + US2 (8 tasks after foundational) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tools must be stateless per FR-010
- User data isolation required per FR-002
