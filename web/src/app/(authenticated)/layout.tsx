'use client'

import { AppShell } from '@/components/layout/app-shell'

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Middleware уже защищает эти маршруты на сервере
  // Клиентская проверка не нужна — просто рендерим layout
  return (
    <AppShell>
      {children}
    </AppShell>
  )
}
