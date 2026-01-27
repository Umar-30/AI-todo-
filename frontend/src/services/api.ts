/**
 * ChatKit API configuration for Todo AI Chatbot.
 */

import type { TaskListResponse } from '../types/task'

// API base URL - uses Vite proxy in development
export const API_BASE_URL = ''

// ChatKit endpoint
export const CHATKIT_ENDPOINT = '/chatkit'

// Storage key for session persistence
export const SESSION_STORAGE_KEY = 'todo-ai-chatbot-session'

/**
 * ChatKit API configuration object for useChatKit hook.
 */
export const chatKitConfig = {
  api: {
    url: CHATKIT_ENDPOINT,
  },
}

/**
 * Send a message to the ChatKit backend.
 *
 * @param message - Message content
 * @param userId - Authenticated user ID
 * @param threadId - Optional thread/conversation ID
 * @returns EventSource for SSE stream
 */
export function createChatRequest(
  message: string,
  userId: string,
  threadId?: string | null,
): { body: string; headers: Record<string, string> } {
  return {
    body: JSON.stringify({
      type: 'message',
      thread_id: threadId || null,
      message: {
        role: 'user',
        content: message,
      },
      metadata: {
        user_id: userId,
      },
    }),
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': userId,
    },
  }
}

/**
 * Fetch messages for a thread.
 */
export function createThreadMessagesRequest(threadId: string, userId: string): {
  body: string
  headers: Record<string, string>
} {
  return {
    body: JSON.stringify({
      type: 'thread.messages',
      thread_id: threadId,
    }),
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': userId,
    },
  }
}

/**
 * Fetch all tasks for the current user using JWT token.
 *
 * @returns Promise resolving to TaskListResponse
 * @throws Error if fetch fails or not authenticated
 */
export async function fetchTasks(): Promise<TaskListResponse> {
  const { getToken } = await import('./authService')
  const token = getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch('/api/tasks', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

/**
 * Mark a task as completed.
 */
export async function completeTask(taskId: string): Promise<void> {
  const { getToken } = await import('./authService')
  const token = getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`/api/tasks/${taskId}/complete`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to complete task: ${response.status}`)
  }
}

/**
 * Mark a task as pending (uncomplete).
 */
export async function uncompleteTask(taskId: string): Promise<void> {
  const { getToken } = await import('./authService')
  const token = getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`/api/tasks/${taskId}/uncomplete`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to uncomplete task: ${response.status}`)
  }
}

/**
 * Delete a task permanently.
 */
export async function deleteTask(taskId: string): Promise<void> {
  const { getToken } = await import('./authService')
  const token = getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`/api/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to delete task: ${response.status}`)
  }
}
