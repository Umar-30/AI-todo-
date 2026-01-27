# Data Model: Database Models

**Feature**: 002-database-models
**Date**: 2026-01-19
**Status**: Complete

## Overview

This feature defines the core data entities for the Todo AI Chatbot: Task, Conversation, and Message. All entities use UUID primary keys and automatic timestamps.

## Entities

### Task

Represents a todo item belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, auto-generated | Unique task identifier |
| user_id | string | Required, indexed | Owner's user identifier |
| title | string | Required, max 255 chars | Task title |
| description | string | Optional, nullable | Detailed task description |
| completed | boolean | Required, default=false | Completion status |
| created_at | datetime | Required, auto-set | Creation timestamp (UTC) |
| updated_at | datetime | Required, auto-update | Last modification timestamp (UTC) |

**Validation Rules**:
- title: Required, 1-255 characters
- user_id: Required, non-empty string
- completed: Defaults to false on creation

**State Transitions**:
- created → completed (via update)
- completed → uncompleted (via update)
- any state → deleted (permanent)

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user's task queries

---

### Conversation

Represents a chat session belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, auto-generated | Unique conversation identifier |
| user_id | string | Required, indexed | Owner's user identifier |
| created_at | datetime | Required, auto-set | Creation timestamp (UTC) |
| updated_at | datetime | Required, auto-update | Last modification timestamp (UTC) |

**Validation Rules**:
- user_id: Required, non-empty string

**Relationships**:
- One-to-many with Message (parent side)
- Cascade delete: deleting a Conversation deletes all its Messages

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user's conversation queries

---

### Message

Represents a single message within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, auto-generated | Unique message identifier |
| user_id | string | Required | Owner's user identifier |
| conversation_id | UUID | Foreign Key (conversations.id), Required | Parent conversation |
| role | string | Required, enum: "user"/"assistant" | Sender type |
| content | text | Required | Message content |
| created_at | datetime | Required, auto-set | Creation timestamp (UTC) |

**Validation Rules**:
- user_id: Required, non-empty string
- conversation_id: Required, must reference existing Conversation
- role: Required, must be "user" or "assistant"
- content: Required, non-empty string

**Relationships**:
- Many-to-one with Conversation (child side)
- Foreign key constraint: conversation_id → conversations.id
- ON DELETE CASCADE: Message deleted when parent Conversation deleted

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for conversation message queries
- Composite index on `(conversation_id, created_at)` for ordered retrieval

---

## Relationship Diagram

```
┌─────────────┐
│    Task     │  (Independent entity)
├─────────────┤
│ id (PK)     │
│ user_id     │
│ title       │
│ description │
│ completed   │
│ created_at  │
│ updated_at  │
└─────────────┘

┌──────────────────┐         ┌─────────────────┐
│   Conversation   │ 1     * │     Message     │
├──────────────────┤─────────├─────────────────┤
│ id (PK)          │         │ id (PK)         │
│ user_id          │         │ user_id         │
│ created_at       │         │ conversation_id │──FK──┐
│ updated_at       │         │ role            │      │
└──────────────────┘         │ content         │      │
         ▲                   │ created_at      │      │
         │                   └─────────────────┘      │
         └────────────────────────────────────────────┘
                        ON DELETE CASCADE
```

## Database Schema (PostgreSQL)

### Tables to Create

1. **tasks**
   - Primary key: `id` (UUID)
   - Columns: user_id, title, description, completed, created_at, updated_at

2. **conversations**
   - Primary key: `id` (UUID)
   - Columns: user_id, created_at, updated_at

3. **messages**
   - Primary key: `id` (UUID)
   - Foreign key: `conversation_id` → `conversations.id` ON DELETE CASCADE
   - Columns: user_id, conversation_id, role, content, created_at

### Constraints

- All `id` fields: UUID, NOT NULL, PRIMARY KEY
- All `user_id` fields: VARCHAR, NOT NULL
- `tasks.title`: VARCHAR(255), NOT NULL
- `tasks.description`: TEXT, NULL
- `tasks.completed`: BOOLEAN, NOT NULL, DEFAULT FALSE
- `messages.role`: VARCHAR(20), NOT NULL, CHECK (role IN ('user', 'assistant'))
- `messages.content`: TEXT, NOT NULL
- All `created_at`: TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW()
- All `updated_at`: TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW()

## Notes

- UUIDs generated using Python's `uuid4()` for globally unique identifiers
- Timestamps stored in UTC timezone
- No soft delete - entities are permanently removed
- user_id is a string to support various authentication providers (future feature)
