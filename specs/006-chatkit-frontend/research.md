# Research: ChatKit Frontend with Sidebar Dashboard

**Feature**: 006-chatkit-frontend
**Date**: 2026-01-22
**Status**: Complete

## Research Tasks

### 1. Web Speech API Browser Support & Implementation

**Decision**: Use native Web Speech API (SpeechRecognition interface)

**Rationale**:
- Native browser API, no external dependencies
- Well-supported in Chrome, Edge, Safari (with webkit prefix)
- Aligns with stateless architecture (no backend voice processing)
- Free to use, no API keys required

**Alternatives Considered**:
- OpenAI Whisper API: Higher accuracy but requires backend changes, API costs, latency
- Azure Speech Services: Enterprise-grade but overkill for this use case
- Google Cloud Speech-to-Text: Good accuracy but adds complexity and cost

**Implementation Notes**:
```typescript
// Browser compatibility check
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const isSupported = !!SpeechRecognition;

// Basic usage pattern
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';
```

**Browser Support**:
| Browser | Support |
|---------|---------|
| Chrome | Full |
| Edge | Full |
| Safari | webkit prefix |
| Firefox | Not supported |

**Fallback Strategy**: Show disabled mic button with tooltip "Voice input not supported in this browser" for Firefox users.

---

### 2. Dark Neon Theme CSS Architecture

**Decision**: CSS custom properties (variables) with dark base colors and neon cyan accents

**Rationale**:
- CSS variables enable easy theme customization
- No additional dependencies (no CSS-in-JS library needed)
- Performant (native browser support)
- Easy to maintain and extend

**Alternatives Considered**:
- Styled-components: Runtime overhead, larger bundle
- Tailwind CSS: Would require project reconfiguration
- SCSS: Build step complexity, not needed for this scope

**Color Palette**:
```css
:root {
  /* Dark base */
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-tertiary: #1a1a25;

  /* Neon cyan accent */
  --accent-primary: #00ffff;
  --accent-secondary: #00cccc;
  --accent-glow: rgba(0, 255, 255, 0.3);

  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --text-muted: #606060;

  /* Semantic */
  --success: #00ff88;
  --warning: #ffcc00;
  --error: #ff4444;

  /* Borders */
  --border-color: #2a2a35;
  --border-glow: 0 0 10px var(--accent-glow);
}
```

**Neon Glow Effects**:
```css
.neon-glow {
  box-shadow: 0 0 5px var(--accent-primary),
              0 0 10px var(--accent-glow),
              0 0 20px var(--accent-glow);
}

.neon-text {
  text-shadow: 0 0 10px var(--accent-primary);
}
```

---

### 3. 70/30 Layout Split Implementation

**Decision**: CSS Grid with `grid-template-columns: 7fr 3fr`

**Rationale**:
- Clean, semantic approach
- Responsive-friendly with media queries
- No JavaScript layout calculations needed
- Native browser support

**Alternatives Considered**:
- Flexbox with percentage widths: Works but grid is more explicit
- CSS columns: Not appropriate for app layouts
- JavaScript-based resizer: Adds complexity, not required per spec

**Implementation Pattern**:
```css
.app-layout {
  display: grid;
  grid-template-columns: 7fr 3fr;
  height: 100vh;
  gap: 0;
}

@media (max-width: 768px) {
  .app-layout {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
  }
}
```

---

### 4. Task List API Endpoint

**Decision**: Add `GET /api/{user_id}/tasks` endpoint to backend

**Rationale**:
- RESTful pattern consistent with existing chat endpoint
- Reuses existing MCP `list_tasks` tool internally
- Simple JSON response, no streaming needed

**Alternatives Considered**:
- Include tasks in chat response: Couples concerns, increases response size
- Separate tasks microservice: Over-engineering for this scope
- GraphQL: Overkill, would require significant backend changes

**Endpoint Design**:
```
GET /api/{user_id}/tasks

Response 200:
{
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string | null",
      "completed": boolean,
      "due_date": "ISO8601 | null",
      "priority": "high | medium | low | null",
      "category": "string | null",
      "created_at": "ISO8601",
      "updated_at": "ISO8601"
    }
  ]
}
```

**Note**: Current Task model lacks `due_date`, `priority`, and `category` fields. Per spec FR-014, these are required. This will need a database migration.

