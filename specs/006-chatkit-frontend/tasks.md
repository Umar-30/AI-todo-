# Tasks: Authentication and Landing Page for ChatKit Frontend

**Input**: Design documents from `/specs/006-chatkit-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/auth-api.yaml

**Tests**: Not explicitly requested - test tasks excluded.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (FR-022 through FR-027)
- Exact file paths included in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [x] T001 Verify frontend dependencies are installed (better-auth, @better-auth/react) in frontend/package.json
- [x] T002 [P] Create auth directory structure at frontend/src/components/auth/
- [x] T003 [P] Create auth service file at frontend/src/services/authService.ts
- [x] T004 [P] Create auth hook file at frontend/src/hooks/useAuth.ts

---

## Phase 2: Backend Foundation (Blocking Prerequisites)

**Purpose**: Backend authentication infrastructure that MUST complete before frontend work begins

**⚠️ CRITICAL**: Better Auth configuration and authentication endpoints must be ready before UI work begins

### Backend Foundation

- [x] T005 Configure Better Auth in backend at backend/src/auth/better-auth-config.py
- [x] T006 Create authentication endpoints in backend/src/api/auth.py
- [x] T007 Register auth router in backend/src/main.py
- [x] T008 Update existing API endpoints to require authentication validation

**Checkpoint**: Backend authentication system ready - auth endpoints working, existing endpoints secured

---

## Phase 3: Frontend Foundation (Blocking Prerequisites)

**Purpose**: Frontend authentication infrastructure that MUST complete before UI work begins

### Frontend Foundation

- [x] T009 [P] Create authService with Better Auth client in frontend/src/services/authService.ts
- [x] T010 [P] Create useAuth hook for authentication state management in frontend/src/hooks/useAuth.ts
- [x] T011 Create ProtectedRoute component in frontend/src/components/auth/ProtectedRoute.tsx
- [x] T012 Update API service to use authenticated user context instead of hardcoded user in frontend/src/services/api.ts

**Checkpoint**: Authentication foundation ready - auth service, hook, and protected routes available

---

## Phase 4: User Story - Landing Page (FR-022)

**Goal**: Implement landing page with prominent button to navigate to signup page

**Independent Test**: Visit root path and verify landing page with signup button is displayed

### Implementation for FR-022

- [x] T013 [FR-022] Create LandingPage component with signup button in frontend/src/pages/LandingPage.tsx
- [x] T014 [FR-022] Add landing page styles with dark theme in frontend/src/App.css
- [x] T015 [FR-022] Update App.tsx to include route for landing page at root path

**Checkpoint**: Landing page displays with functional signup button

---

## Phase 5: User Story - Signup and Login Pages (FR-023)

**Goal**: Provide signup and login pages using Better Auth for user authentication

**Independent Test**: Navigate to signup/login pages and verify forms are displayed with proper validation

### Implementation for FR-023

- [x] T016 [P] [FR-023] Create SignupPage component with registration form in frontend/src/pages/SignupPage.tsx
- [x] T017 [P] [FR-023] Create LoginPage component with login form in frontend/src/pages/LoginPage.tsx
- [x] T018 [FR-023] Add form validation to signup page in frontend/src/pages/SignupPage.tsx
- [x] T019 [FR-023] Add form validation to login page in frontend/src/pages/LoginPage.tsx
- [x] T020 [FR-023] Add signup page styles with dark theme in frontend/src/App.css
- [x] T021 [FR-023] Add login page styles with dark theme in frontend/src/App.css

**Checkpoint**: Signup and login pages display with functional forms

---

## Phase 6: User Story - Redirect After Authentication (FR-024)

**Goal**: Redirect users to the chat page after successful authentication

**Independent Test**: Complete signup/login and verify user is redirected to chat page

### Implementation for FR-024

- [x] T022 [FR-024] Implement signup success redirect to chat page in frontend/src/pages/SignupPage.tsx
- [x] T023 [FR-024] Implement login success redirect to chat page in frontend/src/pages/LoginPage.tsx
- [x] T024 [FR-024] Verify redirect works from both signup and login flows

**Checkpoint**: Successful authentication redirects to chat page

---

## Phase 7: User Story - Session Management (FR-025)

**Goal**: Manage user authentication state using Better Auth's session management

**Independent Test**: Verify session persists across page refreshes and user remains authenticated

### Implementation for FR-025

- [x] T025 [FR-025] Implement session persistence in useAuth hook in frontend/src/hooks/useAuth.ts
- [x] T026 [FR-025] Add session refresh functionality in authService in frontend/src/services/authService.ts
- [x] T027 [FR-025] Verify session persists after page refresh in useAuth hook
- [x] T028 [FR-025] Implement logout functionality with session cleanup in authService

**Checkpoint**: User session persists across page refreshes and can be properly terminated

---

## Phase 8: User Story - Replace Hardcoded User (FR-026)

**Goal**: Replace hardcoded demo user with authenticated user context

**Independent Test**: Verify API calls use authenticated user ID instead of hardcoded 'demo-user'

### Implementation for FR-026

- [x] T029 [FR-026] Update API service to use authenticated user ID in frontend/src/services/api.ts
- [x] T030 [FR-026] Remove hardcoded DEFAULT_USER_ID constant in frontend/src/services/api.ts
- [x] T031 [FR-026] Verify all API calls use authenticated context in frontend/src/services/api.ts

**Checkpoint**: All API calls use authenticated user context instead of hardcoded user

---

## Phase 9: User Story - Protected Access (FR-027)

**Goal**: Validate user authentication before allowing access to chat functionality

**Independent Test**: Navigate directly to chat page without authentication and verify redirect to login

### Implementation for FR-027

- [x] T032 [FR-027] Implement authentication check in ProtectedRoute component in frontend/src/components/auth/ProtectedRoute.tsx
- [x] T033 [FR-027] Apply ProtectedRoute to chat page in App.tsx
- [x] T034 [FR-027] Verify unauthenticated access redirects to login in ProtectedRoute component
- [x] T035 [FR-027] Add authentication loading state to ProtectedRoute component

**Checkpoint**: Chat functionality is protected and requires authentication

---

## Phase 10: Integration & Polish

**Purpose**: Connect all components and refine the user experience

- [x] T036 Update main App component to include all authentication routes in frontend/src/App.tsx
- [x] T037 Verify complete user flow: Landing → Signup/Login → Chat → Logout
- [x] T038 Add error handling for authentication failures in auth components
- [x] T039 Style all auth components consistently with dark neon theme
- [x] T040 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Backend Foundation (Phase 2)**: Depends on Setup - BLOCKS frontend auth work
- **Frontend Foundation (Phase 3)**: Depends on Backend Foundation - BLOCKS UI work
- **Landing Page (Phase 4)**: Depends on Frontend Foundation
- **Signup/Login Pages (Phase 5)**: Depends on Frontend Foundation
- **Redirect After Auth (Phase 6)**: Depends on Signup/Login Pages + Session Management
- **Session Management (Phase 7)**: Depends on Frontend Foundation
- **Replace Hardcoded User (Phase 8)**: Depends on Frontend Foundation
- **Protected Access (Phase 9)**: Depends on Frontend Foundation
- **Integration & Polish (Phase 10)**: Depends on all previous phases

### User Story Dependencies

| Story | Can Start After | Independent? |
|-------|-----------------|--------------|
| FR-022 (Landing) | Frontend Foundation | Yes |
| FR-023 (Signup/Login) | Frontend Foundation | Yes |
| FR-024 (Redirect) | Signup/Login + Session | No |
| FR-025 (Session) | Frontend Foundation | Yes |
| FR-026 (Replace User) | Frontend Foundation | Yes |
| FR-027 (Protected) | Frontend Foundation | Yes |

### Parallel Opportunities

**Within Frontend Foundation Phase:**
```
Parallel Group A (Services):
  T009 (authService) || T010 (useAuth hook)

Parallel Group B (Components - can run after Group A):
  T011 (ProtectedRoute) || T012 (API service update)
```

**After Frontend Foundation:**
```
FR-022 (Landing) and FR-023 (Signup/Login) can start in parallel
FR-025 (Session) and FR-026 (Replace User) can start in parallel
```

---

## Task Summary

| Phase | Story | Task Count |
|-------|-------|------------|
| Phase 1 | Setup | 4 |
| Phase 2 | Backend Foundation | 4 |
| Phase 3 | Frontend Foundation | 4 |
| Phase 4 | FR-022 (Landing) | 3 |
| Phase 5 | FR-023 (Signup/Login) | 6 |
| Phase 6 | FR-024 (Redirect) | 3 |
| Phase 7 | FR-025 (Session) | 4 |
| Phase 8 | FR-026 (Replace User) | 3 |
| Phase 9 | FR-027 (Protected) | 4 |
| Phase 10 | Integration | 5 |
| **Total** | | **40** |

---

## Notes

- Backend Better Auth configuration is blocking prerequisite
- Frontend auth foundation (services/hooks) should complete before UI work
- Existing chat functionality should be preserved and integrated with auth
- Each story independently testable per acceptance scenarios in spec.md