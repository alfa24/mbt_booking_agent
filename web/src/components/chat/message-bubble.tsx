'use client'

import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import { useSpeechSynthesis } from '@/hooks/use-speech-synthesis'
import { VoiceOutput } from './voice-output'
import type { ChatMessage } from '@/types/chat'

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const { isSpeaking, isSupported, speak, stop } = useSpeechSynthesis()

  // Пропускаем system сообщения или показываем их по-другому
  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">
          {message.content}
        </div>
      </div>
    )
  }

  const handleSpeak = () => {
    speak(message.content)
  }

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-2',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
        )}
      >
        <p className="text-sm">{message.content}</p>
        <div
          className={cn(
            'mt-1 flex items-center gap-2',
            isUser ? 'flex-row-reverse' : 'flex-row'
          )}
        >
          <span
            className={cn(
              'text-xs',
              isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'
            )}
          >
            {format(new Date(message.created_at), 'HH:mm', { locale: ru })}
          </span>
          {/* Voice output button only for assistant messages */}
          {!isUser && (
            <VoiceOutput
              text={message.content}
              isSpeaking={isSpeaking}
              isSupported={isSupported}
              onSpeak={handleSpeak}
              onStop={stop}
              size="sm"
              className={cn(
                'h-6 w-6',
                isUser
                  ? 'text-primary-foreground/70 hover:text-primary-foreground hover:bg-primary-foreground/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            />
          )}
        </div>
      </div>
    </div>
  )
}
