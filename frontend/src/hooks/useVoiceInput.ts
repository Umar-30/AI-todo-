import { useState, useCallback, useRef, useEffect } from 'react'

// Web Speech API type definitions
interface SpeechRecognitionEvent extends Event {
  resultIndex: number
  results: SpeechRecognitionResultList
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message?: string
}

interface SpeechRecognitionInstance extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  onstart: ((this: SpeechRecognitionInstance, ev: Event) => void) | null
  onresult: ((this: SpeechRecognitionInstance, ev: SpeechRecognitionEvent) => void) | null
  onerror: ((this: SpeechRecognitionInstance, ev: SpeechRecognitionErrorEvent) => void) | null
  onend: ((this: SpeechRecognitionInstance, ev: Event) => void) | null
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionInstance
}

interface UseVoiceInputResult {
  isListening: boolean
  transcript: string
  isSupported: boolean
  error: string | null
  startListening: () => void
  stopListening: () => void
  clearTranscript: () => void
}

/**
 * Hook for voice input using Web Speech API.
 * Provides speech-to-text transcription with listening state management.
 */
export function useVoiceInput(): UseVoiceInputResult {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Check for browser support
  const SpeechRecognition: SpeechRecognitionConstructor | null =
    typeof window !== 'undefined'
      ? (window as WindowWithSpeech).SpeechRecognition ||
        (window as WindowWithSpeech).webkitSpeechRecognition ||
        null
      : null
  const isSupported = !!SpeechRecognition

  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null)

  // Initialize recognition on mount
  useEffect(() => {
    if (!SpeechRecognition) return

    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
      setError(null)
    }

    recognition.onresult = (event) => {
      let finalTranscript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          finalTranscript += result[0].transcript
        }
      }
      if (finalTranscript) {
        setTranscript(finalTranscript)
      }
    }

    recognition.onerror = (event) => {
      setIsListening(false)
      switch (event.error) {
        case 'not-allowed':
          setError('Microphone access denied. Please allow microphone access.')
          break
        case 'no-speech':
          setError('No speech detected. Please try again.')
          break
        case 'network':
          setError('Network error. Please check your connection.')
          break
        default:
          setError(`Voice input error: ${event.error}`)
      }
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = recognition

    return () => {
      recognition.abort()
    }
  }, [SpeechRecognition])

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return
    setTranscript('')
    setError(null)
    try {
      recognitionRef.current.start()
    } catch (e) {
      console.error('Failed to start recognition:', e)
      setError('Failed to start voice input')
    }
  }, [isListening])

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return
    try {
      recognitionRef.current.stop()
    } catch (e) {
      console.error('Failed to stop recognition:', e)
    }
  }, [isListening])

  const clearTranscript = useCallback(() => {
    setTranscript('')
  }, [])

  return {
    isListening,
    transcript,
    isSupported,
    error,
    startListening,
    stopListening,
    clearTranscript,
  }
}

// Type declarations for Web Speech API
interface WindowWithSpeech extends Window {
  SpeechRecognition?: SpeechRecognitionConstructor
  webkitSpeechRecognition?: SpeechRecognitionConstructor
}
