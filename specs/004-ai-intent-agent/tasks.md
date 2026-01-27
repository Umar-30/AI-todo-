# Tasks: AI Intent Agent

**Input**: Design documents from `/specs/004-ai-intent-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in spec - manual verification approach per plan.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/` for source code
- **Agent module**: `backend/src/agent/` for AI agent components

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Agent module initialization and OpenAI Agents SDK setup

- [x] T001 Create agent module directory structure at backend/src/agent/
- [x] T002 Create __init__.py with module exports in backend/src/agent/__init__.py
- [x] T003 Install OpenAI Agents SDK dependency in backend/pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core agent infrastructure that MUST be complete before ANY intent handling can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create system prompt with role definition and behavior rules in backend/src/agent/prompts.py
- [x] T005 [P] Create response formatting utilities in backend/src/agent/utils.py
- [x] T006 [P] Create base agent configuration with OpenAI Agents SDK in backend/src/agent/task_agent.py
- [x] T007 Wrap add_task MCP tool as function_tool in backend/src/agent/task_agent.py
- [x] T008 Wrap list_tasks MCP tool as function_tool in backend/src/agent/task_agent.py
- [x] T009 Wrap complete_task MCP tool as function_tool in backend/src/agent/task_agent.py
- [x] T010 Wrap update_task MCP tool as function_tool in backend/src/agent/task_agent.py
- [x] T011 Wrap delete_task MCP tool as function_tool in backend/src/agent/task_agent.py
- [x] T012 Register all 5 function tools with the agent in backend/src/agent/task_agent.py

**Checkpoint**: Foundation ready - Agent can be instantiated with all MCP tools attached

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: AI assistant can create tasks when user says "add" or "remember"

**Independent Test**: Send "add buy milk" and verify agent calls add_task with correct title

### Implementation for User Story 1

- [x] T013 [US1] Add intent mapping for "add" and "remember" keywords in backend/src/agent/prompts.py
- [x] T014 [US1] Add parameter extraction guidance for title from natural language in backend/src/agent/prompts.py
- [x] T015 [US1] Add confirmation response template for task creation in backend/src/agent/prompts.py
- [x] T016 [US1] Add error response for add_task failures in backend/src/agent/prompts.py

**Checkpoint**: User Story 1 complete - Agent maps add/remember intents to add_task tool

---

## Phase 4: User Story 2 - List Tasks via Natural Language (Priority: P1)

**Goal**: AI assistant can show tasks when user says "list" or "show"

**Independent Test**: Send "show my tasks" and verify agent calls list_tasks and formats results

### Implementation for User Story 2

- [x] T017 [US2] Add intent mapping for "list" and "show" keywords in backend/src/agent/prompts.py
- [x] T018 [US2] Add response formatting for task list display in backend/src/agent/prompts.py
- [x] T019 [US2] Add empty list response handling in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1 AND 2 complete - Agent can add and list tasks

---

## Phase 5: User Story 3 - Complete Task via Natural Language (Priority: P2)

**Goal**: AI assistant can mark tasks complete when user says "done" or "complete"

**Independent Test**: Send "done with buy milk" and verify agent calls complete_task for matching task

### Implementation for User Story 3

- [x] T020 [US3] Add intent mapping for "done" and "complete" keywords in backend/src/agent/prompts.py
- [x] T021 [US3] Add task identification guidance for matching user references in backend/src/agent/prompts.py
- [x] T022 [US3] Add confirmation response for task completion in backend/src/agent/prompts.py
- [x] T023 [US3] Add task-not-found error handling for complete intent in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - Agent can add, list, and complete tasks

---

## Phase 6: User Story 4 - Delete Task via Natural Language (Priority: P3)

**Goal**: AI assistant can remove tasks when user says "delete" or "remove"

**Independent Test**: Send "delete buy groceries" and verify agent calls delete_task

### Implementation for User Story 4

- [x] T024 [US4] Add intent mapping for "delete" and "remove" keywords in backend/src/agent/prompts.py
- [x] T025 [US4] Add confirmation response for task deletion in backend/src/agent/prompts.py
- [x] T026 [US4] Add task-not-found error handling for delete intent in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1-4 complete - Full lifecycle except update

---

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P3)

**Goal**: AI assistant can modify tasks when user says "change" or "update"

**Independent Test**: Send "change buy milk to buy oat milk" and verify agent calls update_task

### Implementation for User Story 5

