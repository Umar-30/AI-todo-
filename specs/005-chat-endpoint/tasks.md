# Tasks: Stateless Chat Endpoint

**Input**: Design documents from `/specs/005-chat-endpoint/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/chat.yaml, quickstart.md

**Tests**: Not explicitly requested in spec - manual verification approach per quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/` for source code
- **API module**: `backend/src/api/` for API endpoint components

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: API module initialization and FastAPI router setup

- [x] T001 Create api module directory structure at backend/src/api/
- [x] T002 Create __init__.py with module exports in backend/src/api/__init__.py
- [x] T003 [P] Create API schemas (ChatRequest, ChatResponse, ToolCallInfo) in backend/src/api/schemas.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core chat infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create conversation service with DB operations in backend/src/api/services.py
- [x] T005 [P] Add get_conversation_with_messages function in backend/src/api/services.py
- [x] T006 [P] Add create_conversation function in backend/src/api/services.py
- [x] T007 [P] Add create_message function in backend/src/api/services.py
- [x] T008 Create chat router with POST /api/{user_id}/chat endpoint in backend/src/api/chat.py
- [x] T009 Register chat router in FastAPI app in backend/src/main.py

**Checkpoint**: Foundation ready - Chat endpoint registered, conversation service available

---

## Phase 3: User Story 1 - Start New Conversation (Priority: P1) 🎯 MVP

**Goal**: Client can send a message without conversation_id and receive a new conversation with agent response

**Independent Test**: Send POST without conversation_id and verify new conversation created with response

### Implementation for User Story 1

- [x] T010 [US1] Implement new conversation creation flow in chat endpoint in backend/src/api/chat.py
- [x] T011 [US1] Store user message to database before agent processing in backend/src/api/chat.py
- [x] T012 [US1] Integrate TaskAgent execution with user message in backend/src/api/chat.py
- [x] T013 [US1] Store assistant response to database after agent processing in backend/src/api/chat.py
- [x] T014 [US1] Return ChatResponse with new conversation_id, response, and tool_calls in backend/src/api/chat.py

**Checkpoint**: User Story 1 complete - New conversations work end-to-end

---

## Phase 4: User Story 2 - Continue Existing Conversation (Priority: P1)

**Goal**: Client can send a message with conversation_id and receive response with conversation context

**Independent Test**: Create conversation, then send follow-up with conversation_id and verify context maintained

### Implementation for User Story 2

- [x] T015 [US2] Implement conversation loading by ID in chat endpoint in backend/src/api/chat.py
- [x] T016 [US2] Load message history from database for existing conversation in backend/src/api/chat.py
- [x] T017 [US2] Pass conversation history as context to TaskAgent in backend/src/api/chat.py
- [x] T018 [US2] Add conversation ownership validation (user_id matches) in backend/src/api/chat.py

**Checkpoint**: User Stories 1 AND 2 complete - New and existing conversations work

---

## Phase 5: User Story 3 - Conversation Persistence Across Restarts (Priority: P2)

**Goal**: Conversations persist in database and remain accessible after server restarts

**Independent Test**: Create conversation, restart server, continue conversation and verify history intact

### Implementation for User Story 3

- [x] T019 [US3] Verify stateless design - no in-memory conversation state in backend/src/api/chat.py
- [x] T020 [US3] Ensure all conversation state loaded fresh from database per request in backend/src/api/services.py
- [x] T021 [US3] Add conversation updated_at timestamp update on new messages in backend/src/api/services.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - Full stateless persistence verified

---

## Phase 6: User Story 4 - Agent Tool Execution and Response (Priority: P2)

**Goal**: System executes MCP tools and returns tool_calls information in response

**Independent Test**: Send "add buy milk" and verify tool_calls array contains add_task in response

### Implementation for User Story 4

- [x] T022 [US4] Extend TaskAgent.run() to return tool calls alongside response in backend/src/agent/task_agent.py
- [x] T023 [US4] Capture tool call information (name, arguments, result) during agent execution in backend/src/api/chat.py
- [x] T024 [US4] Populate tool_calls array in ChatResponse in backend/src/api/chat.py
- [x] T025 [US4] Handle tool chaining - capture multiple tool calls in order in backend/src/api/chat.py

**Checkpoint**: All user stories complete - Full chat functionality with tool reporting

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, validation, and final improvements

- [x] T026 Add empty message validation with 400 response in backend/src/api/chat.py
- [x] T027 Add conversation not found error handling with 404 response in backend/src/api/chat.py
- [x] T028 Add access denied error handling with 403 response in backend/src/api/chat.py
- [x] T029 Add agent processing error handling with 500 response in backend/src/api/chat.py
- [x] T030 [P] Add logging for chat operations in backend/src/api/chat.py
- [x] T031 [P] Validate all error responses match contracts/chat.yaml specification
- [x] T032 Manual end-to-end test using quickstart.md scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority - implement US1 first as it's the foundation
  - US3 and US4 are both P2 priority - can proceed after US1+US2
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 being complete (needs conversation to exist to continue it)
- **User Story 3 (P2)**: Can start after US1+US2 - Validates persistence behavior
- **User Story 4 (P2)**: Can start after Foundational - Independent (but best after US1 for testing)

### Within Each User Story

- Service functions before endpoint logic
- Database operations before agent integration
- Core flow before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- T003 can run in parallel with other Setup tasks (different file)
- T005, T006, T007 can run in parallel (same file but independent functions)
- T030, T031 can run in parallel (Polish phase)

---

## Parallel Example: Foundational Phase

```bash
# Launch service function tasks in parallel:
Task: "Add get_conversation_with_messages function in backend/src/api/services.py"
Task: "Add create_conversation function in backend/src/api/services.py"
Task: "Add create_message function in backend/src/api/services.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (new conversation flow)
4. **STOP and VALIDATE**: Test with `curl -X POST /api/user-123/chat -d '{"message": "add buy milk"}'`
5. Deploy/demo if ready - basic chat works

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (conversation continuity)
4. Add User Story 3 → Test independently → Deploy/Demo (persistence verified)
5. Add User Story 4 → Test independently → Deploy/Demo (tool reporting)
6. Add Polish → Final validation → Production ready

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 32 |
| Setup Tasks | 3 |
| Foundational Tasks | 6 |
| US1 Tasks (new conversation) | 5 |
| US2 Tasks (continue conversation) | 4 |
| US3 Tasks (persistence) | 3 |
| US4 Tasks (tool reporting) | 4 |
| Polish Tasks | 7 |
| Parallel Opportunities | 8 tasks marked [P] or parallelizable |
| MVP Scope | US1 (5 tasks after foundational) |

---

## Notes

- [P] tasks = different files or independent functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Existing models (Conversation, Message) from feature 002 - no schema changes needed
- TaskAgent from feature 004 - minor extension for tool call capture
- All conversation state via database - no in-memory state per Constitution III
