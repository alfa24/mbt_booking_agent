'use client'

import { useState, useCallback, useEffect, useRef } from 'react'

interface UseSpeechSynthesisReturn {
  isSpeaking: boolean
  isSupported: boolean
  speak: (text: string) => void
  stop: () => void
}

export function useSpeechSynthesis(): UseSpeechSynthesisReturn {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Check for browser support
  useEffect(() => {
    setIsSupported(typeof window !== 'undefined' && 'speechSynthesis' in window)
  }, [])

  // Find Russian voice
  const getRussianVoice = useCallback((): SpeechSynthesisVoice | null => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      return null
    }

    const voices = window.speechSynthesis.getVoices()
    
    // Try to find a Russian voice
    const russianVoice = voices.find(
      (voice) => voice.lang.startsWith('ru') || voice.name.toLowerCase().includes('russian')
    )
    
    return russianVoice || voices[0] || null
  }, [])

  const speak = useCallback(
    (text: string) => {
      if (typeof window === 'undefined' || !window.speechSynthesis) {
        return
      }

      // Stop any ongoing speech
      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      const voice = getRussianVoice()
      
      if (voice) {
        utterance.voice = voice
      }
      
      utterance.lang = 'ru-RU'
      utterance.rate = 1.0
      utterance.pitch = 1.0
      utterance.volume = 1.0

      utterance.onstart = () => {
        setIsSpeaking(true)
      }

      utterance.onend = () => {
        setIsSpeaking(false)
        utteranceRef.current = null
      }

      utterance.onerror = () => {
        setIsSpeaking(false)
        utteranceRef.current = null
      }

      utteranceRef.current = utterance
      window.speechSynthesis.speak(utterance)
    },
    [getRussianVoice]
  )

  const stop = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      utteranceRef.current = null
    }
  }, [])

  // Load voices when available
  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      return
    }

    // Voices may load asynchronously
    const handleVoicesChanged = () => {
      getRussianVoice()
    }

    window.speechSynthesis.addEventListener('voiceschanged', handleVoicesChanged)
    
    // Initial load attempt
    if (window.speechSynthesis.getVoices().length > 0) {
      getRussianVoice()
    }

    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', handleVoicesChanged)
    }
  }, [getRussianVoice])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  return {
    isSpeaking,
    isSupported,
    speak,
    stop,
  }
}
