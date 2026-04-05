export interface ChatMessage {
  id: number
  chat_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}
