# Implementation Plan: Database Models

**Branch**: `002-database-models` | **Date**: 2026-01-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-database-models/spec.md`

## Summary

Define and implement SQLModel models for Task, Conversation, and Message entities with proper relationships, automatic timestamps, and cascade delete behavior. Create database tables in Neon PostgreSQL and verify basic CRUD operations work correctly.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: SQLModel, psycopg (existing from 001-project-setup)
**Storage**: Neon Serverless PostgreSQL via DATABASE_URL
**Testing**: pytest (manual verification for this phase)
**Target Platform**: Linux/Windows/macOS development, Linux server deployment
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: CRUD operations <100ms (per spec SC-002)
**Constraints**: Tables created <30s, cascade delete <1s for 100 messages (per spec)
**Scale/Scope**: Development environment, single developer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. MCP-Compliant Architecture | N/A | No MCP tools in this phase (models only) |
| II. Database as Single Source of Truth | PASS | All entities persisted to Neon PostgreSQL via SQLModel |
| III. Stateless Agent Design | N/A | No agents in this phase |
| IV. Tool-Driven Operations | N/A | No tool operations in this phase |
| V. AI Behavior Constraints | N/A | No AI in this phase |
| VI. Security and Authentication | PARTIAL | user_id field present but auth out of scope |

**Gate Result**: PASS - All applicable principles satisfied. Models establish the data layer for future MCP tools.

## Project Structure

### Documentation (this feature)

```text
specs/002-database-models/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── config.py        # Existing from 001-project-setup
│   ├── database.py      # Existing - will add create_tables()
│   ├── main.py          # Existing from 001-project-setup
│   └── models/          # NEW: Model definitions
│       ├── __init__.py
│       ├── task.py      # Task model
│       ├── conversation.py  # Conversation model
│       └── message.py   # Message model
└── tests/
    ├── __init__.py
    └── test_models.py   # NEW: Model tests (optional)
```

**Structure Decision**: Web application structure (backend/) matching 001-project-setup. Models organized in dedicated `models/` package for clean separation.

## Implementation Steps

Based on user input:

1. **Define SQLModel models**: Task, Conversation, Message in `backend/src/models/`
2. **Add relationships**: One-to-many between Conversation and Message with cascade delete
3. **Create migration function**: Add `create_tables()` to database.py using SQLModel.metadata.create_all()
4. **Apply migrations**: Run table creation on Neon PostgreSQL at startup
5. **Verify table creation**: Check tables exist in database
6. **Test CRUD operations**: Manual verification script or interactive testing

## Complexity Tracking

> No violations to justify - all constitution principles either satisfied or N/A per spec scope.
