import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: number
  telegram_id: string
  name: string
  role?: string
  created_at?: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  login: (user: User) => void
  logout: () => void
}

// Cookie names
const ROLE_COOKIE = "user_role"
const USER_ID_COOKIE = "user_id"

// Helper to set cookie
function setCookie(name: string, value: string, days = 7) {
  if (typeof document === "undefined") return
  const expires = new Date(Date.now() + days * 86400000).toUTCString()
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`
}

// Helper to delete cookie
function deleteCookie(name: string) {
  if (typeof document === "undefined") return
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax`
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      login: (user) => {
        // Set cookies for middleware access
        if (user.role) {
          setCookie(ROLE_COOKIE, user.role)
        }
        setCookie(USER_ID_COOKIE, user.id.toString())
        
        set({ user, isAuthenticated: true })
      },
      logout: () => {
        // Clear cookies
        deleteCookie(ROLE_COOKIE)
        deleteCookie(USER_ID_COOKIE)
        
        set({ user: null, isAuthenticated: false })
      },
    }),
    { 
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        // Re-set cookies when state is rehydrated from storage
        // This ensures middleware can access the role on subsequent requests
        if (state?.user) {
          if (state.user.role) {
            setCookie(ROLE_COOKIE, state.user.role)
          }
          setCookie(USER_ID_COOKIE, state.user.id.toString())
        }
      }
    }
  )
)
