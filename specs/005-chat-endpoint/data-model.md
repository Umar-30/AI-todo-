# Data Model: Stateless Chat Endpoint

**Feature**: 005-chat-endpoint
**Date**: 2026-01-21

## Overview

The chat endpoint uses existing database models (Conversation, Message) from feature 002 and introduces new API schema models for request/response handling. No database schema changes are required.

## Existing Database Entities (Feature 002)

### Conversation (Persisted)

Represents a chat session between a user and the AI assistant.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | UUID | Unique conversation identifier (auto-generated) |
| user_id | string | Owner's user identifier (required, indexed) |
| created_at | datetime | Creation timestamp (UTC, auto-set) |
| updated_at | datetime | Last modification timestamp (UTC, auto-update) |
| messages | List[Message] | Related messages (one-to-many relationship) |

**Constraints**:
- user_id is required and indexed for efficient lookup
- Cascade delete: deleting conversation deletes all messages

### Message (Persisted)

Represents a single message within a conversation.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | UUID | Unique message identifier (auto-generated) |
| user_id | string | Owner's user identifier (required) |
| conversation_id | UUID | Parent conversation (foreign key, required) |
| role | string | Sender type: "user" or "assistant" |
| content | string | Message content (required) |
| created_at | datetime | Creation timestamp (UTC, auto-set) |
| conversation | Conversation | Parent conversation (relationship) |

**Constraints**:
- conversation_id references conversations.id with CASCADE delete
- role must be "user" or "assistant"

## New API Schema Models (Not Persisted)

### ChatRequest

Request body for POST /api/{user_id}/chat endpoint.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| message | string | Yes | User's message content (non-empty) |
| conversation_id | UUID | No | Existing conversation to continue (optional) |

**Validation Rules**:
- message must be non-empty (after trimming whitespace)
- conversation_id, if provided, must be a valid UUID

### ToolCallInfo

Information about a single tool call made by the agent.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Tool name (e.g., "add_task", "list_tasks") |
| arguments | dict | Arguments passed to the tool |
| result | any | Result returned by the tool |

### ChatResponse

Response body from POST /api/{user_id}/chat endpoint.

| Attribute | Type | Description |
|-----------|------|-------------|
| conversation_id | UUID | Conversation identifier (new or existing) |
| response | string | Agent's response message |
| tool_calls | List[ToolCallInfo] | Tools invoked during processing |

## Entity Relationships

```
User (external)
  │
  └─── has many ───> Conversation
                        │
                        └─── has many ───> Message
                                             │
                                             ├── role: "user"
                                             └── role: "assistant" (may contain tool_calls context)
```

## State Flow

```
1. Request arrives: ChatRequest { message, conversation_id? }
                          │
                          ▼
2. Load/Create:    conversation_id provided?
                    ├── Yes: Load Conversation + Messages from DB
                    └── No:  Create new Conversation in DB
                          │
                          ▼
3. Store:          Create Message { role: "user", content: message }
                          │
                          ▼
4. Process:        Run TaskAgent with message history context
                          │
                          ▼
5. Execute:        Agent calls MCP tools (add_task, list_tasks, etc.)
                          │
                          ▼
6. Store:          Create Message { role: "assistant", content: response }
                          │
                          ▼
7. Response:       ChatResponse { conversation_id, response, tool_calls }
```

## Database Operations

### Read Operations

| Operation | Query Pattern | Used For |
|-----------|---------------|----------|
| Get conversation | `SELECT * FROM conversations WHERE id = ? AND user_id = ?` | Load existing conversation |
| Get messages | `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at` | Load conversation history |

### Write Operations

| Operation | Query Pattern | Used For |
|-----------|---------------|----------|
| Create conversation | `INSERT INTO conversations (id, user_id, created_at, updated_at)` | Start new conversation |
| Create message | `INSERT INTO messages (id, user_id, conversation_id, role, content, created_at)` | Store user/assistant message |
| Update conversation | `UPDATE conversations SET updated_at = ? WHERE id = ?` | Update timestamp on new message |

## Notes

- No schema migrations needed - using existing models
- Tool call information is returned in API response, not stored in database (MVP decision)
- Future enhancement: Add tool_calls JSON field to Message model for audit trail
- All timestamps use UTC timezone
