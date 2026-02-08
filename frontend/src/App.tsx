import { useCallback, useRef, useState, useEffect } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { ChatKitPanel } from './components/ChatKitPanel'
import { TaskSidebar } from './components/TaskSidebar'
import { VoiceInput } from './components/VoiceInput'
import { useTasks } from './hooks/useTasks'
import { useVoiceInput } from './hooks/useVoiceInput'
import { useAuth } from './hooks/useAuth'
import { signOut } from './services/authService'
import LandingPage from './pages/LandingPage'
import SignupPage from './pages/SignupPage'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/auth/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatBotPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

function ChatBotPage() {
  const { tasks, isLoading, error, refresh, isStreamConnected } = useTasks()
  const { user } = useAuth()
  const navigate = useNavigate()
  const sidebarRef = useRef<{ refresh: () => void }>({ refresh })

  const handleLogout = useCallback(async () => {
    await signOut()
    navigate('/login')
  }, [navigate])

  // Voice input hook for the top voice input
  const {
    isListening,
    transcript,
    isSupported: voiceSupported,
    startListening,
    stopListening,
    clearTranscript,
  } = useVoiceInput()

  // Track voice transcript in the voice input field
  const [voiceText, setVoiceText] = useState<string>('')

  // When transcript updates from voice input, show it in voice field
  useEffect(() => {
    if (transcript) {
      setVoiceText(transcript)
      clearTranscript()
    }
  }, [transcript, clearTranscript])

  // Update ref when refresh changes
  sidebarRef.current.refresh = refresh

  // Callback to refresh tasks after chat message completes
  const handleMessageComplete = useCallback(() => {
    sidebarRef.current.refresh()
  }, [])

  // Handle voice text change (manual editing)
  const handleVoiceTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVoiceText(e.target.value)
  }


  // State to trigger sending voice text
  const [sendVoiceText, setSendVoiceText] = useState<string>('')

  // Handle send button click
  const handleVoiceSend = useCallback(() => {
    if (voiceText.trim()) {
      setSendVoiceText(voiceText)
      setVoiceText('')
    }
  }, [voiceText])

  // Clear send trigger after ChatKitPanel consumes it
  const handleVoiceSent = useCallback(() => {
    setSendVoiceText('')
  }, [])

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="header-logo">
            <h1>
              <span className="neon-text">Todo AI Chatbot</span>
            </h1>
            <div className="neon-border"></div>
          </div>
          <p className="header-subtitle">Manage your tasks with natural language</p>
        </div>
        <div className="header-user">
          {user && <span className="header-email">{user.email}</span>}
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Top voice input bar spanning full width */}
      <div className="top-voice-input">
        <div className="voice-input-container">
          <VoiceInput
            isListening={isListening}
            isSupported={voiceSupported}
            disabled={false}
            onToggle={isListening ? stopListening : startListening}
          />
          <input
            type="text"
            className="voice-text-field"
            value={voiceText}
            onChange={handleVoiceTextChange}
            placeholder={isListening ? 'Listening...' : 'Click mic to speak your task'}
            readOnly={isListening}
          />
          <button
            className="voice-send-button"
            onClick={handleVoiceSend}
            disabled={!voiceText.trim() || isListening}
          >
            Send
          </button>
        </div>
      </div>

      {/* Split layout: chat input on left, task dashboard on right */}
      <div className="chat-task-split-layout">
        <div className="chat-input-section">
          <div className="section-title">Chat & Commands</div>
          <ChatKitPanel
            onMessageComplete={handleMessageComplete}
            externalTranscript={sendVoiceText}
            onTranscriptConsumed={handleVoiceSent}
          />
        </div>

        <div className="task-dashboard-section">
          <div className="section-title">Task Dashboard</div>
          <TaskSidebar
            tasks={tasks}
            isLoading={isLoading}
            error={error}
            onRefresh={refresh}
            isLive={isStreamConnected}
          />
        </div>
      </div>
    </div>
  )
}

export default App
