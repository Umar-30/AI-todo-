# Quickstart: AI Intent Agent

**Feature**: 004-ai-intent-agent
**Date**: 2026-01-21

## Prerequisites

1. Python 3.11+ installed
2. OpenAI API key configured
3. Database running (Neon PostgreSQL)
4. Feature 003 (MCP Task Tools) implemented

## Installation

```bash
cd backend
pip install openai-agents
```

## Environment Setup

```bash
# .env file
OPENAI_API_KEY=your-api-key-here
DATABASE_URL=your-neon-database-url
```

## Quick Test

### 1. Import the Agent

```python
from src.agent import create_task_agent

# Create agent instance
agent = create_task_agent()
```

### 2. Test Intent Recognition

```python
# Test add intent
response = await agent.run("add buy milk", context={"user_id": "test-user-123"})
print(response.output)  # "I've added 'buy milk' to your tasks."

# Test list intent
response = await agent.run("show my tasks", context={"user_id": "test-user-123"})
print(response.output)  # Lists all tasks

# Test complete intent
response = await agent.run("done with buy milk", context={"user_id": "test-user-123"})
print(response.output)  # "I've marked 'buy milk' as complete."
```

## Test Scenarios

### Scenario 1: Basic Add Task (US1)

**Input**: "add buy groceries"
**Expected**:
- Agent calls `add_task` with title="buy groceries"
- Response confirms task creation

```python
response = await agent.run("add buy groceries", context={"user_id": "user1"})
assert "added" in response.output.lower()
assert "buy groceries" in response.output.lower()
```

### Scenario 2: List Empty Tasks (US2)

**Input**: "show my tasks"
**Expected**:
- Agent calls `list_tasks`
- Response indicates no tasks (for new user)

```python
response = await agent.run("show my tasks", context={"user_id": "new-user"})
assert "no tasks" in response.output.lower() or "empty" in response.output.lower()
```

### Scenario 3: Complete Task (US3)

**Input**: "done with buy groceries"
**Expected**:
- Agent calls `complete_task` for matching task
- Response confirms completion

```python
# First add a task
await agent.run("add buy groceries", context={"user_id": "user1"})

# Then complete it
response = await agent.run("done with buy groceries", context={"user_id": "user1"})
assert "complete" in response.output.lower() or "done" in response.output.lower()
```

### Scenario 4: Delete Task (US4)

**Input**: "delete buy groceries"
**Expected**:
- Agent calls `delete_task` for matching task
- Response confirms deletion

```python
response = await agent.run("delete buy groceries", context={"user_id": "user1"})
assert "deleted" in response.output.lower() or "removed" in response.output.lower()
```

### Scenario 5: Update Task (US5)

**Input**: "change buy groceries to buy organic groceries"
**Expected**:
- Agent calls `update_task` with new title
- Response confirms update

```python
response = await agent.run("change buy groceries to buy organic groceries", context={"user_id": "user1"})
assert "updated" in response.output.lower() or "changed" in response.output.lower()
```

### Scenario 6: Tool Chaining (US6)

**Input**: "add buy milk and show my list"
**Expected**:
- Agent calls `add_task` then `list_tasks`
- Response confirms addition and shows list

```python
response = await agent.run("add buy milk and show my list", context={"user_id": "user1"})
assert "added" in response.output.lower()
# Response should also contain task list
```

### Scenario 7: Task Not Found Error

**Input**: "done with nonexistent task"
**Expected**:
- Agent attempts `complete_task`
- Response is user-friendly error

```python
response = await agent.run("done with nonexistent task", context={"user_id": "user1"})
assert "not found" in response.output.lower() or "couldn't find" in response.output.lower()
```

### Scenario 8: Ambiguous Intent

**Input**: "tasks"
**Expected**:
- Agent asks for clarification

```python
response = await agent.run("tasks", context={"user_id": "user1"})
# Should ask what user wants to do with tasks
assert "?" in response.output  # Contains a question
```

## Validation Checklist

- [ ] Agent correctly maps "add" intent to `add_task`
- [ ] Agent correctly maps "list"/"show" intent to `list_tasks`
- [ ] Agent correctly maps "done"/"complete" intent to `complete_task`
- [ ] Agent correctly maps "delete"/"remove" intent to `delete_task`
- [ ] Agent correctly maps "change"/"update" intent to `update_task`
- [ ] Agent extracts task title from natural language
- [ ] Agent handles task not found gracefully
- [ ] Agent asks for clarification when intent is ambiguous
- [ ] Agent chains multiple tools when requested
- [ ] Response time is under 3 seconds
- [ ] No direct database access (all via MCP tools)

## Common Issues

### Issue: OpenAI API Key Not Set

```
Error: OPENAI_API_KEY not found
Solution: Set OPENAI_API_KEY in .env file
```

### Issue: Database Connection Failed

```
Error: Database connection failed
Solution: Verify DATABASE_URL and ensure Neon database is accessible
```

### Issue: MCP Tools Not Found

```
Error: Tool 'add_task' not found
Solution: Ensure feature 003-mcp-task-tools is implemented
```