---

### 5. Task Refresh Strategy

**Decision**: Refresh task list after each successful chat response (not polling)

**Rationale**:
- Matches spec clarification (refresh after each chat response)
- No polling overhead
- Ensures UI consistency with conversation state
- Simple implementation

**Alternatives Considered**:
- Polling every N seconds: Unnecessary API calls, wasted resources
- WebSocket push: Explicitly out of scope per spec
- Manual refresh button only: Poor UX, user might miss task updates

**Implementation Pattern**:
```typescript
// In ChatKitPanel after receiving assistant message
const handleChatResponse = async (response) => {
  // ... process message
  await refreshTasks(); // Trigger sidebar refresh
};
```

---

### 6. Task Model Extension (Database Migration Required)

**Decision**: Extend Task model with `due_date`, `priority`, `category` fields

**Current Model** (from `backend/src/models/task.py`):
- id, user_id, title, description, completed, created_at, updated_at

**Required Fields** (per FR-014):
- `due_date: Optional[datetime]` - Task due date
- `priority: Optional[str]` - Enum: "high", "medium", "low"
- `category: Optional[str]` - User-defined category

**Migration Strategy**:
1. Add nullable columns (no data loss)
2. Update MCP tools to accept/return new fields
3. Frontend displays null values gracefully

---

## Summary of Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Voice API choice | Web Speech API (native browser) |
| Theme architecture | CSS custom properties |
| Layout approach | CSS Grid 7fr/3fr |
| Task API design | GET /api/{user_id}/tasks |
| Refresh mechanism | After each chat response |
| Missing task fields | Extend model with migration |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Firefox no voice support | Graceful degradation with disabled button |
| Voice recognition accuracy | Users can edit transcribed text before sending |
| Task model migration | Nullable fields, backward compatible |
| CSS variable browser support | 95%+ coverage, fallbacks for edge cases |

## Additional Research: Authentication Implementation

### 1. Better Auth Integration

**Decision**: Use Better Auth for complete authentication solution
**Rationale**: Better Auth is mandated by the project constitution and provides a comprehensive authentication solution with support for various providers, secure session management, and easy React integration.

**Alternatives considered**:
- Custom authentication: Would require significant security expertise and ongoing maintenance
- Firebase Auth: Not aligned with constitution's technology stack
- Other third-party solutions: Better Auth specifically mentioned in constitution

### 2. Frontend Authentication Components

**Decision**: Create dedicated auth components (LandingPage, SignupPage, LoginPage, ProtectedRoute)
**Rationale**: Separation of concerns and reusable authentication components that follow React best practices.

**Implementation approach**:
- LandingPage: Entry point with prominent signup button
- SignupPage: Registration form with validation
- LoginPage: Login form with validation
- ProtectedRoute: Route guard to protect chat functionality

### 3. Session Management Strategy

**Decision**: Use Better Auth's built-in session management
**Rationale**: Leverages proven, secure session management rather than custom implementation.

**Key considerations**:
- Secure token handling
- Automatic session refresh
- Cross-tab synchronization
- Proper cleanup on logout

### 4. User Flow Implementation

**Decision**: Landing → Signup/Login → Chat flow as specified in requirements
**Rationale**: Matches user requirements and provides clear, intuitive navigation.

**Flow details**:
- Unauthenticated users land on landing page
- Click signup button to go to registration
- After successful signup/login, redirect to chat page
- Subsequent visits check auth status and redirect appropriately

### 5. API Integration Updates

**Decision**: Replace hardcoded user_id with authenticated user context
**Rationale**: Required by constitution for security and proper user isolation.

**Changes needed**:
- Update api.ts to use authenticated user_id from Better Auth
- Modify backend endpoints to validate authentication tokens
- Remove hardcoded 'demo-user' references

## Summary of Authentication Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Authentication provider | Better Auth (constitution mandate) |
| Component structure | Dedicated auth components (Landing, Signup, Login, ProtectedRoute) |
| Session management | Better Auth's built-in solution |
| User flow | Landing → Signup/Login → Chat |
| API integration | Replace hardcoded user_id with authenticated context |

## Next Steps

Proceed to Phase 1: Generate data-model.md and API contracts.
