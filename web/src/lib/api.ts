import ky from 'ky'

export const api = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  credentials: 'include', // Send cookies with requests
})

export interface User {
  id: number
  telegram_id: string
  name: string
  role?: string
  created_at?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export class ApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function getUserByTelegramId(telegramId: string): Promise<User | null> {
  const searchParams = new URLSearchParams({ telegram_id: telegramId })
  const response = await api.get('users', { searchParams })
  
  if (!response.ok) {
    throw new ApiError('Failed to load user')
  }
  
  const data = await response.json<PaginatedResponse<User>>()
  return data.items.length > 0 ? data.items[0] : null
}
