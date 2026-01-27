# Data Model: Authentication and Landing Page for ChatKit Frontend

**Feature**: 006-chatkit-frontend
**Date**: 2026-01-23

## Entity Overview

This feature primarily works with existing entities but requires:
1. **Extension** of the Task model (backend) - to be retained
2. **New authentication entities** for user accounts and sessions
3. **New TypeScript interfaces** for frontend authentication state management

---

## Backend Entity: Task (Extended)

**Location**: `backend/src/models/task.py`

### Current Fields (Unchanged)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes (auto) | Unique task identifier |
| user_id | string | Yes | Owner's user identifier |
| title | string | Yes | Task title (max 255 chars) |
| description | string | No | Detailed task description |
| completed | boolean | Yes | Completion status (default: false) |
| created_at | datetime | Yes (auto) | Creation timestamp (UTC) |
| updated_at | datetime | Yes (auto) | Last modification timestamp (UTC) |

### New Fields (To Add)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| due_date | datetime | No | Task due date (nullable) |
| priority | string | No | Priority level: "high", "medium", "low" (nullable) |
| category | string | No | User-defined category (nullable) |

### SQLModel Definition (Updated)
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

    # New fields
    due_date: Optional[datetime] = Field(default=None)
    priority: Optional[str] = Field(default=None)  # "high" | "medium" | "low"
    category: Optional[str] = Field(default=None, max_length=50)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Validation Rules
- `priority` must be one of: "high", "medium", "low", or null
- `category` max length: 50 characters
- `due_date` must be a valid ISO8601 datetime or null

---

## Frontend Entities (TypeScript Interfaces)

### Task Interface
**Location**: `frontend/src/types/task.ts` (new file)

```typescript
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  due_date: string | null;      // ISO8601 format
  priority: 'high' | 'medium' | 'low' | null;
  category: string | null;
  created_at: string;           // ISO8601 format
  updated_at: string;           // ISO8601 format
}

export interface TaskListResponse {
  tasks: Task[];
}
```

### Voice Input State
**Location**: `frontend/src/hooks/useVoiceInput.ts`

```typescript
export interface VoiceInputState {
  isListening: boolean;
  isSupported: boolean;
  transcript: string;
  error: string | null;
}
```

### Chat State (Extended)
**Location**: `frontend/src/components/ChatKitPanel.tsx` (existing, extend)

```typescript
// Add to existing ChatKitPanel state
interface ChatPanelState {
  // Existing
  messages: Message[];
  inputValue: string;
  isLoading: boolean;
  error: string | null;
  threadId: string | null;

  // New - for coordination with sidebar
  onMessageComplete?: () => void;  // Callback to trigger task refresh
}
```

---

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend State                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐         ┌─────────────────┐               │
│  │ ChatPanel   │────────▶│ TaskSidebar     │               │
│  │ (messages)  │ refresh │ (tasks[])       │               │
│  └─────────────┘         └─────────────────┘               │
│         │                        │                          │
│         │ POST /chatkit          │ GET /api/{user_id}/tasks │
│         ▼                        ▼                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       Backend API                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐         ┌─────────────────┐               │
│  │ Chat API    │         │ Tasks API       │               │
│  │ (SSE)       │         │ (JSON)          │               │
│  └─────────────┘         └─────────────────┘               │
│         │                        │                          │
│         │ MCP Tools              │ MCP list_tasks           │
│         ▼                        ▼                          │
│  ┌─────────────────────────────────────────┐               │
│  │            MCP Server / Tools            │               │
│  └─────────────────────────────────────────┘               │
│                      │                                      │
│                      │ SQLModel                             │
│                      ▼                                      │
│  ┌─────────────────────────────────────────┐               │
│  │         PostgreSQL (Neon)               │               │
│  │         - tasks table                   │               │
│  │         - conversations table           │               │
│  │         - messages table                │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## State Transitions

### Task Lifecycle
```
[Created] ──▶ [Active] ──▶ [Completed]
    │             │
    │             │ update
    │             ▼
    │        [Active]
    │
    └──────▶ [Deleted]
```

### Voice Input States
```
[Idle] ──▶ [Listening] ──▶ [Processing] ──▶ [Complete]
  │             │               │               │
  │             │ error         │ error         │
  │             ▼               ▼               │
  │        [Error] ◀───────────────────────────┘
  │             │
  │             │ retry
  └─────────────┘
```

---

## Migration Notes

### Database Migration Required
1. Add `due_date` column (nullable datetime)
2. Add `priority` column (nullable varchar(10))
3. Add `category` column (nullable varchar(50))

### Backward Compatibility
- All new fields are nullable
- Existing tasks will have null values for new fields
- Frontend gracefully handles null values (shows "-" or empty)

---

## New Backend Entities: Authentication

### User Account Entity
**Location**: Managed by Better Auth, integrates with existing user_id concept

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique user identifier (UUID) |
| email | string | Yes | User's email address (unique) |
| name | string | No | Display name |
| email_verified | boolean | Yes | Whether email has been verified |
| created_at | datetime | Yes | Account creation timestamp |
| updated_at | datetime | Yes | Last update timestamp |

### Session Entity
**Location**: Managed by Better Auth session system

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique session identifier |
| user_id | string | Yes | Reference to user account |
| expires_at | datetime | Yes | Session expiration timestamp |
| created_at | datetime | Yes | Session creation timestamp |
| updated_at | datetime | Yes | Last refresh timestamp |

---

## New Frontend Entities: Authentication State

### AuthState Interface
**Location**: `frontend/src/hooks/useAuth.ts`

```typescript
export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  emailVerified: boolean;
}
```

### Route Protection State
**Location**: `frontend/src/components/auth/ProtectedRoute.tsx`

```typescript
export interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;  // Where to redirect if not authenticated
  fallback?: React.ReactNode;  // What to show while checking auth
}
```

### Landing Page State
**Location**: `frontend/src/pages/LandingPage.tsx`

```typescript
export interface LandingPageState {
  isAuthenticated: boolean;
  loading: boolean;
}
```

### Signup Page State
**Location**: `frontend/src/pages/SignupPage.tsx`

```typescript
export interface SignupFormData {
  email: string;
  password: string;
  name: string;
}

export interface SignupPageState {
  formData: SignupFormData;
  loading: boolean;
  error: string | null;
  success: boolean;
}
```

### Login Page State
**Location**: `frontend/src/pages/LoginPage.tsx`

```typescript
export interface LoginFormData {
  email: string;
  password: string;
}

export interface LoginPageState {
  formData: LoginFormData;
  loading: boolean;
  error: string | null;
  rememberMe: boolean;
}
```

---

## Updated Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │LandingPage  │───▶│ SignupPage   │───▶│ ChatPage     │   │
│  │             │    │ (or Login)   │    │ (protected)  │   │
│  └─────────────┘    └──────────────┘    └──────────────┘   │
│         │                   │                    │         │
│         │                   │                    │         │
│         │                   ▼                    │         │
│         │              ┌──────────────┐          │         │
│         │              │ Better Auth  │◀─────────┤         │
│         │              │ (backend)    │          │         │
│         │              └──────────────┘          │         │
│         │                       │                │         │
│         │                       ▼                │         │
│         └──────────────────►┌─────────┐◄─────────┘         │
│                           │ Session │                     │
│                           │ Storage │                     │
│                           └─────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### Authentication Data Protection
- Passwords are handled by Better Auth (secure hashing, transport encryption)
- Session tokens are securely stored and managed
- Personal information is protected by authentication

### Authorization Flow
- All API calls must include authenticated user context
- User isolation: users can only access their own data
- Protected routes ensure authentication before accessing sensitive areas
