'use client'

import { useEffect, useRef, useState } from 'react'
import { Bot } from 'lucide-react'
import { format, isToday, isYesterday } from 'date-fns'
import { ru } from 'date-fns/locale'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { MessageBubble } from './message-bubble'
import { MessageInput } from './message-input'
import { useChat } from '@/hooks/use-chat'
import { useDataQuery } from '@/hooks/use-data-query'
import { DataQueryMode, type QueryMode } from './data-query-mode'
import type { ChatMessage } from '@/types/chat'

// Группировка сообщений по дате
function groupMessagesByDate(messages: ChatMessage[]): Map<string, ChatMessage[]> {
  const groups = new Map<string, ChatMessage[]>()

  messages.forEach((message) => {
    if (message.role === 'system') return

    const date = new Date(message.created_at)
    const dateKey = format(date, 'yyyy-MM-dd')

    if (!groups.has(dateKey)) {
      groups.set(dateKey, [])
    }
    groups.get(dateKey)!.push(message)
  })

  return groups
}

// Форматирование заголовка даты
function formatDateHeader(dateStr: string): string {
  const date = new Date(dateStr)

  if (isToday(date)) {
    return 'Сегодня'
  }
  if (isYesterday(date)) {
    return 'Вчера'
  }
  return format(date, 'd MMMM', { locale: ru })
}

export function ConversationView() {
  const { messages, isLoadingMessages, sendMessage, isSending } = useChat()
  const { queryData, data, isLoading: isQueryLoading, error, reset } = useDataQuery()
  const [queryMode, setQueryMode] = useState<QueryMode>('chat')
  const bottomRef = useRef<HTMLDivElement>(null)

  // Автопрокрутка к новым сообщениям
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Группируем сообщения по дате
  const messageGroups = groupMessagesByDate(messages)
  const sortedDates = Array.from(messageGroups.keys()).sort()

  // Handle mode change
  const handleModeChange = (mode: QueryMode) => {
    setQueryMode(mode)
    if (mode === 'chat') {
      reset()
    }
  }

  // Handle send based on mode
  const handleSend = (content: string) => {
    if (queryMode === 'data') {
      queryData(content)
    } else {
      sendMessage(content)
    }
  }

  return (
    <div className="flex h-full flex-col rounded-lg border bg-card">
      {/* Header */}
      <div className="flex items-center gap-3 border-b p-4">
        <Avatar className="size-10 shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <Bot className="size-5" />
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
          <span className="font-medium">Ассистент</span>
          <span className="text-xs text-muted-foreground">Всегда на связи</span>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-4">
        {isLoadingMessages ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-muted-foreground">Загрузка...</div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center text-muted-foreground">
              <p>Начните диалог с ассистентом</p>
              <p className="text-sm">Задайте вопрос о бронировании домиков</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-4 py-4">
            {sortedDates.map((dateKey, groupIndex) => (
              <div key={dateKey} className="flex flex-col gap-4">
                {/* Date Separator */}
                {groupIndex > 0 && <Separator className="my-2" />}
                <div className="flex justify-center">
                  <Badge variant="secondary" className="text-xs">
                    {formatDateHeader(dateKey)}
                  </Badge>
                </div>

                {/* Messages for this date */}
                {messageGroups.get(dateKey)?.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </ScrollArea>

      {/* Data Query Results */}
      {queryMode === 'data' && (
        <div className="border-t px-4 py-3">
          <DataQueryMode
            mode={queryMode}
            onModeChange={handleModeChange}
            isLoading={isQueryLoading}
            sql={data?.sql ?? null}
            results={data?.results ?? null}
            columns={data?.columns ?? null}
            explanation={data?.explanation ?? null}
            error={error?.message ?? null}
          />
        </div>
      )}

      {/* Input */}
      <MessageInput
        onSend={handleSend}
        isSending={isSending || isQueryLoading}
        mode={queryMode}
        onModeChange={handleModeChange}
      />
    </div>
  )
}
