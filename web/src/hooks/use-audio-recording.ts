'use client'

import { useState, useCallback, useRef, useEffect } from 'react'

export type AudioRecordingError =
  | 'not-supported'
  | 'not-allowed'
  | 'no-device'
  | 'recording-failed'
  | 'transcription-failed'
  | 'network-error'
  | 'unknown'

interface UseAudioRecordingReturn {
  transcript: string
  isListening: boolean
  isProcessing: boolean
  error: AudioRecordingError | null
  errorMessage: string
  isSupported: boolean
  start: () => void
  stop: () => void
  reset: () => void
}

// Error messages in Russian
const errorMessages: Record<AudioRecordingError, string> = {
  'not-supported': 'Запись аудио не поддерживается в этом браузере.',
  'not-allowed': 'Нет доступа к микрофону. Разрешите доступ в настройках браузера.',
  'no-device': 'Микрофон не найден. Проверьте подключение.',
  'recording-failed': 'Ошибка записи аудио. Попробуйте ещё раз.',
  'transcription-failed': 'Ошибка распознавания речи. Попробуйте ещё раз.',
  'network-error': 'Ошибка сети. Проверьте подключение к интернету.',
  'unknown': 'Неизвестная ошибка. Попробуйте ещё раз.',
}

// API endpoint for transcription
const TRANSCRIBE_API_URL = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/chats/transcribe`
  : '/api/v1/chats/transcribe'

export function useAudioRecording(): UseAudioRecordingReturn {
  const [transcript, setTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<AudioRecordingError | null>(null)
  const [isSupported, setIsSupported] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const mimeTypeRef = useRef<string>('audio/webm')

  // Check for browser support
  useEffect(() => {
    const supported = typeof window !== 'undefined' &&
      !!window.navigator?.mediaDevices?.getUserMedia &&
      !!window.MediaRecorder
    setIsSupported(supported)
  }, [])

  // Cleanup on unmount - only stop streams, don't clear refs
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try {
          mediaRecorderRef.current.stop()
        } catch {
          // Ignore
        }
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const transcribeAudio = useCallback(async (audioBlob: Blob) => {
    setIsProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      console.log('[AudioRecording] Sending blob:', {
        size: audioBlob.size,
        type: audioBlob.type,
        url: TRANSCRIBE_API_URL
      })

      const response = await fetch(TRANSCRIBE_API_URL, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error('transcription-failed')
        }
        throw new Error('network-error')
      }

      const data = await response.json()

      if (data.text) {
        setTranscript(data.text)
      } else {
        throw new Error('transcription-failed')
      }
    } catch (err) {
      console.error('[AudioRecording] Transcription error:', err)
      const errorType = err instanceof Error && errorMessages[err.message as AudioRecordingError]
        ? (err.message as AudioRecordingError)
        : 'transcription-failed'
      setError(errorType)
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const start = useCallback(async () => {
    console.log('[AudioRecording] start() called')

    if (!isSupported) {
      console.error('[AudioRecording] not supported')
      setError('not-supported')
      return
    }

    // Reset state
    setError(null)
    setTranscript('')
    audioChunksRef.current = []

    try {
      // Request microphone access
      console.log('[AudioRecording] Requesting microphone access...')
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      console.log('[AudioRecording] Microphone access granted')

      // Create media recorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : MediaRecorder.isTypeSupported('audio/mp4')
          ? 'audio/mp4'
          : 'audio/ogg'
      mimeTypeRef.current = mimeType

      console.log('[AudioRecording] Using mime type:', mimeType)

      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder

      // Collect audio chunks
      mediaRecorder.ondataavailable = (event) => {
        console.log('[AudioRecording] Data available:', event.data.size, 'bytes')
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        console.log('[AudioRecording] Recording stopped, chunks:', audioChunksRef.current.length)
        setIsListening(false)

        if (audioChunksRef.current.length === 0) {
          console.error('[AudioRecording] No audio data recorded')
          setError('recording-failed')
          return
        }

        // Create audio blob from all chunks
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeTypeRef.current })
        console.log('[AudioRecording] Audio blob created:', audioBlob.size, 'bytes')

        // Stop the stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
        }

        // Transcribe
        await transcribeAudio(audioBlob)

        // Clear chunks after transcription
        audioChunksRef.current = []
      }

      mediaRecorder.onerror = (event) => {
        console.error('[AudioRecording] MediaRecorder error:', event)
        setError('recording-failed')
        setIsListening(false)
      }

      // Start recording
      mediaRecorder.start(100) // Collect data every 100ms
      setIsListening(true)
      console.log('[AudioRecording] Recording started')

    } catch (err) {
      console.error('[AudioRecording] Error starting recording:', err)

      if (err instanceof Error) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setError('not-allowed')
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
          setError('no-device')
        } else if (err.name === 'NotSupportedError') {
          setError('not-supported')
        } else {
          setError('unknown')
        }
      } else {
        setError('unknown')
      }

      // Cleanup on error
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
    }
  }, [isSupported, transcribeAudio])

  const stop = useCallback(() => {
    console.log('[AudioRecording] stop() called')

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop()
        // onstop handler will process the data
      } catch (err) {
        console.error('[AudioRecording] Error stopping recorder:', err)
        setError('recording-failed')
        setIsListening(false)
      }
    }
  }, [])

  const reset = useCallback(() => {
    setTranscript('')
    setError(null)
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
