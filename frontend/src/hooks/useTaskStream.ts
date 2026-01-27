import { useEffect, useRef, useCallback } from 'react'
import { getToken } from '../services/authService'
import type { Task } from '../types/task'

/**
 * Task event types from the SSE stream.
 */
export type TaskEventType =
  | 'task.created'
  | 'task.updated'
  | 'task.completed'
  | 'task.uncompleted'
  | 'task.deleted'
  | 'connected'

/**
 * Task event payload from SSE.
 */
export interface TaskStreamEvent {
  type: TaskEventType
  task_id: string
  task: Task | null
  timestamp: string
}

interface UseTaskStreamOptions {
  /** Called when a new task is created */
  onTaskCreated?: (task: Task) => void
  /** Called when a task is updated */
  onTaskUpdated?: (task: Task) => void
  /** Called when a task is marked complete */
  onTaskCompleted?: (task: Task) => void
  /** Called when a task is marked incomplete */
  onTaskUncompleted?: (task: Task) => void
  /** Called when a task is deleted */
  onTaskDeleted?: (taskId: string) => void
  /** Called on any task event */
  onAnyEvent?: (event: TaskStreamEvent) => void
  /** Whether the stream is enabled (default: true) */
  enabled?: boolean
}

/**
 * Hook for subscribing to real-time task updates via SSE.
 *
 * Automatically connects when authenticated and reconnects on disconnection.
 */
export function useTaskStream(options: UseTaskStreamOptions = {}) {
  const {
    onTaskCreated,
    onTaskUpdated,
    onTaskCompleted,
    onTaskUncompleted,
    onTaskDeleted,
    onAnyEvent,
    enabled = true,
  } = options

  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const reconnectAttempts = useRef(0)

  // Store callbacks in refs to avoid reconnection on callback changes
  const callbacksRef = useRef({
    onTaskCreated,
    onTaskUpdated,
    onTaskCompleted,
    onTaskUncompleted,
    onTaskDeleted,
    onAnyEvent,
  })

  // Update refs when callbacks change (without triggering reconnection)
  useEffect(() => {
    callbacksRef.current = {
      onTaskCreated,
      onTaskUpdated,
      onTaskCompleted,
      onTaskUncompleted,
      onTaskDeleted,
      onAnyEvent,
    }
  }, [onTaskCreated, onTaskUpdated, onTaskCompleted, onTaskUncompleted, onTaskDeleted, onAnyEvent])

  const connect = useCallback(() => {
    const token = getToken()
    if (!token || !enabled) {
      return
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Create EventSource with auth token in URL (SSE doesn't support headers)
    // We'll use a custom endpoint that accepts token as query param
    const url = `/api/tasks/stream?token=${encodeURIComponent(token)}`

    try {
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        console.log('[TaskStream] Connected')
        reconnectAttempts.current = 0
      }

      eventSource.onerror = (error) => {
        console.error('[TaskStream] Error:', error)
        eventSource.close()
        eventSourceRef.current = null

        // Only reconnect if we haven't exceeded max attempts
        if (reconnectAttempts.current < 5) {
          // Reconnect with exponential backoff (starting at 3s)
          const delay = Math.min(3000 * Math.pow(2, reconnectAttempts.current), 60000)
          reconnectAttempts.current++

          console.log(`[TaskStream] Reconnecting in ${delay}ms... (attempt ${reconnectAttempts.current}/5)`)
          reconnectTimeoutRef.current = window.setTimeout(connect, delay)
        } else {
          console.warn('[TaskStream] Max reconnection attempts reached. Real-time updates disabled.')
        }
      }

      // Handle different event types
      eventSource.addEventListener('connected', (_e) => {
        console.log('[TaskStream] Received connected event')
      })

      eventSource.addEventListener('task.created', (e) => {
        const data = JSON.parse((e as MessageEvent).data) as TaskStreamEvent
        console.log('[TaskStream] Task created:', data.task_id)
        if (data.task) {
          callbacksRef.current.onTaskCreated?.(data.task)
        }
        callbacksRef.current.onAnyEvent?.(data)
      })

      eventSource.addEventListener('task.updated', (e) => {
        const data = JSON.parse((e as MessageEvent).data) as TaskStreamEvent
        console.log('[TaskStream] Task updated:', data.task_id)
        if (data.task) {
          callbacksRef.current.onTaskUpdated?.(data.task)
        }
        callbacksRef.current.onAnyEvent?.(data)
      })

      eventSource.addEventListener('task.completed', (e) => {
        const data = JSON.parse((e as MessageEvent).data) as TaskStreamEvent
        console.log('[TaskStream] Task completed:', data.task_id)
        if (data.task) {
          callbacksRef.current.onTaskCompleted?.(data.task)
        }
        callbacksRef.current.onAnyEvent?.(data)
      })

      eventSource.addEventListener('task.uncompleted', (e) => {
        const data = JSON.parse((e as MessageEvent).data) as TaskStreamEvent
        console.log('[TaskStream] Task uncompleted:', data.task_id)
        if (data.task) {
          callbacksRef.current.onTaskUncompleted?.(data.task)
        }
        callbacksRef.current.onAnyEvent?.(data)
      })

      eventSource.addEventListener('task.deleted', (e) => {
        const data = JSON.parse((e as MessageEvent).data) as TaskStreamEvent
        console.log('[TaskStream] Task deleted:', data.task_id)
        callbacksRef.current.onTaskDeleted?.(data.task_id)
        callbacksRef.current.onAnyEvent?.(data)
      })
    } catch (error) {
      console.error('[TaskStream] Failed to create EventSource:', error)
    }
  }, [enabled]) // Only reconnect when enabled changes, not on callback changes

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    reconnect: connect,
    disconnect,
  }
}
