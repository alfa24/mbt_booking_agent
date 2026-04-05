'use client'

import { useState, useCallback, useRef, useEffect } from 'react'

// Type definitions for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
}

export type SpeechRecognitionError =
  | 'no-speech'
  | 'aborted'
  | 'audio-capture'
  | 'network'
  | 'not-allowed'
  | 'service-not-allowed'
  | 'bad-grammar'
  | 'language-not-supported'
  | 'unsupported'

interface UseSpeechRecognitionReturn {
  transcript: string
  isListening: boolean
  isProcessing: boolean
  error: SpeechRecognitionError | null
  errorMessage: string
  isSupported: boolean
  start: () => void
  stop: () => void
  reset: () => void
}

// Error messages in Russian
const errorMessages: Record<SpeechRecognitionError, string> = {
  'no-speech': 'Речь не распознана. Попробуйте говорить громче и чётче.',
  'aborted': 'Запись прервана.',
  'audio-capture': 'Микрофон не найден. Проверьте подключение.',
  'network': 'Ошибка сети. Проверьте подключение к интернету.',
  'not-allowed': 'Нет доступа к микрофону. Разрешите доступ в настройках браузера.',
  'service-not-allowed': 'Сервис распознавания недоступен.',
  'bad-grammar': 'Ошибка грамматики.',
  'language-not-supported': 'Язык не поддерживается.',
  'unsupported': 'Голосовой ввод не поддерживается в этом браузере.',
}

export function useSpeechRecognition(): UseSpeechRecognitionReturn {
  const [transcript, setTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<SpeechRecognitionError | null>(null)
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const restartTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Check for browser support
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    setIsSupported(!!SpeechRecognition)
  }, [])

  // Cleanup restart timeout on unmount
  useEffect(() => {
    return () => {
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current)
      }
    }
  }, [])

  const start = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setError('unsupported')
      return
    }

    // Reset state
    setError(null)
    setTranscript('')
    setIsProcessing(true)

    // Create new recognition instance
    const recognition = new SpeechRecognition()
    recognition.lang = 'ru-RU'
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onstart = () => {
      setIsListening(true)
      setIsProcessing(false)
    }

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          finalTranscript += result[0].transcript
        } else {
          interimTranscript += result[0].transcript
        }
      }

      setTranscript((prev) => {
        const newTranscript = finalTranscript || interimTranscript
        return prev ? `${prev} ${newTranscript}`.trim() : newTranscript
      })
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      const errorType = event.error as SpeechRecognitionError
      setError(errorType)
      setIsListening(false)
      setIsProcessing(false)

      // Auto-restart on no-speech error after a short delay
      if (errorType === 'no-speech' && restartTimeoutRef.current === null) {
        restartTimeoutRef.current = setTimeout(() => {
          restartTimeoutRef.current = null
          // Only restart if still in "listening" mode (user hasn't stopped)
          if (recognitionRef.current) {
            try {
              recognition.start()
            } catch {
              // Ignore restart errors
            }
          }
        }, 500)
      }
    }

    recognition.onend = () => {
      setIsListening(false)
      setIsProcessing(false)
    }

    recognitionRef.current = recognition

    try {
      recognition.start()
    } catch (_err) {
      setError('not-allowed')
      setIsProcessing(false)
    }
  }, [])

  const stop = useCallback(() => {
    // Clear any pending restart
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current)
      restartTimeoutRef.current = null
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch {
        // Ignore stop errors
      }
      recognitionRef.current = null
    }
    setIsListening(false)
    setIsProcessing(false)
  }, [])

  const reset = useCallback(() => {
    setTranscript('')
    setError(null)
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current)
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch {
          // Ignore cleanup errors
        }
      }
    }
  }, [])

  const errorMessage = error ? errorMessages[error] || `Ошибка: ${error}` : ''

  return {
    transcript,
    isListening,
    isProcessing,
    error,
    errorMessage,
    isSupported,
    start,
    stop,
    reset,
  }
}
