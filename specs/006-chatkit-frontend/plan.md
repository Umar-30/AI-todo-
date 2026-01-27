# Implementation Plan: Authentication and Landing Page for ChatKit Frontend

**Branch**: `006-chatkit-frontend` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chatkit-frontend/spec.md`

## Summary

Implementation of authentication functionality including landing page, signup/login pages, and integration with Better Auth as mandated by the project constitution. This will replace the current hardcoded demo user with proper user authentication flow, enabling secure access to the chat interface. The solution will include a landing page with navigation to signup, proper session management, and protected routes to control access to the chat functionality.

## Technical Context

**Language/Version**: TypeScript 5.x, React 18.x
**Primary Dependencies**: React, Vite, Better Auth, React Router DOM, Web Speech API (native browser)
**Storage**: localStorage (session persistence), Backend API (tasks and user data)
**Testing**: Vitest (unit), Playwright (e2e)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend enhancement)
**Performance Goals**: Chat UI interactive within 2 seconds, authentication flow < 1000ms, page load < 2 seconds
**Constraints**: Secure authentication flow required, session management via Better Auth, browser Web Speech API support required
**Scale/Scope**: Individual user accounts, single session per device, ~100 tasks max displayed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. MCP-Compliant Architecture | ✅ PASS | Frontend uses existing MCP-backed APIs; no direct DB access |
| II. Database as Single Source of Truth | ✅ PASS | Tasks fetched from backend API; localStorage only for session |
| III. Stateless Agent Design | ✅ PASS | Frontend is stateless; state persisted via backend |
| IV. Tool-Driven Operations | ✅ PASS | UI triggers chat endpoint which invokes MCP tools |
| V. AI Behavior Constraints | ✅ PASS | No AI logic in frontend; delegated to backend agent |
| VI. Security and Authentication | ✅ PASS | Now implementing Better Auth as required by constitution |

**Gate Result**: PASS - No constitution violations. Authentication now properly implemented per constitution requirement.

## Project Structure

### Documentation (this feature)

```text
specs/006-chatkit-frontend/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── auth-api.yaml    # Authentication API contracts
│   └── api.yaml         # Task list API contract
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LandingPage.tsx    # NEW - Landing page with signup button
│   │   │   ├── SignupPage.tsx     # NEW - User registration page
│   │   │   ├── LoginPage.tsx      # NEW - User login page
│   │   │   └── ProtectedRoute.tsx # NEW - Route guard for auth
│   │   ├── ChatKitPanel.tsx       # Existing - will be refactored
│   │   ├── TaskSidebar.tsx        # NEW - Task dashboard sidebar
│   │   ├── VoiceInput.tsx         # NEW - Voice input button
│   │   └── Layout.tsx             # NEW - 70/30 split layout wrapper
│   ├── hooks/
│   │   ├── useAuth.ts             # NEW - Authentication state hook
│   │   ├── useSession.ts          # Existing
│   │   ├── useTasks.ts            # NEW - Task fetching hook
│   │   └── useVoiceInput.ts       # NEW - Web Speech API hook
│   ├── services/
│   │   ├── authService.ts         # NEW - Better Auth integration
│   │   └── api.ts                 # Existing - add task list endpoint
│   ├── styles/
│   │   └── theme.css              # NEW - Dark neon theme variables
│   ├── App.tsx                    # Existing - update layout with auth routes
│   ├── App.css                    # Existing - replace with dark theme
│   └── main.tsx                   # Existing
└── tests/
    ├── unit/
    │   ├── auth/
    │   │   ├── useAuth.test.ts
    │   │   ├── LandingPage.test.tsx
    │   │   ├── SignupPage.test.tsx
    │   │   └── LoginPage.test.tsx
    │   ├── TaskSidebar.test.tsx
    │   ├── VoiceInput.test.tsx
    │   └── useTasks.test.ts
    └── e2e/
        ├── auth-flow.spec.ts
        └── chat-with-sidebar.spec.ts

backend/
├── src/
│   ├── auth/
│   │   └── better-auth-config.py  # NEW - Better Auth configuration
│   └── api/
│       ├── auth.py                # NEW - Authentication endpoints
│       └── tasks.py               # NEW - GET /api/{user_id}/tasks endpoint
└── (existing structure unchanged)
```

**Structure Decision**: Web application structure with frontend/backend separation. Frontend receives new authentication components and protected routes. Backend requires Better Auth configuration and authentication endpoints. The landing page will serve as the initial entry point for unauthenticated users.

## Complexity Tracking

No constitution violations to justify.

