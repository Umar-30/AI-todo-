<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change: 0.0.0 → 1.0.0 (MAJOR: Initial constitution ratification)

Modified principles: N/A (initial version)

Added sections:
- Core Principles (6 principles)
- Technology Stack
- Development Workflow
- Governance

Removed sections: N/A (initial version)

Templates requiring updates:
- .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
- .specify/templates/spec-template.md: ✅ Compatible (Requirements section supports MCP constraints)
- .specify/templates/tasks-template.md: ✅ Compatible (Phase structure supports MCP tool tasks)

Follow-up TODOs: None
================================================================================
-->

# Todo AI Chatbot Constitution

## Core Principles

### I. MCP-Compliant Architecture

All task operations MUST be executed through MCP (Model Context Protocol) tools.
The system MUST maintain a clear separation between AI logic, tools, and APIs.
Tools MUST validate input and persist state to the database.
Tools MUST return deterministic, typed outputs.
No in-memory or internal tool state is allowed.

**Rationale**: MCP compliance ensures reproducibility, auditability, and clean boundaries
between components. Stateless tools enable horizontal scaling and simplify debugging.

### II. Database as Single Source of Truth

All application state MUST be persisted to the database (Neon Serverless PostgreSQL).
Conversation state MUST be stored in the database, not in memory.
Agents and tools MUST NOT maintain internal state between invocations.
All data access MUST go through SQLModel ORM.

**Rationale**: A single source of truth eliminates state synchronization issues,
enables stateless deployment, and provides clear audit trails for all operations.

### III. Stateless Agent Design

AI agents MUST be stateless between requests.
The chat endpoint MUST be stateless with conversation state persisted to DB.
Agents MUST NOT access the database directly; all data operations MUST use MCP tools.
Each request MUST be self-contained with all required context.

**Rationale**: Stateless agents enable horizontal scaling, simplify testing,
and ensure reproducible behavior across invocations.

### IV. Tool-Driven Operations

All task operations MUST use MCP tools exclusively.
The AI layer MUST translate user intent into MCP tool calls.
The `add_task` tool MUST accept: user_id (string, required), title (string, required),
description (string, optional) and return: task_id, status, title.
Tools MUST validate all input before executing operations.

**Rationale**: Tool-driven architecture creates explicit, testable contracts
between components and ensures all operations are auditable.

### V. AI Behavior Constraints

The AI MUST translate user intent into appropriate MCP tool calls.
The AI MUST ask clarifying questions when intent is ambiguous.
The AI MUST confirm tool execution before responding to the user.
The AI MUST NOT access the database directly.
The AI MUST NOT include sensitive data in responses.

**Rationale**: Clear AI behavior constraints ensure predictable interactions,
protect user data, and maintain system integrity.

### VI. Security and Authentication

Authentication MUST be required for all operations (via Better Auth).
User context MUST be provided for all task actions.
No sensitive data MUST appear in AI responses.
All API endpoints MUST validate authentication before processing.

**Rationale**: Security is non-negotiable. Authentication ensures user isolation
and protects against unauthorized access to task data.

## Technology Stack

**Frontend**: OpenAI ChatKit
**Backend**: FastAPI (Python)
**AI Framework**: OpenAI Agents SDK
**MCP Server**: Official MCP SDK
**ORM**: SQLModel
**Database**: Neon Serverless PostgreSQL
**Auth**: Better Auth

All technology choices are mandatory. Deviations require explicit justification
and constitution amendment.

## Development Workflow

### Conversational Task Management

Users interact with the system through natural language chat.
The AI interprets user intent and executes appropriate MCP tool calls.
All task CRUD operations flow through the MCP server.
The system confirms successful operations before responding.

### Testing Requirements

All MCP tools MUST have contract tests verifying input/output types.
Integration tests MUST verify end-to-end chat-to-database flows.
All tools MUST be tested for deterministic, reproducible outputs.

### Deployment Requirements

The system MUST be stateless and reproducible.
All state MUST be externalized to the database.
The chat endpoint MUST handle concurrent requests without state conflicts.

## Governance

This constitution supersedes all other development practices and guidelines.
All code changes MUST verify compliance with these principles.

**Amendment Process**:
1. Document proposed changes with rationale
2. Assess impact on existing system components
3. Update all dependent templates and documentation
4. Increment version according to semantic versioning:
   - MAJOR: Breaking changes to principles or architecture
   - MINOR: New principles or expanded guidance
   - PATCH: Clarifications or typo fixes

**Compliance Review**:
All pull requests MUST include a constitution compliance check.
Violations MUST be justified with explicit tradeoff documentation.

**Version**: 1.0.0 | **Ratified**: 2026-01-19 | **Last Amended**: 2026-01-19
