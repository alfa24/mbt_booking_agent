'use client'

import { Volume2, VolumeX } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface VoiceOutputProps {
  text: string
  isSpeaking: boolean
  isSupported: boolean
  onSpeak: () => void
  onStop: () => void
  className?: string
  size?: 'sm' | 'default'
}

export function VoiceOutput({
  text: _text,
  isSpeaking,
  isSupported,
  onSpeak,
  onStop,
  className,
  size = 'default',
}: VoiceOutputProps) {
  if (!isSupported) {
    return null
  }

  const handleClick = () => {
    if (isSpeaking) {
      onStop()
    } else {
      onSpeak()
    }
  }

  return (
    <Button
      type="button"
      size={size === 'sm' ? 'icon' : 'icon'}
      variant="ghost"
      onClick={handleClick}
      className={cn(
        'shrink-0',
        size === 'sm' && 'size-6',
        isSpeaking && 'text-primary',
        className
      )}
      title={isSpeaking ? 'Остановить' : 'Прослушать'}
      aria-label={isSpeaking ? 'Остановить воспроизведение' : 'Прослушать сообщение'}
    >
      {isSpeaking ? (
        <span className="relative">
          <VolumeX data-icon className={cn('size-4', size === 'sm' && 'size-3')} />
          <span className="absolute -right-1 -top-1 flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75" />
            <span className="relative inline-flex size-2 rounded-full bg-primary" />
          </span>
        </span>
      ) : (
        <Volume2 data-icon className={cn('size-4', size === 'sm' && 'size-3')} />
      )}
    </Button>
  )
}

interface VoiceOutputIndicatorProps {
  isSpeaking: boolean
}

export function VoiceOutputIndicator({ isSpeaking }: VoiceOutputIndicatorProps) {
  if (!isSpeaking) {
    return null
  }

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <span className="relative flex size-3">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75" />
        <span className="relative inline-flex size-3 rounded-full bg-primary" />
      </span>
      <span>Говорит...</span>
    </div>
  )
}
