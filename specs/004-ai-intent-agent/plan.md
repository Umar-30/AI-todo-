# Implementation Plan: AI Intent Agent

**Branch**: `004-ai-intent-agent` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-intent-agent/spec.md`

## Summary

Implement an AI agent using OpenAI Agents SDK that interprets natural language user messages and maps them to appropriate MCP tools for task management. The agent handles intent recognition (add, list, complete, delete, update), extracts task details from user input, executes MCP tool calls, and provides user-friendly confirmations and error messages. Tool chaining is supported for complex multi-intent requests.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK (existing from 003-mcp-task-tools)
**Storage**: N/A (agent is stateless; task persistence handled by MCP tools)
**Testing**: pytest (manual verification for agent behavior)
**Target Platform**: Linux/Windows/macOS development, Linux server deployment
**Project Type**: Web application (backend only for this feature)
**Performance Goals**: Response within 3 seconds per spec SC-004
**Constraints**: Agent must be stateless (Constitution III), all task operations via MCP tools only (Constitution IV)
**Scale/Scope**: Single agent instance, 5 MCP tools attached

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. MCP-Compliant Architecture | PASS | Agent uses MCP tools exclusively for task operations per FR-006 |
| II. Database as Single Source of Truth | PASS | Agent has no direct DB access; MCP tools handle persistence |
| III. Stateless Agent Design | PASS | Agent designed stateless per spec assumptions |
| IV. Tool-Driven Operations | PASS | All task operations map to MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) |
| V. AI Behavior Constraints | PASS | Agent translates intent to tools (FR-001-005), asks clarification (FR-012), confirms actions (FR-007) |
| VI. Security and Authentication | PARTIAL | user_id required for all tool calls; auth enforcement out of scope for this feature |

**Gate Result**: PASS - All applicable principles satisfied. Authentication enforcement deferred to chat endpoint feature.

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-intent-agent/
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
│   │   ├── task.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── mcp/             # Existing from 003-mcp-task-tools
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   └── agent/           # NEW: AI agent module
│       ├── __init__.py
│       ├── task_agent.py    # Agent definition with MCP tools
│       ├── prompts.py       # System prompts for intent mapping
│       └── utils.py         # Helper functions for response formatting
└── tests/
    ├── __init__.py
    └── test_agent.py    # NEW: Agent behavior tests
```

**Structure Decision**: Web application structure (backend/) matching existing project layout. Agent module organized in dedicated `agent/` package for clean separation from MCP tools and other concerns.

## Implementation Steps

Based on user input:

1. **Define agent using OpenAI Agents SDK**: Create `backend/src/agent/task_agent.py` with agent configuration
2. **Attach MCP tools to the agent**: Connect existing MCP tools from `backend/src/mcp/tools.py` to agent
3. **Implement intent-to-tool mapping rules**: Define system prompt in `backend/src/agent/prompts.py` with intent keywords
4. **Add confirmation responses**: Implement response formatting for successful tool calls
5. **Add error responses**: Implement user-friendly error handling for tool failures
6. **Test agent decisions using sample inputs**: Verify correct tool selection for various intents

## Complexity Tracking

> No violations to justify - all constitution principles either satisfied or out of scope per spec.
