# Implementation Plan: MCP Task Tools

**Branch**: `003-mcp-task-tools` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-mcp-task-tools/spec.md`

## Summary

Implement an MCP server that exposes stateless task operations for AI assistants. The server will provide 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) that read/write directly to the database with proper user isolation and error handling.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Official MCP SDK, SQLModel, existing database models from 002-database-models
**Storage**: Neon PostgreSQL via DATABASE_URL (existing from 001-project-setup)
**Testing**: pytest (manual verification for this phase)
**Target Platform**: Linux/Windows/macOS development, Linux server deployment
**Project Type**: Backend service for AI assistant integration
**Performance Goals**: Tool responses <2 seconds (per spec SC-003)
**Constraints**: User data isolation, stateless operations (per spec FR-010), graceful error handling (per spec FR-009)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. MCP-Compliant Architecture | PASS | MCP server design aligns with MCP SDK requirements |
| II. Database as Single Source of Truth | PASS | Tools read/write directly to database per spec FR-008 |
| III. Stateless Agent Design | PASS | All operations are stateless per spec FR-010 |
| IV. Tool-Driven Operations | PASS | MCP tools enable AI assistant operations per spec FR-001 |
| V. AI Behavior Constraints | N/A | No AI implementation in this phase |
| VI. Security and Authentication | PARTIAL | user_id validation present but auth out of scope |

**Gate Result**: PASS - All applicable principles satisfied. MCP tools provide stateless access to database operations.

## Project Structure

### Documentation (this feature)

```text
specs/003-mcp-task-tools/
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
│   ├── database.py      # Existing from 002-database-models
│   ├── main.py          # Existing from 001-project-setup
│   ├── models/          # Existing from 002-database-models
│   │   ├── __init__.py
│   │   ├── task.py      # Existing from 002-database-models
│   │   ├── conversation.py  # Existing from 002-database-models
│   │   └── message.py   # Existing from 002-database-models
│   └── mcp/             # NEW: MCP server and tools
│       ├── __init__.py
│       ├── server.py    # MCP server initialization
│       └── tools.py     # Task operation tools
└── tests/
    ├── __init__.py
    └── test_mcp_tools.py # NEW: MCP tool tests
```

**Structure Decision**: Web application structure (backend/) matching 001-project-setup. MCP components organized in dedicated `mcp/` package for clean separation from other concerns.

## Implementation Steps

Based on user input:

1. **Initialize MCP server**: Set up MCP server using Official MCP SDK in `backend/src/mcp/server.py`
2. **Implement add_task tool**: Create tool that accepts user_id, title, description and adds to database
3. **Implement list_tasks tool**: Create tool that accepts user_id and returns all user's tasks
4. **Implement complete_task tool**: Create tool that accepts user_id, task_id and marks as completed
5. **Implement delete_task tool**: Create tool that accepts user_id, task_id and deletes from database
6. **Implement update_task tool**: Create tool that accepts user_id, task_id and optional fields to update
7. **Add structured error handling**: Implement proper error responses for missing tasks and validation
8. **Test each tool**: Verify each tool works independently with database operations

## Complexity Tracking

> No violations to justify - all constitution principles either satisfied or N/A per spec scope.