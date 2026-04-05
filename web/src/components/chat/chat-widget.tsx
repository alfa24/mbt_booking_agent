'use client'

import { MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat'
import { useChat } from '@/hooks/use-chat'
import { ChatWindow } from './chat-window'

export function ChatWidget() {
  const { isOpen, setOpen, chatId } = useChatStore()
  const { createChat, isCreatingChat } = useChat()

  const handleClick = () => {
    if (!chatId) {
      // Создаем чат и открываем окно
      createChat(undefined, {
        onSuccess: () => {
          setOpen(true)
        },
      })
    } else {
      // Просто открываем окно
      setOpen(true)
    }
  }

  return (
    <>
      <div className="fixed bottom-4 right-4">
        <Button
          size="icon"
          className="size-14 rounded-full shadow-lg"
          onClick={handleClick}
          disabled={isCreatingChat}
          aria-label="Открыть чат с ассистентом"
        >
          <MessageCircle data-icon className="size-6" />
        </Button>
      </div>
      {isOpen && <ChatWindow />}
    </>
  )
}
