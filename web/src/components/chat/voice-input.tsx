'use client'

import { Mic, MicOff, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { AudioRecordingError } from '@/hooks/use-audio-recording'

interface VoiceInputProps {
  isListening: boolean
  isProcessing: boolean
  isSupported: boolean
  error: AudioRecordingError | null
  onStart: () => void
  onStop: () => void
  className?: string
}

export function VoiceInput({
  isListening,
  isProcessing,
  isSupported,
  error,
  onStart,
  onStop,
  className,
}: VoiceInputProps) {
  // Show disabled button if not supported
  if (!isSupported) {
    return (
      <Button
        type="button"
        size="icon"
        variant="outline"
        disabled
        className={cn('shrink-0 opacity-50', className)}
        title="Голосовой ввод не поддерживается в этом браузере"
      >
        <MicOff data-icon className="size-4" />
      </Button>
    )
  }

  const hasError = error !== null
  const isRecording = isListening && !isProcessing

  return (
    <Button
      type="button"
      size="icon"
      variant={hasError ? 'destructive' : isRecording ? 'default' : 'outline'}
      onClick={isRecording ? onStop : onStart}
      disabled={isProcessing}
      className={cn(
        'shrink-0 transition-all duration-200',
        isRecording && 'animate-pulse bg-red-500 hover:bg-red-600',
        className
      )}
      title={
        isProcessing
          ? 'Инициализация...'
          : isRecording
            ? 'Остановить запись'
            : hasError
              ? 'Повторить попытку'
              : 'Начать голосовой ввод'
      }
      aria-label={
        isProcessing
          ? 'Инициализация'
          : isRecording
            ? 'Остановить запись'
            : 'Начать голосовой ввод'
      }
    >
      {isProcessing ? (
        <Loader2 data-icon className="size-4 animate-spin" />
      ) : isRecording ? (
        <span className="relative">
          <Mic data-icon className="size-4" />
          <span className="absolute -right-1 -top-1 flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-white opacity-75" />
            <span className="relative inline-flex size-2 rounded-full bg-white" />
          </span>
        </span>
      ) : hasError ? (
        <MicOff data-icon className="size-4" />
      ) : (
        <Mic data-icon className="size-4" />
      )}
    </Button>
  )
}

interface VoiceInputIndicatorProps {
  isListening: boolean
  isProcessing: boolean
  transcript?: string
}

export function VoiceInputIndicator({
  isListening,
  isProcessing,
  transcript,
}: VoiceInputIndicatorProps) {
  if (!isListening && !isProcessing) {
    return null
  }

  if (isProcessing) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 data-icon className="size-3 animate-spin" />
        <span>Инициализация микрофона...</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <span className="relative flex size-3">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-red-500 opacity-75" />
        <span className="relative inline-flex size-3 rounded-full bg-red-500" />
      </span>
      <span className="flex items-center gap-1">
        Слушаю
        <span className="animate-pulse">...</span>
      </span>
      {transcript && (
        <span className="ml-2 max-w-[200px] truncate text-xs text-muted-foreground">
          «{transcript}»
        </span>
      )}
    </div>
  )
}
