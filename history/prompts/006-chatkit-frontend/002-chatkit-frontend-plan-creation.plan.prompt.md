---
id: 002
title: ChatKit Frontend Plan Creation
stage: plan
date: 2026-01-21
surface: agent
model: claude-opus-4-5-20251101
feature: 006-chatkit-frontend
branch: 006-chatkit-frontend
user: developer
command: sp.plan
labels: ["planning", "frontend", "chatkit", "architecture", "research"]
links:
  spec: specs/006-chatkit-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-chatkit-frontend/plan.md
  - specs/006-chatkit-frontend/research.md
  - specs/006-chatkit-frontend/data-model.md
  - specs/006-chatkit-frontend/quickstart.md
  - specs/006-chatkit-frontend/contracts/chatkit.yaml
tests:
  - null
---

## Prompt

/sp.plan

# sp.plan

## Steps
1. Initialize ChatKit UI
2. Connect ChatKit to POST `/api/{user_id}/chat`
3. Store and reuse conversation_id on client
4. Render user and assistant messages
5. Add loading and error handling

## Output
- Working chat UI connected to backend
- Stateless frontend with persistent conversations

## Response snapshot

Created implementation plan for ChatKit Frontend Integration:

**Phase 0 - Research (7 decisions)**:
- R1: ChatKit Architecture - Use ChatKit Python SDK wrapper
- R2: Backend Integration - Delegate to existing TaskAgent
- R3: Frontend Stack - Vite + React + TypeScript
- R4: Configuration - Self-hosted with domain key
- R5: Persistence - Map ChatKit threads to existing models
- R6: Error Handling - Map errors to ChatKit events
- R7: User ID - Hardcoded for MVP

**Phase 1 - Design Artifacts**:
- data-model.md: Message, ChatState, StoredSession entities
- contracts/chatkit.yaml: OpenAPI 3.1 spec for /chatkit endpoint
- quickstart.md: 7 test scenarios covering all user stories

**Constitution Check**: PASS (5/6 principles, VI deferred per scope)

**Key Architecture Decision**:
ChatKit frontend requires ChatKit Python SDK on backend. Created wrapper approach:
```
ChatKit React → /chatkit → ChatKitServer → TaskAgent → MCP Tools → DB
```

**Implementation Phases**:
1. Backend ChatKit Integration (add SDK, create wrapper)
2. Frontend Setup (Vite + React + TypeScript)
3. ChatKit UI Integration (components, hooks)
4. Polish (CORS, edge cases, testing)

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation
- 🧪 Tests: 7 test scenarios in quickstart.md
- 📁 Files: 5 files created (plan, research, data-model, quickstart, contract)
- 🔁 Next prompts: /sp.tasks for implementation tasks
- 🧠 Reflection: ChatKit requires SDK integration, not direct API calls

## Evaluation notes (flywheel)

- Failure modes observed: None - clean planning
- Graders run and results (PASS/FAIL): Constitution Check PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate tasks and implement
