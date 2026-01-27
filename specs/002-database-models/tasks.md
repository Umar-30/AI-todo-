# Tasks: Database Models

**Input**: Design documents from `/specs/002-database-models/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in specification. Test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Models**: `backend/src/models/`
- **Database**: `backend/src/database.py`
- Paths based on plan.md structure

---

## Phase 1: Setup

**Purpose**: Initialize models package structure

- [x] T001 Create models package directory `backend/src/models/`
- [x] T002 [P] Create `backend/src/models/__init__.py` with model exports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `create_tables()` function to `backend/src/database.py`:
  - Import SQLModel.metadata.create_all
  - Create function that creates all tables from registered models
  - Add logging for table creation status
- [x] T004 Update `backend/src/main.py` lifespan to call `create_tables()` on startup

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Task Data Persistence (Priority: P1)

**Goal**: System can store, retrieve, update, and delete Task entities

**Independent Test**: Task CRUD operations work correctly via Python REPL or script

### Implementation for User Story 1

- [x] T005 [US1] Create `backend/src/models/task.py` with Task model:
  - UUID primary key (id) with default uuid4
  - user_id: string, required, indexed
  - title: string, required, max 255 chars
  - description: string, optional, nullable
  - completed: boolean, default=False
  - created_at: datetime, auto-set on create (UTC)
  - updated_at: datetime, auto-update on modify (UTC)
- [x] T006 [US1] Export Task model from `backend/src/models/__init__.py`
- [x] T007 [US1] Verify Task table creation by starting server and checking database

**Checkpoint**: User Story 1 complete - Task CRUD operations work

---

## Phase 4: User Story 2 - Conversation History Persistence (Priority: P2)

**Goal**: System can store conversations and messages with proper relationships

**Independent Test**: Conversation with messages can be created and retrieved in order

### Implementation for User Story 2

- [x] T008 [P] [US2] Create `backend/src/models/conversation.py` with Conversation model:
  - UUID primary key (id) with default uuid4
  - user_id: string, required, indexed
  - created_at: datetime, auto-set on create (UTC)
  - updated_at: datetime, auto-update on modify (UTC)
  - messages: Relationship to Message (back_populates)
- [x] T009 [P] [US2] Create `backend/src/models/message.py` with Message model:
  - UUID primary key (id) with default uuid4
  - user_id: string, required
  - conversation_id: UUID, foreign key to conversations.id, required
  - role: string, required (validate: "user" or "assistant")
  - content: text, required
  - created_at: datetime, auto-set on create (UTC)
  - conversation: Relationship to Conversation (back_populates)
- [x] T010 [US2] Export Conversation and Message models from `backend/src/models/__init__.py`
- [x] T011 [US2] Verify Conversation and Message tables creation

**Checkpoint**: User Story 2 complete - Conversation and Message CRUD work

---

## Phase 5: User Story 3 - Data Integrity and Relationships (Priority: P3)

**Goal**: Foreign key constraints and cascade delete are enforced

**Independent Test**: Deleting a Conversation automatically deletes all its Messages

### Implementation for User Story 3

- [x] T012 [US3] Configure cascade delete on Conversation → Message relationship in `backend/src/models/conversation.py`:
  - Add sa_relationship_kwargs={"cascade": "all, delete-orphan"}
  - Ensure orphan messages cannot exist
- [x] T013 [US3] Add foreign key constraint with ON DELETE CASCADE in `backend/src/models/message.py`:
  - Configure sa_column for conversation_id with ondelete="CASCADE"
- [x] T014 [US3] Test cascade delete: create conversation with messages, delete conversation, verify messages deleted

**Checkpoint**: User Story 3 complete - Data integrity enforced

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation

- [x] T015 Verify all three tables exist in Neon PostgreSQL
- [x] T016 Verify SC-001: Tables created within 30 seconds of migration
- [x] T017 Verify SC-003: Foreign key constraints enforced (try creating orphan message)
- [x] T018 Run quickstart.md validation: complete CRUD test for all entities

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Can run independently
- **User Story 2 (Phase 4)**: Depends on Foundational - Can run in parallel with US1
- **User Story 3 (Phase 5)**: Depends on US1 and US2 (needs models from both)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - only needs Foundational phase
- **User Story 2 (P2)**: Independent - only needs Foundational phase
- **User Story 3 (P3)**: Depends on US1 and US2 (configures relationships between existing models)

### Within Each User Story

- Model file → Export in __init__.py → Verify table creation

### Parallel Opportunities

Phase 1:
- T001, T002 sequential (directory before __init__.py)

Phase 3 & 4 (after Foundational):
- T005-T007 (US1) can run in parallel with T008-T011 (US2)
- Within US2: T008 and T009 can run in parallel (different model files)

---

## Parallel Example: User Stories 1 & 2

```bash
# After Foundational phase, launch in parallel:
# Stream 1 (US1):
Task: "Create Task model in backend/src/models/task.py"
Task: "Export Task from __init__.py"

# Stream 2 (US2):
Task: "Create Conversation model in backend/src/models/conversation.py"
Task: "Create Message model in backend/src/models/message.py"
Task: "Export Conversation and Message from __init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Task model)
4. **STOP and VALIDATE**: Create/read/update/delete a Task
5. Task persists correctly = MVP achieved

### Incremental Delivery

1. Complete Setup + Foundational → Models package ready
2. Add User Story 1 → Task CRUD works (MVP!)
3. Add User Story 2 → Conversation/Message CRUD works
4. Add User Story 3 → Relationships and cascade delete enforced
5. Polish phase → All success criteria verified

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US2 can be implemented in parallel after Foundational
- US3 requires both US1 and US2 complete (relationship configuration)
- No test tasks generated (not explicitly requested in spec)
- Models use UUID primary keys per research.md decision
