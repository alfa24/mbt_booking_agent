import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ChatState {
  chatId: number | null
  isOpen: boolean
  setChatId: (id: number) => void
  setOpen: (open: boolean) => void
  toggleOpen: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      chatId: null,
      isOpen: false,
      setChatId: (id) => set({ chatId: id }),
      setOpen: (open) => set({ isOpen: open }),
      toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
    }),
    { name: 'chat-storage' }
  )
)
