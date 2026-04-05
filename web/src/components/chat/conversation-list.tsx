'use client'

import { Search, Bot } from 'lucide-react'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useChat } from '@/hooks/use-chat'

interface ConversationListProps {
  onSelectConversation: () => void
}

export function ConversationList({ onSelectConversation }: ConversationListProps) {
  const { messages } = useChat()

  // Получаем последнее сообщение для отображения
  const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null
  const lastMessageTime = lastMessage
    ? format(new Date(lastMessage.created_at), 'HH:mm', { locale: ru })
    : null

  // Формируем превью последнего сообщения
  const lastMessagePreview = lastMessage
    ? lastMessage.content.slice(0, 50) + (lastMessage.content.length > 50 ? '...' : '')
    : 'Начните диалог...'

  const handleSelect = () => {
    onSelectConversation()
  }

  return (
    <div className="flex h-full flex-col gap-4 rounded-lg border bg-card">
      {/* Search */}
      <div className="border-b p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Поиск..."
            className="pl-9"
          />
        </div>
      </div>

      {/* Conversation List */}
      <ScrollArea className="flex-1">
        <div className="flex flex-col gap-1 p-2">
          {/* Assistant Conversation */}
          <button
            onClick={handleSelect}
            className={cn(
              'flex items-center gap-3 rounded-lg p-3 text-left transition-colors',
              'hover:bg-accent hover:text-accent-foreground',
              'bg-accent text-accent-foreground'
            )}
          >
            <Avatar className="size-10 shrink-0">
              <AvatarFallback className="bg-primary text-primary-foreground">
                <Bot className="size-5" />
              </AvatarFallback>
            </Avatar>

            <div className="flex min-w-0 flex-1 flex-col gap-1">
              <div className="flex items-center justify-between gap-2">
                <span className="truncate font-medium">Ассистент</span>
                {lastMessageTime && (
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {lastMessageTime}
                  </span>
                )}
              </div>
              <p className="truncate text-sm text-muted-foreground">
                {lastMessagePreview}
              </p>
            </div>
          </button>
        </div>
      </ScrollArea>
    </div>
  )
}
