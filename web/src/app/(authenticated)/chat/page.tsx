'use client'

import { useEffect } from 'react'
import { ChatLayout } from '@/components/chat/chat-layout'
import { useChat } from '@/hooks/use-chat'
import { useChatStore } from '@/store/chat'

export default function ChatPage() {
  const { chatId } = useChatStore()
  const { createChat, isCreatingChat } = useChat()

  // При входе на страницу: если chatId нет — создаем чат
  useEffect(() => {
    if (!chatId && !isCreatingChat) {
      createChat()
    }
  }, [chatId, isCreatingChat, createChat])

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-3xl font-bold">Чат с ассистентом</h1>
      <ChatLayout />
    </div>
  )
}
