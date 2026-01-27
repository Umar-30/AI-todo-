import { useState, useCallback, useEffect } from 'react'
import { fetchTasks } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import { useTaskStream } from '../hooks/useTaskStream'
import type { Task } from '../types/task'

interface UseTasksResult {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
  /** Whether real-time updates are connected */
  isStreamConnected: boolean
}

/**
 * Hook for fetching and managing tasks with real-time updates.
 * Uses JWT authentication - user ID is extracted from token on backend.
 * Automatically receives real-time updates via SSE when tasks change.
 */
export function useTasks(): UseTasksResult {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isStreamConnected, setIsStreamConnected] = useState(false)

  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Handle real-time task events
  const handleTaskCreated = useCallback((task: Task) => {
    setTasks((prev) => {
      // Avoid duplicates
      if (prev.some((t) => t.id === task.id)) {
        return prev
      }
      return [task, ...prev]
    })
  }, [])

  const handleTaskUpdated = useCallback((task: Task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? task : t))
    )
  }, [])

  const handleTaskCompleted = useCallback((task: Task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, ...task } : t))
    )
  }, [])

  const handleTaskUncompleted = useCallback((task: Task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, ...task } : t))
    )
  }, [])

  const handleTaskDeleted = useCallback((taskId: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId))
  }, [])

  const handleConnected = useCallback(() => {
    setIsStreamConnected(true)
  }, [])

  // Subscribe to real-time updates
  useTaskStream({
    enabled: isAuthenticated && !authLoading,
    onTaskCreated: handleTaskCreated,
    onTaskUpdated: handleTaskUpdated,
    onTaskCompleted: handleTaskCompleted,
    onTaskUncompleted: handleTaskUncompleted,
    onTaskDeleted: handleTaskDeleted,
    onAnyEvent: handleConnected,
  })

  const refresh = useCallback(async () => {
    if (authLoading) return;

    if (!isAuthenticated) {
      setTasks([])
      setIsLoading(false)
      return;
    }

    setIsLoading(true)
    setError(null)
    try {
      const response = await fetchTasks()
      setTasks(response.tasks)
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to fetch tasks'
      setError(message)
      console.error('useTasks error:', e)
    } finally {
      setIsLoading(false)
    }
  }, [isAuthenticated, authLoading])

  // Initial fetch on mount and when auth changes
  useEffect(() => {
    refresh()
  }, [refresh])

  return {
    tasks,
    isLoading,
    error,
    refresh,
    isStreamConnected,
  }
}
