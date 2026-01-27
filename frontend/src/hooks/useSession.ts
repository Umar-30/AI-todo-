import { useState, useEffect, useCallback } from 'react'
import { SESSION_STORAGE_KEY } from '../services/api'

// Default user ID for session management
const DEFAULT_USER_ID = 'demo-user'

/**
 * Session data structure for browser storage.
 */
export interface StoredSession {
  threadId: string
  userId: string
  lastUpdated: string
}

/**
 * Hook for managing session persistence in browser storage.
 *
 * Handles:
 * - Loading session on mount
 * - Saving session when threadId changes
 * - Clearing session (start fresh)
 * - Validating session staleness (24 hours)
 */
export function useSession() {
  const [session, setSession] = useState<StoredSession | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load session from storage on mount
  useEffect(() => {
    const stored = localStorage.getItem(SESSION_STORAGE_KEY)
    if (stored) {
      try {
        const parsed: StoredSession = JSON.parse(stored)

        // Validate session isn't stale (24 hours)
        const lastUpdated = new Date(parsed.lastUpdated)
        const now = new Date()
        const hoursDiff = (now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60)

        if (hoursDiff < 24) {
          setSession(parsed)
        } else {
          // Session is stale, clear it
          localStorage.removeItem(SESSION_STORAGE_KEY)
        }
      } catch (e) {
        console.error('Failed to parse session:', e)
        localStorage.removeItem(SESSION_STORAGE_KEY)
      }
    }
    setIsLoaded(true)
  }, [])

  /**
   * Save or update session with a thread ID.
   */
  const saveSession = useCallback((threadId: string) => {
    const newSession: StoredSession = {
      threadId,
      userId: DEFAULT_USER_ID,
      lastUpdated: new Date().toISOString(),
    }
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(newSession))
    setSession(newSession)
  }, [])

  /**
   * Update the lastUpdated timestamp for current session.
   */
  const touchSession = useCallback(() => {
    if (session) {
      const updated: StoredSession = {
        ...session,
        lastUpdated: new Date().toISOString(),
      }
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(updated))
      setSession(updated)
    }
  }, [session])

  /**
   * Clear session and start fresh.
   */
  const clearSession = useCallback(() => {
    localStorage.removeItem(SESSION_STORAGE_KEY)
    setSession(null)
  }, [])

  /**
   * Check if session exists and is valid.
   */
  const hasValidSession = useCallback(() => {
    return session !== null && session.threadId.length > 0
  }, [session])

  return {
    session,
    isLoaded,
    threadId: session?.threadId || null,
    saveSession,
    touchSession,
    clearSession,
    hasValidSession,
  }
}