- [x] T027 [US5] Add intent mapping for "change" and "update" keywords in backend/src/agent/prompts.py
- [x] T028 [US5] Add parameter extraction for old title and new values in backend/src/agent/prompts.py
- [x] T029 [US5] Add confirmation response for task update in backend/src/agent/prompts.py
- [x] T030 [US5] Add task-not-found error handling for update intent in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1-5 complete - Full CRUD operations via natural language

---

## Phase 8: User Story 6 - Tool Chaining for Complex Requests (Priority: P3)

**Goal**: AI assistant can chain multiple tool calls for requests like "add X and show my list"

**Independent Test**: Send "add buy milk and show my tasks" and verify agent calls both tools

### Implementation for User Story 6

- [x] T031 [US6] Add multi-intent recognition guidance in backend/src/agent/prompts.py
- [x] T032 [US6] Add tool chaining behavior rules in backend/src/agent/prompts.py
- [x] T033 [US6] Add combined response formatting for chained operations in backend/src/agent/prompts.py

**Checkpoint**: All user stories complete - Agent handles single and chained tool calls

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T034 Add clarification behavior for ambiguous intents in backend/src/agent/prompts.py
- [x] T035 Add conversational fallback for non-task messages in backend/src/agent/prompts.py
- [x] T036 [P] Add agent factory function for easy instantiation in backend/src/agent/__init__.py
- [x] T037 [P] Validate all intent-to-tool mappings per quickstart.md scenarios
- [x] T038 Manual end-to-end test of complete agent workflow (add → list → complete → delete)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority - can proceed in parallel
  - US3 (P2) can start after Foundational - independent
  - US4, US5, US6 (P3) can start after Foundational - independent
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational - Independent (but testing requires tasks to exist)
- **User Story 4 (P3)**: Can start after Foundational - Independent (but testing requires tasks to exist)
- **User Story 5 (P3)**: Can start after Foundational - Independent (but testing requires tasks to exist)
- **User Story 6 (P3)**: Can start after Foundational - Builds on US1-US5 tools being wrapped

### Within Each User Story

- Add intent mapping to prompts.py
- Add parameter extraction guidance
- Add response templates
- Add error handling
- Story complete before moving to next priority

### Parallel Opportunities

- T005, T006 can run in parallel (Foundational phase - different concerns)
- T007, T008, T009, T010, T011 can run in parallel (wrapping different MCP tools)
- Once Foundational is complete, US1 and US2 can proceed in parallel
- T036, T037 can run in parallel (Polish phase)

---

## Parallel Example: Foundational Phase

```bash
# Launch tool wrapping tasks in parallel:
Task: "Wrap add_task MCP tool as function_tool in backend/src/agent/task_agent.py"
Task: "Wrap list_tasks MCP tool as function_tool in backend/src/agent/task_agent.py"
Task: "Wrap complete_task MCP tool as function_tool in backend/src/agent/task_agent.py"
Task: "Wrap update_task MCP tool as function_tool in backend/src/agent/task_agent.py"
Task: "Wrap delete_task MCP tool as function_tool in backend/src/agent/task_agent.py"
```

## Parallel Example: User Stories 1 & 2

```bash
# Both P1 stories can start after Foundational:
Task: "Add intent mapping for 'add' and 'remember' keywords in backend/src/agent/prompts.py"
Task: "Add intent mapping for 'list' and 'show' keywords in backend/src/agent/prompts.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (add intent)
4. Complete Phase 4: User Story 2 (list intent)
5. **STOP and VALIDATE**: Test add/list cycle independently
6. Deploy/demo if ready - users can create and view tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test independently → Deploy/Demo (complete tasks)
4. Add User Story 4 + 5 → Test independently → Deploy/Demo (delete + update)
5. Add User Story 6 → Test independently → Deploy/Demo (tool chaining)
6. Each story adds value without breaking previous stories

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 38 |
| Setup Tasks | 3 |
| Foundational Tasks | 9 |
| US1 Tasks (add intent) | 4 |
| US2 Tasks (list intent) | 3 |
| US3 Tasks (complete intent) | 4 |
| US4 Tasks (delete intent) | 3 |
| US5 Tasks (update intent) | 4 |
| US6 Tasks (tool chaining) | 3 |
| Polish Tasks | 5 |
| Parallel Opportunities | 12 tasks marked [P] or parallelizable |
| MVP Scope | US1 + US2 (7 tasks after foundational) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All intent mappings defined in prompts.py (single source of truth for agent behavior)
- Tool wrappers call existing MCP tools from backend/src/mcp/tools.py
- Agent must remain stateless per Constitution III
- All task operations via MCP tools only per Constitution IV
