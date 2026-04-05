'use client'
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import type { ChatMessage } from '@/types/chat'

interface MessagesResponse {
  items: ChatMessage[]
  cursor: string | null
  has_more: boolean
}

export function useChat() {
  const queryClient = useQueryClient()
  const { chatId, setChatId } = useChatStore()
  const { user } = useAuthStore()

  // Создание чата
  const createChat = useMutation({
    mutationFn: async () => {
      if (!user?.id) {
        throw new Error('User not authenticated')
      }
      const res = await api.post('chats', { json: { user_id: user.id } }).json<{ id: number }>()
      return res
    },
    onSuccess: (data) => {
      setChatId(data.id)
    },
  })

  // Получение истории сообщений (cursor-based infinite query)
  const messages = useInfiniteQuery({
    queryKey: ['chat-messages', chatId],
    queryFn: async ({ pageParam }) => {
      const params = new URLSearchParams({ limit: '50' })
      if (pageParam) params.set('cursor', pageParam)
      return api.get(`chats/${chatId}/messages`, { searchParams: params }).json<MessagesResponse>()
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.has_more ? lastPage.cursor : undefined,
    enabled: !!chatId,
  })

  // Отправка сообщения
  const sendMessage = useMutation({
    mutationFn: async (content: string) => {
      return api.post(`chats/${chatId}/messages`, { json: { content } }).json<ChatMessage>()
    },
    onMutate: async (content) => {
      // Оптимистичное обновление — добавляем сообщение пользователя сразу
      await queryClient.cancelQueries({ queryKey: ['chat-messages', chatId] })
      
      const previousMessages = queryClient.getQueryData(['chat-messages', chatId])
      
      queryClient.setQueryData(['chat-messages', chatId], (old: unknown) => {
        if (!old) return old
        const optimisticMsg: ChatMessage = {
          id: Date.now(), // temp id
          chat_id: chatId!,
          role: 'user',
          content,
          created_at: new Date().toISOString(),
        }
        const pages = (old as { pages: { items: ChatMessage[] }[] }).pages
        const lastPage = pages[pages.length - 1]
        return {
          ...old,
          pages: [
            ...pages.slice(0, -1),
            { ...lastPage, items: [...lastPage.items, optimisticMsg] },
          ],
        }
      })
      
      return { previousMessages }
    },
    onSuccess: () => {
      // Рефетч для получения ответа ассистента
      queryClient.invalidateQueries({ queryKey: ['chat-messages', chatId] })
    },
    onError: (_err, _content, context) => {
      // Откат при ошибке
      if (context?.previousMessages) {
        queryClient.setQueryData(['chat-messages', chatId], context.previousMessages)
      }
    },
  })

  // Все сообщения из всех страниц (flat)
  const allMessages = messages.data?.pages.flatMap(page => page.items) ?? []

  return {
    chatId,
    messages: allMessages,
    isLoadingMessages: messages.isLoading,
    hasMoreMessages: messages.hasNextPage,
    fetchMoreMessages: messages.fetchNextPage,
    sendMessage: sendMessage.mutate,
    isSending: sendMessage.isPending,
    createChat: createChat.mutate,
    isCreatingChat: createChat.isPending,
  }
}
