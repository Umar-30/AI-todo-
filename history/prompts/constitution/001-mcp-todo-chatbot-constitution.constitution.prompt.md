---
id: 001
title: MCP Todo Chatbot Constitution
stage: constitution
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["constitution", "mcp", "todo-chatbot", "initial-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

/sp.constitution

Project: Phase III – Todo AI Chatbot (MCP-Based)

Core principles:
- MCP-compliant, tool-driven AI architecture
- Stateless agents and stateless MCP tools
- Database as the single source of truth
- Clear separation of AI logic, tools, and APIs

System requirements:
- Conversational todo management via AI
- AI logic implemented with OpenAI Agents SDK
- MCP server built using Official MCP SDK
- Stateless chat endpoint with conversation state persisted to DB

Technology stack:
- Frontend: OpenAI ChatKit
- Backend: FastAPI (Python)
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth

MCP tool rules:
- All task operations MUST use MCP tools
- Tools MUST validate input and persist to DB
- Tools MUST return deterministic, typed outputs
- No in-memory or internal tool state allowed

Required MCP tool:
Tool: add_task
Parameters:
- user_id (string, required)
- title (string, required)
- description (string, optional)

Returns:
- task_id
- status
- title

AI behavior constraints:
- Translate user intent into MCP tool calls
- Do not access DB directly
- Ask clarifying questions when intent is ambiguous
- Confirm tool execution before responding

Security & integrity:
- Auth required for all operations
- User context mandatory for task actions
- No sensitive data in AI responses

Success criteria:
- All todo actions work via chat
- Full MCP compliance
- Stateless, reproducible system

## Response snapshot

Created initial constitution (v1.0.0) for Todo AI Chatbot (MCP-Based) project with 6 core principles:
1. MCP-Compliant Architecture
2. Database as Single Source of Truth
3. Stateless Agent Design
4. Tool-Driven Operations
5. AI Behavior Constraints
6. Security and Authentication

Additional sections: Technology Stack, Development Workflow, Governance.

All placeholder tokens filled. Templates verified compatible.

## Outcome

- Impact: Initial project constitution established - foundational governance document
- Tests: N/A (documentation artifact)
- Files: .specify/memory/constitution.md (created)
- Next prompts: /sp.specify to create feature specs, /sp.plan for implementation planning
- Reflection: User provided comprehensive requirements enabling complete constitution without clarification

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
