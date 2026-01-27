# Quickstart: Stateless Chat Endpoint

**Feature**: 005-chat-endpoint
**Date**: 2026-01-21

## Prerequisites

1. Python 3.11+ installed
2. OpenAI API key configured
3. Database running (Neon PostgreSQL)
4. Features 002, 003, 004 implemented (database models, MCP tools, AI agent)

## Installation

```bash
cd backend
pip install -e ".[dev]"
```

## Environment Setup

```bash
# .env file
OPENAI_API_KEY=your-api-key-here
DATABASE_URL=your-neon-database-url
```

## Running the Server

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Quick Test

### 1. Start a New Conversation

```bash
curl -X POST "http://localhost:8000/api/user-123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy milk"}'
```

**Expected Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added 'buy milk' to your tasks.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"user_id": "user-123", "title": "buy milk"},
      "result": {"id": "...", "title": "buy milk", "completed": false}
    }
  ]
}
```

### 2. Continue the Conversation

```bash
curl -X POST "http://localhost:8000/api/user-123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "show my tasks", "conversation_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Expected Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Here are your tasks:\n1. [○] buy milk\n\n0/1 tasks completed",
  "tool_calls": [
    {
      "name": "list_tasks",
      "arguments": {"user_id": "user-123"},
      "result": [{"id": "...", "title": "buy milk", "completed": false}]
    }
  ]
}
```

## Test Scenarios

### Scenario 1: New Conversation (US1)

**Input**: POST without conversation_id
```bash
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy groceries"}'
```

**Expected**:
- Response includes new conversation_id
- Response confirms task creation
- tool_calls array contains add_task

### Scenario 2: Continue Conversation (US2)

**Input**: POST with valid conversation_id
```bash
# Use conversation_id from previous response
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "list my tasks", "conversation_id": "<id-from-previous>"}'
```

**Expected**:
- Same conversation_id returned
- Agent has context from previous messages
- tool_calls array contains list_tasks

### Scenario 3: Conversation Persistence (US3)

1. Create a conversation with Scenario 1
2. Restart the server: `Ctrl+C` then `uvicorn src.main:app --reload`
3. Continue the conversation with Scenario 2 using the same conversation_id

**Expected**:
- Conversation loads successfully after restart
- All previous messages are preserved
- No data loss

### Scenario 4: Tool Chaining (US4)

**Input**: Message that triggers multiple tools
```bash
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "add call mom and show my tasks"}'
```

**Expected**:
- Response confirms task addition AND shows list
- tool_calls array contains both add_task and list_tasks

### Scenario 5: Empty Message Error

**Input**: Empty message
```bash
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

**Expected**: 400 Bad Request
```json
{"detail": "Message content is required"}
```

### Scenario 6: Invalid Conversation ID

**Input**: Non-existent conversation_id
```bash
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "conversation_id": "00000000-0000-0000-0000-000000000000"}'
```

**Expected**: 404 Not Found
```json
{"detail": "Conversation not found"}
```

### Scenario 7: Wrong User's Conversation

**Input**: Conversation belonging to different user
```bash
# First create conversation as user-a
curl -X POST "http://localhost:8000/api/user-a/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "add my task"}'

# Then try to access as user-b
curl -X POST "http://localhost:8000/api/user-b/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "conversation_id": "<user-a-conversation-id>"}'
```

**Expected**: 403 Forbidden
```json
{"detail": "Access denied to conversation"}
```

## Validation Checklist

- [ ] New conversation creates successfully without conversation_id
- [ ] Existing conversation continues with valid conversation_id
- [ ] Conversation persists after server restart
- [ ] tool_calls array populated correctly
- [ ] Empty message returns 400 error
- [ ] Invalid conversation_id returns 404 error
- [ ] Wrong user's conversation returns 403 error
- [ ] Response time under 5 seconds
- [ ] No in-memory state (verified by restart test)

## Common Issues

### Issue: 500 Internal Server Error

```
Error: Failed to process message
Solution: Check OPENAI_API_KEY is set correctly in .env
```

### Issue: 503 Service Unavailable

```
Error: Database connection failed
Solution: Verify DATABASE_URL and ensure Neon database is accessible
```

### Issue: Conversation not persisting

```
Error: Conversation not found after restart
Solution: Ensure database tables are created (check /health endpoint)
```

### Issue: Tool calls empty

```
Error: tool_calls array is empty
Solution: Verify TaskAgent is properly configured with MCP tools
```

## Python Test Client

```python
import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Start new conversation
        response = await client.post(
            "/api/test-user/chat",
            json={"message": "add buy milk"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"Conversation ID: {data['conversation_id']}")
        print(f"Response: {data['response']}")
        print(f"Tool calls: {data['tool_calls']}")

        # Continue conversation
        response = await client.post(
            "/api/test-user/chat",
            json={
                "message": "show my tasks",
                "conversation_id": data['conversation_id']
            }
        )
        assert response.status_code == 200
        data = response.json()
        print(f"Response: {data['response']}")

if __name__ == "__main__":
    asyncio.run(test_chat())
```
