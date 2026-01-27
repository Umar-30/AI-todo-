# Data Model: AI Intent Agent

**Feature**: 004-ai-intent-agent
**Date**: 2026-01-21

## Overview

The AI Intent Agent is stateless and does not introduce new persistent entities. All task data is managed by the existing MCP tools from feature 003-mcp-task-tools. This document describes the conceptual entities the agent works with.

## Entities

### Agent (Runtime Only)

The AI agent instance configured with MCP tools. Not persisted.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Agent identifier ("TaskAssistant") |
| instructions | string | System prompt with intent mapping rules |
| tools | list[Tool] | Attached MCP tool wrappers |
| model | string | OpenAI model identifier |

### Intent (Derived)

Represents a recognized user intention extracted from natural language. Not persisted.

| Attribute | Type | Description |
|-----------|------|-------------|
| type | enum | add, list, complete, delete, update |
| keywords | list[string] | Trigger keywords for this intent |
| target_tool | string | MCP tool name to invoke |
| required_params | list[string] | Parameters that must be extracted |
| optional_params | list[string] | Parameters that may be extracted |

**Intent Mapping Table**:

| Intent Type | Keywords | Target Tool | Required Params | Optional Params |
|-------------|----------|-------------|-----------------|-----------------|
| add | add, remember | add_task | user_id, title | description |
| list | list, show | list_tasks | user_id | - |
| complete | done, complete | complete_task | user_id, task_id | - |
| delete | delete, remove | delete_task | user_id, task_id | - |
| update | change, update | update_task | user_id, task_id | title, description |

### ToolCall (Runtime Only)

A structured request to an MCP tool with parameters. Not persisted.

| Attribute | Type | Description |
|-----------|------|-------------|
| tool_name | string | MCP tool to invoke |
| arguments | dict | Parameters for the tool call |
| result | dict | Tool response (success or error) |

### AgentResponse (Runtime Only)

The agent's response to the user after processing. Not persisted.

| Attribute | Type | Description |
|-----------|------|-------------|
| message | string | User-facing response text |
| tool_calls | list[ToolCall] | Tools invoked for this response |
| success | bool | Whether all tool calls succeeded |

## Existing Entities (From Feature 003)

The agent interacts with these entities via MCP tools:

### Task (Persisted in Database)

| Attribute | Type | Description |
|-----------|------|-------------|
| id | UUID | Unique task identifier |
| user_id | string | Owner's user identifier |
| title | string | Task title (max 255 chars) |
| description | string? | Optional task description |
| completed | bool | Completion status |
| created_at | datetime | Creation timestamp (UTC) |
| updated_at | datetime | Last modification timestamp (UTC) |

## State Flow

```
User Message → Agent → Intent Recognition → Tool Selection → Tool Call → Response
                ↑                                              ↓
                └────────── Tool Result ───────────────────────┘
```

1. User sends natural language message
2. Agent analyzes message and recognizes intent
3. Agent selects appropriate MCP tool based on intent
4. Agent extracts parameters from message
5. Agent calls MCP tool with parameters
6. Tool returns result (success or error)
7. Agent formats user-friendly response
8. Response returned to user

## Notes

- Agent is fully stateless per Constitution III
- All task persistence handled by MCP tools (feature 003)
- User context (user_id) must be provided externally (e.g., by chat endpoint)
- Tool chaining: Agent may call multiple tools sequentially for complex requests
