import { useState, useCallback, useRef, useEffect } from 'react'
import {
  CHATKIT_ENDPOINT,
  SESSION_STORAGE_KEY,
} from '../services/api'
import { useAuth } from '../hooks/useAuth'

/**
 * Message structure for the chat interface.
 */
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
  status?: 'sending' | 'sent' | 'error'
}

/**
 * SSE event data structure.
 */
interface ChatKitEvent {
  event: string
  data: Record<string, unknown>
}

interface ChatKitPanelProps {
  onMessageComplete?: () => void
  externalTranscript?: string
  onTranscriptConsumed?: () => void
}

/**
 * ChatKitPanel component - main chat interface for Todo AI Chatbot.
 *
 * Handles:
 * - Message send/receive (US1)
 * - Conversation continuity (US2)
 * - Session persistence (US3)
 * - Error handling (US4)
 */
export function ChatKitPanel({ onMessageComplete, externalTranscript, onTranscriptConsumed }: ChatKitPanelProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Get authenticated user ID
  const { user } = useAuth();
  const userId = user?.id || 'demo-user'; // fallback for development

  // Reference to track if we should auto-send
  const pendingVoiceMessage = useRef<string | null>(null)

  // Handle external transcript from top voice bar - send it directly
  useEffect(() => {
    if (externalTranscript && !isLoading) {
      pendingVoiceMessage.current = externalTranscript
      onTranscriptConsumed?.()
    }
  }, [externalTranscript, onTranscriptConsumed, isLoading])

  // Send pending voice message
  useEffect(() => {
    if (pendingVoiceMessage.current && !isLoading) {
      const content = pendingVoiceMessage.current
      pendingVoiceMessage.current = null
      sendMessageDirect(content)
    }
  })

  // Load session from storage on mount (US3)
  useEffect(() => {
    const stored = localStorage.getItem(SESSION_STORAGE_KEY)
    if (stored) {
      try {
        const session = JSON.parse(stored)
        if (session.threadId) {
          setThreadId(session.threadId)
          // Load conversation history
          loadConversationHistory(session.threadId)
        }
      } catch (e) {
        console.error('Failed to load session:', e)
        localStorage.removeItem(SESSION_STORAGE_KEY)
      }
    }
  }, [])

  // Save session when threadId changes (US3)
  useEffect(() => {
    if (threadId) {
      const session = {
        threadId,
        userId,
        lastUpdated: new Date().toISOString(),
      }
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
    }
  }, [threadId, userId])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /**
   * Load conversation history for a thread (US3).
   */
  const loadConversationHistory = async (tid: string) => {
    try {
      const response = await fetch(CHATKIT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId,
        },
        body: JSON.stringify({
          type: 'thread.messages',
          thread_id: tid,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to load history')
      }

      // Process SSE response
      const reader = response.body?.getReader()
      if (!reader) return

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = parseSSEEvents(buffer)
        buffer = events.remaining

        for (const evt of events.parsed) {
          if (evt.event === 'thread.messages') {
            const historyMessages = (evt.data.messages as Array<{
              id: string
              role: 'user' | 'assistant'
              content: string
              created_at: string
            }>).map((m) => ({
              id: m.id,
              role: m.role,
              content: m.content,
              createdAt: m.created_at,
              status: 'sent' as const,
            }))
            setMessages(historyMessages)
          } else if (evt.event === 'error') {
            // Thread doesn't exist, start fresh
            setThreadId(null)
            localStorage.removeItem(SESSION_STORAGE_KEY)
          }
        }
      }
    } catch (e) {
      console.error('Failed to load conversation history:', e)
      // Start fresh on error (US3)
      setThreadId(null)
      localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }

  /**
   * Parse SSE events from a buffer.
   */
  const parseSSEEvents = (
    buffer: string
  ): { parsed: ChatKitEvent[]; remaining: string } => {
    const events: ChatKitEvent[] = []
    const lines = buffer.split('\n')
    let currentEvent = ''
    let currentData = ''
    let remaining = ''

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]

      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7)
      } else if (line.startsWith('data: ')) {
        currentData = line.slice(6)
      } else if (line === '' && currentEvent && currentData) {
        try {
          events.push({
            event: currentEvent,
            data: JSON.parse(currentData),
          })
        } catch (e) {
          console.error('Failed to parse event data:', e)
        }
        currentEvent = ''
        currentData = ''
      } else if (i === lines.length - 1 && line !== '') {
        // Incomplete line at the end
        remaining = line
      }
    }

    return { parsed: events, remaining }
  }

  /**
   * Send a message directly with content (for voice input).
   */
  const sendMessageDirect = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return

    setError(null)
    setIsLoading(true)

    const tempUserMsgId = `temp-${Date.now()}`
    const userMessage: Message = {
      id: tempUserMsgId,
      role: 'user',
      content: content.trim(),
      createdAt: new Date().toISOString(),
      status: 'sending',
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await fetch(CHATKIT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId,
        },
        body: JSON.stringify({
          type: 'message',
          thread_id: threadId,
          message: {
            role: 'user',
            content: content.trim(),
          },
          metadata: {
            user_id: userId,
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = parseSSEEvents(buffer)
        buffer = events.remaining

        for (const evt of events.parsed) {
          handleSSEEvent(evt, tempUserMsgId)
        }
      }
      onMessageComplete?.()
    } catch (e) {
      console.error('Send message error:', e)
      setError(e instanceof Error ? e.message : 'Failed to send message')
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempUserMsgId ? { ...m, status: 'error' } : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, threadId, userId, onMessageComplete])

  /**
   * Send a message to the backend (US1).
   */
  const sendMessage = useCallback(async () => {
    const content = inputValue.trim()
    if (!content || isLoading) return

    // Clear input and error
    setInputValue('')
    setError(null)
    setIsLoading(true)

    // Add user message optimistically
    const tempUserMsgId = `temp-${Date.now()}`
    const userMessage: Message = {
      id: tempUserMsgId,
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
      status: 'sending',
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await fetch(CHATKIT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId,
        },
        body: JSON.stringify({
          type: 'message',
          thread_id: threadId,
          message: {
            role: 'user',
            content,
          },
          metadata: {
            user_id: userId,
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // Process SSE stream
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = parseSSEEvents(buffer)
        buffer = events.remaining

        for (const evt of events.parsed) {
          handleSSEEvent(evt, tempUserMsgId)
        }
      }
      // Notify parent that message exchange is complete (for task refresh)
      onMessageComplete?.()
    } catch (e) {
      console.error('Send message error:', e)
      setError(e instanceof Error ? e.message : 'Failed to send message')
      // Mark user message as error
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempUserMsgId ? { ...m, status: 'error' } : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [inputValue, isLoading, threadId, onMessageComplete])

  /**
   * Handle SSE events from the backend.
   */
  const handleSSEEvent = (evt: ChatKitEvent, tempUserMsgId: string) => {
    switch (evt.event) {
      case 'thread.created': {
        const thread = evt.data.thread as { id: string }
        setThreadId(thread.id)
        break
      }
      case 'message.created': {
        const msg = evt.data.message as {
          id: string
          role: 'user' | 'assistant'
          content: string
          created_at: string
        }

        if (msg.role === 'user') {
          // Update temp user message with real ID
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempUserMsgId
                ? { ...m, id: msg.id, status: 'sent' }
                : m
            )
          )
        } else {
          // Add assistant message
          setMessages((prev) => [
            ...prev,
            {
              id: msg.id,
              role: msg.role,
              content: msg.content,
              createdAt: msg.created_at,
              status: 'sent',
            },
          ])
        }
        break
      }
      case 'error': {
        const message = evt.data.message as string
        setError(message)
        break
      }
      default:
        // Ignore other events (tool.started, tool.completed, etc.)
        break
    }
  }

  /**
   * Handle input submission.
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage()
  }

  /**
   * Handle keyboard shortcuts.
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  /**
   * Clear error state (US4).
   */
  const clearError = () => {
    setError(null)
  }

  return (
    <div className="chatkit-panel">
      {/* Messages area */}
      <div className="chatkit-messages">
        {messages.length === 0 && (
          <div className="chatkit-welcome">
            <p>Welcome to Todo AI Chatbot!</p>
            <p>Try saying:</p>
            <ul>
              <li>"Add buy groceries to my tasks"</li>
              <li>"Show my tasks"</li>
              <li>"Mark the first task as done"</li>
            </ul>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chatkit-message chatkit-message-${msg.role} ${
              msg.status === 'sending' ? 'chatkit-message-sending' : ''
            } ${msg.status === 'error' ? 'chatkit-message-error' : ''}`}
          >
            <div className="chatkit-message-content">{msg.content}</div>
            <div className="chatkit-message-meta">
              {msg.status === 'sending' && <span>Sending...</span>}
              {msg.status === 'error' && <span>Failed to send</span>}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="chatkit-loading">
            <span className="chatkit-loading-dot">.</span>
            <span className="chatkit-loading-dot">.</span>
            <span className="chatkit-loading-dot">.</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error display (US4) */}
      {error && (
        <div className="chatkit-error" onClick={clearError}>
          <span>{error}</span>
          <button type="button" aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}

      {/* Input area - text only, voice input is now at the top of the page */}
      <form className="chatkit-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chatkit-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={isLoading}
          autoFocus
        />
        <button
          type="submit"
          className="chatkit-send-button"
          disabled={isLoading || !inputValue.trim()}
        >
          Send
        </button>
      </form>
    </div>
  )
}
