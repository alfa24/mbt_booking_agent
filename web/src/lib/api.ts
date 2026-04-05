import ky from 'ky'

export const api = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
})

export interface User {
  id: number
  telegram_id: string
  first_name: string | null
  last_name: string | null
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
  
  const users = await response.json<User[]>()
  return users.length > 0 ? users[0] : null
}
