# Tasks: Project Setup

**Input**: Design documents from `/specs/001-project-setup/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification. Test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` (placeholder only)
- Paths based on plan.md structure

---

## Phase 1: Setup

**Purpose**: Project initialization and directory structure

- [x] T001 Create monorepo directory structure: `/frontend`, `/backend`, `/specs`
- [x] T002 Create frontend placeholder with `frontend/.gitkeep`
- [x] T003 [P] Create backend directory structure: `backend/src/`, `backend/tests/`
- [x] T004 [P] Create `backend/src/__init__.py` package marker
- [x] T005 [P] Create `backend/tests/__init__.py` package marker

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create `backend/pyproject.toml` with project metadata (name, version, Python 3.11+)
- [x] T007 Create `backend/requirements.txt` with pinned dependencies:
  - fastapi>=0.109.0
  - sqlmodel>=0.0.14
  - psycopg[binary]>=3.1.0
  - python-dotenv>=1.0.0
  - uvicorn[standard]>=0.27.0
  - pytest>=8.0.0
  - httpx>=0.26.0
- [x] T008 [P] Add `.gitignore` entries for Python/venv: `.venv/`, `__pycache__/`, `.env`, `*.pyc`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Developer Project Initialization (Priority: P1)

**Goal**: Developer can clone repo, set up environment, and start the backend server

**Independent Test**: Server starts without errors and displays ready status within 5 seconds

### Implementation for User Story 1

- [x] T009 [US1] Create `backend/src/config.py` with Settings class:
  - Load DATABASE_URL from environment (required)
  - Load OPENAI_API_KEY from environment (required)
  - Fail fast with clear error if missing
- [x] T010 [US1] Create `backend/src/database.py` with database connection:
  - Create SQLModel engine with postgresql+psycopg:// driver
  - Enable SSL mode for Neon connections
  - Implement get_engine() function
  - Implement check_connection() function returning bool
- [x] T011 [US1] Create `backend/src/main.py` with FastAPI application:
  - Import FastAPI and create app instance
  - Implement lifespan context manager for startup/shutdown
  - Connect to database on startup, log connection status
  - Close database connection on shutdown
- [x] T012 [US1] Add HealthStatus response model to `backend/src/main.py`:
  - Fields: status, server, database, timestamp (per data-model.md)
  - Use Pydantic BaseModel with enum constraints
- [x] T013 [US1] Implement GET /health endpoint in `backend/src/main.py`:
  - Return 200 with status="healthy" when DB connected
  - Return 503 with status="unhealthy" when DB disconnected
  - Include timestamp in ISO 8601 format (per contracts/health.yaml)

**Checkpoint**: User Story 1 complete - server starts and health check works

---

## Phase 4: User Story 2 - Environment Configuration (Priority: P2)

**Goal**: Developer can configure environment variables securely without exposing credentials

**Independent Test**: Developer copies .env.example, fills credentials, app reads values correctly

### Implementation for User Story 2

- [x] T014 [US2] Create `backend/.env.example` template:
  - DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
  - OPENAI_API_KEY=sk-your-api-key-here
  - Include comments explaining each variable
- [x] T015 [US2] Update `backend/src/config.py` to use python-dotenv:
  - Load .env file if present (for local development)
  - Validate DATABASE_URL format (starts with postgresql:// or postgres://)
  - Log config loaded (without sensitive values)
- [x] T016 [US2] Add missing environment variable error handling to `backend/src/config.py`:
  - Raise descriptive error if DATABASE_URL missing
  - Raise descriptive error if OPENAI_API_KEY missing
  - Include troubleshooting hints in error messages

**Checkpoint**: User Story 2 complete - environment configuration works securely

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification and cleanup

- [x] T017 Verify server startup meets SC-002: starts within 5 seconds
- [x] T018 Verify database connection meets SC-003: connects within 10 seconds
- [x] T019 Verify no credentials in version control (SC-004): .env in .gitignore
- [x] T020 Run quickstart.md validation: follow steps, confirm all work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 (config.py must exist)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (extends config.py created in US1)

### Within Each User Story

- config.py before database.py (config needed for connection string)
- database.py before main.py (database needed for health check)
- Response model before endpoint (model needed for return type)

### Parallel Opportunities

Phase 1:
- T003, T004, T005 can run in parallel (different directories)

Phase 2:
- T008 can run in parallel with T006, T007 (different files)

---

## Parallel Example: Phase 1 Setup

```bash
# Launch in parallel:
Task: "Create backend directory structure: backend/src/, backend/tests/"
Task: "Create backend/src/__init__.py package marker"
Task: "Create backend/tests/__init__.py package marker"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Start server, hit /health endpoint
5. Server responds with healthy status = MVP achieved

### Incremental Delivery

1. Complete Setup + Foundational → Project structure ready
2. Add User Story 1 → Server starts, health check works (MVP!)
3. Add User Story 2 → Environment configuration polished
4. Polish phase → All success criteria verified

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No test tasks generated (not explicitly requested in spec)
