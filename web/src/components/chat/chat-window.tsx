'use client'

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { MessageList } from './message-list'
import { MessageInput } from './message-input'
import { useChat } from '@/hooks/use-chat'
import { useChatStore } from '@/store/chat'

export function ChatWindow() {
  const { isOpen, setOpen } = useChatStore()
  const {
    messages,
    isLoadingMessages,
    sendMessage,
    isSending,
  } = useChat()

  return (
    <Sheet open={isOpen} onOpenChange={setOpen}>
      <SheetContent side="right" className="flex w-full flex-col sm:max-w-md">
        <SheetHeader className="border-b pb-4">
          <SheetTitle>Ассистент</SheetTitle>
        </SheetHeader>

        {isLoadingMessages ? (
          <div className="flex flex-1 items-center justify-center">
            <div className="text-muted-foreground">Загрузка...</div>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}

        <MessageInput onSend={sendMessage} isSending={isSending} />
      </SheetContent>
    </Sheet>
  )
}
