'use client'

import { Mic, MicOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface VoiceInputProps {
  isListening: boolean
  isSupported: boolean
  onStart: () => void
  onStop: () => void
  className?: string
}

export function VoiceInput({
  isListening,
  isSupported,
  onStart,
  onStop,
  className,
}: VoiceInputProps) {
  if (!isSupported) {
    return null
  }

  return (
    <Button
      type="button"
      size="icon"
      variant={isListening ? 'destructive' : 'outline'}
      onClick={isListening ? onStop : onStart}
      className={cn('shrink-0', className)}
      title={isListening ? 'Остановить запись' : 'Начать голосовой ввод'}
      aria-label={isListening ? 'Остановить запись' : 'Начать голосовой ввод'}
    >
      {isListening ? (
        <span className="relative">
          <MicOff data-icon className="size-4" />
          <span className="absolute -right-1 -top-1 flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-destructive opacity-75" />
            <span className="relative inline-flex size-2 rounded-full bg-destructive" />
          </span>
        </span>
      ) : (
        <Mic data-icon className="size-4" />
      )}
    </Button>
  )
}

interface VoiceInputIndicatorProps {
  isListening: boolean
}

export function VoiceInputIndicator({ isListening }: VoiceInputIndicatorProps) {
  if (!isListening) {
    return null
  }

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <span className="relative flex size-3">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75" />
        <span className="relative inline-flex size-3 rounded-full bg-primary" />
      </span>
      <span>Слушаю...</span>
    </div>
  )
}
