'use client'

import { useState, useCallback, useEffect } from 'react'
import { Send, Database } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import { useSpeechRecognition } from '@/hooks/use-speech-recognition'
import { VoiceInput, VoiceInputIndicator } from './voice-input'
import { DataQueryInputIndicator, type QueryMode } from './data-query-mode'

interface MessageInputProps {
  onSend: (content: string) => void
  isSending: boolean
  mode?: QueryMode
  onModeChange?: (mode: QueryMode) => void
}

export function MessageInput({
  onSend,
  isSending,
  mode = 'chat',
  onModeChange,
}: MessageInputProps) {
  const [content, setContent] = useState('')
  const [lastError, setLastError] = useState<string | null>(null)

  const {
    transcript,
    isListening,
    isProcessing,
    error,
    errorMessage,
    isSupported,
    start,
    stop,
    reset,
  } = useSpeechRecognition()

  // Update content when transcript changes
  useEffect(() => {
    if (transcript) {
      setContent((prev) => {
        const newContent = prev ? `${prev} ${transcript}`.trim() : transcript
        return newContent
      })
      reset()
    }
  }, [transcript, reset])

  // Show error toast when error changes
  useEffect(() => {
    if (error && errorMessage && errorMessage !== lastError) {
      toast.error(errorMessage, {
        duration: 5000,
        action: {
          label: 'Повторить',
          onClick: () => start(),
        },
      })
      setLastError(errorMessage)
    }
  }, [error, errorMessage, lastError, start])

  // Clear lastError when starting new recording
  useEffect(() => {
    if (isListening) {
      setLastError(null)
    }
  }, [isListening])

  const handleSend = useCallback(() => {
    const trimmed = content.trim()
    if (!trimmed) {
      toast.error('Введите сообщение')
      return
    }
    // Stop listening if active before sending
    if (isListening) {
      stop()
    }
    onSend(trimmed)
    setContent('')
  }, [content, onSend, isListening, stop])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Отправка по Enter (без Shift) или Ctrl+Enter
      if ((e.key === 'Enter' && !e.shiftKey) || (e.key === 'Enter' && e.ctrlKey)) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const toggleMode = useCallback(() => {
    if (onModeChange) {
      onModeChange(mode === 'chat' ? 'data' : 'chat')
    }
  }, [mode, onModeChange])

  const placeholder =
    mode === 'data'
      ? 'Задайте вопрос о данных (например: "Сколько бронирований в этом месяце?")'
      : 'Введите сообщение...'

  return (
    <div className="flex flex-col gap-2 border-t bg-background p-4">
      {/* Indicators */}
      <div className="flex items-center gap-2 px-1">
        <VoiceInputIndicator
          isListening={isListening}
          isProcessing={isProcessing}
          transcript={transcript}
        />
        <DataQueryInputIndicator mode={mode} />
      </div>

      <div className="flex items-end gap-2">
        {/* Voice Input */}
        <VoiceInput
          isListening={isListening}
          isProcessing={isProcessing}
          isSupported={isSupported}
          error={error}
          onStart={start}
          onStop={stop}
        />

        {/* Mode Toggle Button */}
        {onModeChange && (
          <Button
            type="button"
            size="icon"
            variant={mode === 'data' ? 'default' : 'outline'}
            onClick={toggleMode}
            disabled={isSending}
            className="shrink-0"
            title={
              mode === 'data' ? 'Переключить на обычный чат' : 'Вопрос к данным'
            }
          >
            <Database data-icon className="size-4" />
          </Button>
        )}

        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isSending}
          className={cn(
            'min-h-[44px] resize-none',
            'focus-visible:ring-1 focus-visible:ring-ring'
          )}
          rows={1}
        />
        <Button
          size="icon"
          onClick={handleSend}
          disabled={isSending || !content.trim()}
          className="shrink-0"
        >
          <Send data-icon className="size-4" />
        </Button>
      </div>
    </div>
  )
}
