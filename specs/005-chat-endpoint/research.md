# Research: Stateless Chat Endpoint

**Feature**: 005-chat-endpoint
**Date**: 2026-01-21

## Overview

This document captures research decisions and alternatives considered for implementing the stateless chat endpoint.

## Research Topics

### 1. FastAPI Router Organization

**Decision**: Create dedicated `api/` package with `chat.py` router

**Rationale**:
- Separation of concerns - API endpoints separate from models and services
- Scalable pattern for adding more endpoints (future features)
- Follows FastAPI best practices for larger applications
- Consistent with existing project structure (models/, mcp/, agent/ packages)

**Alternatives Considered**:
- Add endpoint directly to `main.py` - Rejected: would bloat main.py as endpoints grow
- Create `routes/` directory - Rejected: `api/` is more descriptive for REST endpoints

### 2. Request/Response Schema Design

**Decision**: Use Pydantic models in `api/schemas.py`

**Rationale**:
- FastAPI automatic validation and documentation
- Type safety for request/response contracts
- Clear separation of API schemas from database models
- Consistent with FastAPI best practices

**Schema Structure**:
```python
# Request
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None

# Response
class ToolCallInfo(BaseModel):
    name: str
    arguments: dict
    result: Any

class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    tool_calls: list[ToolCallInfo]
```

**Alternatives Considered**:
- Inline models in endpoint - Rejected: reduces reusability and documentation clarity
- Use dataclasses - Rejected: Pydantic provides validation and FastAPI integration

### 3. Conversation History Loading Strategy

**Decision**: Load all messages for conversation, ordered by created_at

**Rationale**:
- Simple implementation for MVP
- Conversation history needed as context for agent
- OpenAI Agents SDK can handle reasonable message counts
- Per spec: "Conversation history is loaded in full (no pagination in initial implementation)"

**Alternatives Considered**:
- Paginate or limit history - Rejected for MVP: adds complexity, optimization can come later
- Summarize old messages - Rejected: requires additional LLM calls, out of scope

### 4. Tool Call Capture Strategy

**Decision**: Extend TaskAgent.run() to return tool calls alongside response

**Rationale**:
- OpenAI Agents SDK provides tool call information in response
- Need to extract and format for API response
- Minimal change to existing agent code

**Implementation Approach**:
- Modify TaskAgent.run() to return a structured result (response + tool_calls)
- Or create a wrapper service that captures this information
- Agent already has access to tool execution results

**Alternatives Considered**:
- Log tool calls separately - Rejected: need to return in response
- Store tool calls in database - Could be added later, not required for MVP

### 5. Error Handling Strategy

**Decision**: Use FastAPI HTTPException with appropriate status codes

**Rationale**:
- Standard HTTP error responses
- FastAPI automatic error formatting
- Clear client feedback per spec FR-012

**Error Mapping**:
| Scenario | Status Code | Message |
|----------|-------------|---------|
| Empty message | 400 | "Message content is required" |
| Conversation not found | 404 | "Conversation not found" |
| Conversation not owned by user | 403 | "Access denied to conversation" |
| Agent error | 500 | "Failed to process message" |

**Alternatives Considered**:
- Custom exception classes - Could add later for more granular handling
- Return error in response body - Rejected: HTTP status codes are more RESTful

### 6. Stateless Architecture Verification

**Decision**: Load conversation fresh from database on every request

**Rationale**:
- Per Constitution II: "Database as Single Source of Truth"
- Per Constitution III: "Stateless Agent Design"
- Per spec: "No in-memory state"
- Enables horizontal scaling
- Survives server restarts

**Implementation**:
- No conversation caching
- No session state
- Each request is independent
- All state read from and written to database

**Alternatives Considered**:
- Cache recent conversations - Rejected: violates stateless requirement
- Use Redis for session - Rejected: adds complexity, not needed per spec

### 7. Existing Model Integration

**Decision**: Use existing Conversation and Message models from feature 002

**Rationale**:
- Models already exist and are tested
- Relationship (Conversation has many Messages) already defined
- Cascade delete configured
- No schema changes needed

**Existing Model Fields**:
- Conversation: id, user_id, created_at, updated_at, messages (relationship)
- Message: id, user_id, conversation_id, role, content, created_at

**Note**: Message model lacks `tool_calls` field - will store in response content or add field if needed.

## Dependencies

### Existing (No Changes Needed)

- `backend/src/models/conversation.py` - Conversation model
- `backend/src/models/message.py` - Message model
- `backend/src/agent/task_agent.py` - TaskAgent with MCP tools
- `backend/src/database.py` - Database session management

### New Files to Create

- `backend/src/api/__init__.py` - API package init
- `backend/src/api/schemas.py` - Request/response Pydantic models
- `backend/src/api/chat.py` - Chat endpoint router
- `backend/tests/test_chat.py` - Endpoint tests

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Long conversation history slows agent | Medium | Accept for MVP; optimize later with summarization |
| Tool call capture changes agent interface | Low | Minimal wrapper or extension to existing TaskAgent |
| Database connection errors | Medium | FastAPI lifespan handles connection; return 503 on failure |

## Conclusion

All technical decisions align with the constitution and existing architecture. The implementation is straightforward with no blocking unknowns. Ready to proceed to Phase 1 design.
