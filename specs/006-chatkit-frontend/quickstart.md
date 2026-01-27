# Quickstart: Authentication and Landing Page for ChatKit Frontend

**Feature**: 006-chatkit-frontend
**Date**: 2026-01-23

## Overview

This feature implements authentication functionality including landing page, signup/login pages, and integration with Better Auth as mandated by the project constitution. It also retains the sidebar task dashboard, voice input, and dark neon theme functionality.

## Prerequisites

- Node.js 18+
- Python 3.11+
- Backend running (`cd backend && uvicorn src.main:app --reload`)
- PostgreSQL (Neon) database configured
- Better Auth configured for the backend

## Quick Setup

### 1. Backend Authentication Setup

Configure Better Auth in the backend:

```bash
cd backend

# Install Better Auth if not already available
pip install better-auth-python  # Or follow Better Auth Python setup guide

# Create auth configuration file
mkdir -p src/auth
touch src/auth/better-auth-config.py
```

### 2. Frontend Authentication Setup

```bash
cd frontend

# Install Better Auth dependencies
npm install better-auth @better-auth/react

# Install routing dependencies if not already installed
npm install react-router-dom

# Start development server
npm run dev
```

### 3. Create Authentication Components

Create the following authentication-related files in the frontend:

#### Auth Service (`frontend/src/services/authService.ts`)
```typescript
import { createAuthClient } from "@better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000",
  // Add your Better Auth configuration
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

#### Authentication Hook (`frontend/src/hooks/useAuth.ts`)
```typescript
import { useState, useEffect } from 'react';
import { useSession } from '../services/authService';

export const useAuth = () => {
  const { data: session, isLoading } = useSession();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(!!session?.user);
  }, [session]);

  return {
    isAuthenticated,
    user: session?.user,
    isLoading,
    error: session?.error || null
  };
};
```

#### Landing Page (`frontend/src/pages/LandingPage.tsx`)
```typescript
import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="landing-page">
      <h1>Welcome to Todo AI Chatbot</h1>
      <p>Your intelligent task management assistant</p>
      <Link to="/signup" className="cta-button">Get Started</Link>
      <Link to="/login">Already have an account? Sign in</Link>
    </div>
  );
};

export default LandingPage;
```

#### Protected Route Component (`frontend/src/components/auth/ProtectedRoute.tsx`)
```typescript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;
```

### 4. Update Main App Component
Modify `App.tsx` to include authentication routes:

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
```

### 5. Update API Service
Modify `frontend/src/services/api.ts` to use authenticated user context instead of hardcoded demo user:

```typescript
// Replace the hardcoded DEFAULT_USER_ID with authenticated user ID
// Use the auth service to get the current user's ID for API calls
// Example:
// export const getCurrentUserId = () => {
//   const { user } = useAuth();
//   return user?.id || 'demo-user'; // fallback for dev only
// };
```

## Key Implementation Steps

### Step 1: Extend Task Model (Backend)

Update `backend/src/models/task.py`:
```python
due_date: Optional[datetime] = Field(default=None)
priority: Optional[str] = Field(default=None)
category: Optional[str] = Field(default=None, max_length=50)
```

### Step 2: Add Task List API (Backend)

Create `backend/src/api/tasks.py`:
```python
@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str):
    tasks = list_tasks(user_id)
    return {"tasks": tasks}
```

### Step 3: Create Layout Component (Frontend)

```typescript
// frontend/src/components/Layout.tsx
export function Layout({ children, sidebar }) {
  return (
    <div className="app-layout">
      <main className="chat-area">{children}</main>
      <aside className="sidebar">{sidebar}</aside>
    </div>
  );
}
```

### Step 4: Create Task Sidebar (Frontend)

```typescript
// frontend/src/components/TaskSidebar.tsx
export function TaskSidebar({ tasks, isLoading }) {
  return (
    <div className="task-sidebar">
      <h2>Tasks</h2>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
}
```

### Step 5: Add Voice Input Hook (Frontend)

```typescript
// frontend/src/hooks/useVoiceInput.ts
export function useVoiceInput() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  // ... Web Speech API integration
}
```

### Step 6: Apply Dark Neon Theme (Frontend)

```css
/* frontend/src/styles/theme.css */
:root {
  --bg-primary: #0a0a0f;
  --accent-primary: #00ffff;
  /* ... */
}
```

## Testing

### Manual Testing Checklist

- [ ] Chat panel displays messages correctly
- [ ] Sidebar shows task list with all fields
- [ ] Voice input transcribes speech to text
- [ ] Dark theme renders correctly
- [ ] 70/30 layout ratio is correct
- [ ] Tasks refresh after chat response

### Run Tests

```bash
# Frontend unit tests
cd frontend && npm test

# Frontend e2e tests
cd frontend && npm run test:e2e
```

## API Reference

### GET /api/{user_id}/tasks

Returns all tasks for a user.

**Response:**
```json
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

## Troubleshooting

### Voice Input Not Working

1. Check browser support (Chrome/Edge/Safari required)
2. Ensure microphone permissions granted
3. Check console for Web Speech API errors

### Tasks Not Refreshing

1. Verify backend `/api/{user_id}/tasks` endpoint is accessible
2. Check network tab for failed requests
3. Ensure `onMessageComplete` callback is wired up

### Theme Not Applied

1. Verify `theme.css` is imported in `main.tsx`
2. Check CSS variable names match usage
3. Clear browser cache
