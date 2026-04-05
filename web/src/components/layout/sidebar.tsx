"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Trophy, MessageCircle, Home, Calendar } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/store/auth"

const ownerNavItems = [
  {
    href: "/dashboard",
    label: "Обзор",
    icon: LayoutDashboard,
  },
  {
    href: "/dashboard/houses",
    label: "Дома",
    icon: Home,
  },
  {
    href: "/dashboard/bookings",
    label: "Бронирования",
    icon: Calendar,
  },
  {
    href: "/leaderboard",
    label: "Лидерборд",
    icon: Trophy,
  },
  {
    href: "/chat",
    label: "Чат",
    icon: MessageCircle,
  },
]

const tenantNavItems = [
  {
    href: "/tenant/houses",
    label: "Каталог домов",
    icon: Home,
  },
  {
    href: "/tenant/bookings",
    label: "Мои бронирования",
    icon: Calendar,
  },
  {
    href: "/chat",
    label: "Чат",
    icon: MessageCircle,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user } = useAuthStore()
  
  const isTenant = user?.role === "tenant"
  const navItems = isTenant ? tenantNavItems : ownerNavItems

  return (
    <aside className="w-64 border-r bg-card min-h-screen">
      <div className="p-6">
        <h1 className="text-xl font-bold text-primary">Бронирования</h1>
      </div>
      <nav className="px-4">
        <ul className="flex flex-col gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
            const Icon = item.icon
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <Icon data-icon className="size-4" />
                  {item.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}
