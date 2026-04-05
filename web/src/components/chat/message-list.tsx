'use client'

import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { MessageBubble } from './message-bubble'
import type { ChatMessage } from '@/types/chat'

interface MessageListProps {
  messages: ChatMessage[]
}

export function MessageList({ messages }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  // Автопрокрутка при новых сообщениях
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Фильтруем system сообщения из основного списка
  const visibleMessages = messages.filter((m) => m.role !== 'system')

  return (
    <ScrollArea className="flex-1 px-4" ref={scrollRef}>
      <div className="flex flex-col gap-4 py-4">
        {visibleMessages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}
