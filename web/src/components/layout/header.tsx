"use client"

import { useRouter } from "next/navigation"
import { LogOut, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuthStore } from "@/store/auth"

export function Header() {
  const router = useRouter()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const displayName = user?.name || user?.telegram_id || "Пользователь"

  return (
    <header className="border-b bg-card px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <User data-icon className="size-5 text-muted-foreground" />
          <span className="font-medium">{displayName}</span>
        </div>
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          <LogOut data-icon className="size-4 mr-2" />
          Выйти
        </Button>
      </div>
    </header>
  )
}
