# Feature Specification: Stateless Chat Endpoint

**Feature Branch**: `005-chat-endpoint`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Define a stateless chat API backed by database persistence."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start New Conversation (Priority: P1)

A client sends a chat message to the API without a conversation_id. The system creates a new conversation, stores the user's message, runs the AI agent to process it, and returns the agent's response along with the new conversation_id for future reference.

**Why this priority**: This is the foundational flow - without the ability to start new conversations, no other functionality is possible.

**Independent Test**: Send a POST request without conversation_id and verify a new conversation is created with the message stored and a response returned.

**Acceptance Scenarios**:

1. **Given** no existing conversation, **When** client sends a message to `POST /api/{user_id}/chat` without conversation_id, **Then** system creates a new conversation, stores the user message, runs the agent, stores the assistant response, and returns conversation_id + response + tool_calls.
2. **Given** no existing conversation, **When** client sends "add buy milk", **Then** system returns a response confirming task creation and includes any tool_calls executed by the agent.
3. **Given** no existing conversation, **When** client sends a message, **Then** the response includes the newly created conversation_id that can be used for follow-up messages.

---

### User Story 2 - Continue Existing Conversation (Priority: P1)

A client sends a chat message with an existing conversation_id. The system loads the conversation history, provides it as context to the AI agent, processes the new message, and returns the response while maintaining conversation continuity.

**Why this priority**: Conversation continuity is essential for meaningful task management - users need context from previous messages to effectively manage their tasks.

**Independent Test**: Create a conversation, then send follow-up messages with the conversation_id and verify context is maintained.

**Acceptance Scenarios**:

1. **Given** an existing conversation with ID "abc-123", **When** client sends a new message with conversation_id "abc-123", **Then** system loads previous messages, includes them as context for the agent, and processes the new message with full context.
2. **Given** a conversation where user previously added a task, **When** user says "show my tasks" in the same conversation, **Then** agent has access to conversation history and can provide contextually relevant responses.
3. **Given** an existing conversation, **When** client sends multiple sequential messages, **Then** each message is stored and the conversation history grows with each interaction.

---

### User Story 3 - Conversation Persistence Across Restarts (Priority: P2)

Conversations persist in the database and remain accessible after server restarts. A client can resume any conversation at any time using its conversation_id, regardless of server state.

**Why this priority**: Persistence is critical for reliability but depends on basic conversation flow working first.

**Independent Test**: Create a conversation, simulate server restart (or test with fresh server instance), then continue the conversation and verify history is intact.

**Acceptance Scenarios**:

1. **Given** a conversation created before server restart, **When** client sends a message with that conversation_id after restart, **Then** system loads the full conversation history and continues normally.
2. **Given** conversations stored in the database, **When** the server process restarts, **Then** no conversation data is lost and all conversations remain accessible.
3. **Given** no in-memory state is used, **When** any request is processed, **Then** all conversation state is loaded fresh from the database.

---

### User Story 4 - Agent Tool Execution and Response (Priority: P2)

When the AI agent determines it needs to execute MCP tools (add_task, list_tasks, etc.), the system executes those tools and returns information about what tools were called along with the agent's response.

**Why this priority**: Tool execution is the core value of the chat interface but requires conversation flow to be established first.

**Independent Test**: Send a message that triggers tool use (e.g., "add buy milk") and verify tool_calls are included in the response.

**Acceptance Scenarios**:

1. **Given** a user message that triggers tool use, **When** agent decides to call add_task, **Then** the response includes tool_calls array showing which tools were invoked.
2. **Given** a message like "add groceries and show my list", **When** agent chains multiple tools, **Then** response includes all tool_calls in execution order.
3. **Given** the agent executes tools, **When** response is returned, **Then** the assistant's message reflects the outcomes of those tool calls.

---

### Edge Cases

- What happens when conversation_id is provided but doesn't exist? System returns an error indicating conversation not found.
- What happens when user_id in the path doesn't match the conversation owner? System returns an authorization error.
- How does system handle empty messages? System returns a validation error requiring non-empty message content.
- What happens when the agent fails to respond? System returns an error message and does not store a partial response.
- How does system handle very long conversation histories? System loads all messages (future optimization may paginate or summarize).
- What happens when MCP tool execution fails? Agent handles the error gracefully and returns a user-friendly error message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept POST requests at `/api/{user_id}/chat` endpoint
- **FR-002**: System MUST create a new conversation when no conversation_id is provided in the request
- **FR-003**: System MUST load existing conversation history when conversation_id is provided
- **FR-004**: System MUST store the user's message in the database before processing
- **FR-005**: System MUST pass conversation history to the AI agent as context
- **FR-006**: System MUST execute MCP tools as directed by the agent
- **FR-007**: System MUST store the assistant's response in the database after processing
- **FR-008**: System MUST return conversation_id, response text, and tool_calls array in the response
- **FR-009**: System MUST NOT maintain any in-memory conversation state between requests
- **FR-010**: System MUST use the database as the single source of truth for all conversation data
- **FR-011**: System MUST validate that conversation_id belongs to the specified user_id when provided
- **FR-012**: System MUST return appropriate error responses for invalid requests (missing user_id, empty message, invalid conversation_id)

### Key Entities

- **Conversation**: Represents a chat session between a user and the AI assistant. Contains a unique identifier, the owning user_id, and timestamps. Has many Messages.
- **Message**: Represents a single message in a conversation. Contains the message content, role (user or assistant), timestamp, and optional metadata about tool calls. Belongs to one Conversation.
- **Tool Call Record**: Represents a tool invocation made by the agent during message processing. Contains tool name, arguments, and result. Associated with assistant Messages.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a message and receive an AI response within 5 seconds (excluding network latency)
- **SC-002**: Conversations persist 100% reliably across server restarts with no data loss
- **SC-003**: Users can continue any existing conversation with correct context loaded
- **SC-004**: System correctly reports all tool calls made by the agent in every response
- **SC-005**: System handles 100 concurrent chat requests without failures
- **SC-006**: Error responses are returned within 1 second with clear, actionable messages
- **SC-007**: All conversation data is recoverable from the database alone (no in-memory state dependency)

## Assumptions

- User authentication is handled externally; user_id is provided and trusted
- MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) are already implemented and available
- AI agent (from feature 004) is already implemented and can be instantiated
- Database schema for Conversation and Message entities exists (from feature 002)
- No message size limits beyond reasonable request size constraints
- Conversation history is loaded in full (no pagination in initial implementation)
