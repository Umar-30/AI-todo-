# Implementation Plan: Stateless Chat Endpoint

**Branch**: `005-chat-endpoint` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-chat-endpoint/spec.md`

## Summary

Implement a stateless chat API endpoint (`POST /api/{user_id}/chat`) that handles conversation management with database persistence. The endpoint creates/loads conversations, stores messages, runs the AI agent with conversation history context, executes MCP tools, and returns the agent's response along with tool call information. All state is persisted to the database to survive server restarts.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, SQLModel, Pydantic
**Storage**: Neon Serverless PostgreSQL (via SQLModel ORM)
**Testing**: pytest with httpx for async API testing
**Target Platform**: Linux/Windows/macOS development, Linux server deployment
**Project Type**: Web application (backend API)
**Performance Goals**: Response within 5 seconds per spec SC-001
**Constraints**: Stateless (no in-memory conversation state), Database as single source of truth
**Scale/Scope**: 100 concurrent chat requests per spec SC-005

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. MCP-Compliant Architecture | PASS | All task operations flow through MCP tools via TaskAgent |
| II. Database as Single Source of Truth | PASS | Conversations and messages persisted to PostgreSQL, no in-memory state |
| III. Stateless Agent Design | PASS | Each request loads conversation from DB, agent is stateless |
| IV. Tool-Driven Operations | PASS | Agent uses MCP tools (add_task, list_tasks, etc.) for all task operations |
| V. AI Behavior Constraints | PASS | Agent translates intent to tools, confirms actions per prompts.py |
| VI. Security and Authentication | PARTIAL | user_id from path, validation that conversation belongs to user; full auth out of scope per spec |

**Gate Result**: PASS - All applicable principles satisfied. Full authentication deferred per spec assumptions.

## Project Structure

### Documentation (this feature)

```text
specs/005-chat-endpoint/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat.yaml        # OpenAPI contract for chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── config.py           # Existing from 001-project-setup
│   ├── database.py         # Existing from 001-project-setup
│   ├── main.py             # Existing - will add chat router
│   ├── models/             # Existing from 002-database-models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── conversation.py # Existing - Conversation model
│   │   └── message.py      # Existing - Message model
│   ├── mcp/                # Existing from 003-mcp-task-tools
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   ├── agent/              # Existing from 004-ai-intent-agent
│   │   ├── __init__.py
│   │   ├── task_agent.py
│   │   ├── prompts.py
│   │   └── utils.py
│   └── api/                # NEW: API endpoints module
│       ├── __init__.py
│       ├── chat.py         # Chat endpoint implementation
│       └── schemas.py      # Pydantic request/response models
└── tests/
    ├── __init__.py
    └── test_chat.py        # NEW: Chat endpoint tests
```

**Structure Decision**: Web application structure (backend/) matching existing project layout. API endpoints organized in dedicated `api/` package. Conversation/Message models already exist from feature 002.

## Implementation Steps

Based on user input:

1. **Create API schemas**: Define Pydantic models for request/response in `backend/src/api/schemas.py`
2. **Create chat endpoint**: Implement `POST /api/{user_id}/chat` in `backend/src/api/chat.py`
3. **Create conversation service**: Database operations for conversations/messages
4. **Integrate with TaskAgent**: Load history, run agent, capture tool calls
5. **Register router**: Add chat router to FastAPI app in `main.py`
6. **Add error handling**: Validate user_id, conversation_id, empty messages
7. **Test endpoint**: Manual and automated testing per quickstart.md

## Complexity Tracking

> No violations to justify - all constitution principles either satisfied or out of scope per spec.
