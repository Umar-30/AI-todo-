# Research: AI Intent Agent

**Feature**: 004-ai-intent-agent
**Date**: 2026-01-21

## Decision 1: Agent Framework

**Decision**: Use OpenAI Agents SDK with built-in MCP support

**Rationale**:
- OpenAI Agents SDK has native MCP integration since 2025
- Supports multiple transport options (stdio, SSE, streamable HTTP)
- Aligns with constitution technology stack (OpenAI Agents SDK)
- Production-ready with automatic retries and caching

**Alternatives Considered**:
- LangChain Agents: More complex, heavier abstraction layer
- Custom implementation: More work, less battle-tested
- LastMile AI extension: Only needed for older SDK versions

## Decision 2: MCP Transport Method

**Decision**: Use `MCPServerStdio` for local MCP server communication

**Rationale**:
- MCP server from feature 003 runs as a local process
- Stdio transport is simplest for same-machine communication
- No network overhead or HTTP configuration needed
- Ideal for development and single-server deployments

**Alternatives Considered**:
- SSE Transport: Better for remote/cloud servers, but adds complexity
- Streamable HTTP: Good for custom infrastructure, overkill for local process
- Hosted MCP: Requires external service, not applicable here

## Decision 3: Tool Integration Pattern

**Decision**: Wrap existing MCP tools as function tools using `@function_tool` decorator

**Rationale**:
- OpenAI Agents SDK supports both MCP servers and function tools
- Function tools allow direct Python integration without subprocess
- Can call existing `backend/src/mcp/tools.py` functions directly
- Simpler than running separate MCP server process

**Alternatives Considered**:
- MCPServerStdio with subprocess: More overhead, harder to debug
- HostedMCPTool: Requires external hosting
- Direct API integration: Bypasses MCP, violates constitution

## Decision 4: Intent Recognition Approach

**Decision**: Use system prompt with explicit intent-to-tool mapping rules

**Rationale**:
- OpenAI models excel at following explicit instructions
- Intent keywords (add/remember, list/show, etc.) are well-defined in spec
- No additional NLP/ML infrastructure needed
- Agent can handle ambiguity by asking clarifying questions

**Alternatives Considered**:
- Separate intent classifier: Additional complexity, not needed for clear keywords
- Regex-based extraction: Too rigid, misses natural language variations
- Fine-tuned model: Overkill for simple intent mapping

## Decision 5: Response Formatting

**Decision**: Define response templates in system prompt with agent-generated natural language

**Rationale**:
- Agent can generate contextual confirmations ("I've added 'buy milk' to your tasks")
- Error messages can be user-friendly without hardcoding
- Flexibility for tool chaining responses
- Aligns with FR-007 (confirm actions) and FR-008 (user-friendly errors)

**Alternatives Considered**:
- Hardcoded response templates: Too rigid for varied user inputs
- Separate response generation step: Unnecessary complexity
- Raw tool output: Not user-friendly

## Technical Notes

### OpenAI Agents SDK Installation

```bash
pip install openai-agents
```

### Agent Configuration Pattern

```python
from agents import Agent, function_tool

@function_tool
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Create a new task for a user."""
    # Calls existing MCP tool
    from ..mcp.tools import add_task as mcp_add_task
    return mcp_add_task(user_id, title, description)

agent = Agent(
    name="TaskAssistant",
    instructions="...",  # System prompt with intent mapping
    tools=[add_task, list_tasks, complete_task, update_task, delete_task],
)
```

### System Prompt Structure

The system prompt should include:
1. Role definition (task management assistant)
2. Intent-to-tool mapping rules
3. Parameter extraction guidance
4. Response format guidelines
5. Clarification behavior rules

## Sources

- [OpenAI Agents SDK - MCP](https://openai.github.io/openai-agents-python/mcp/)
- [OpenAI Agents SDK - Tools](https://openai.github.io/openai-agents-python/tools/)
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
