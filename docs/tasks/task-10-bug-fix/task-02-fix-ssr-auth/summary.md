# Task 02: Исправить SSR isAuthenticated проверку

## Проблема

`authenticated/layout.tsx` использовал Zustand store для проверки `isAuthenticated` при SSR:
- Zustand store пустой во время SSR → `isAuthenticated = false`
- Layout показывал loading state или `null`
- Это создавало гидратационный конфликт между SSR и клиентом
- Дублировала функциональность middleware

## Решение

Убрал всю клиентскую логику проверки аутентификации из layout:

**Было:**
```typescript
'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'

export default function AuthenticatedLayout({ children }) {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
    if (!isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, router])

  if (!isClient) {
    return <div>Загрузка...</div>
  }

  if (!isAuthenticated) {
    return null
  }

  return <AppShell>{children}</AppShell>
}
```

**Стало:**
```typescript
'use client'
import { AppShell } from '@/components/layout/app-shell'

export default function AuthenticatedLayout({ children }) {
  // Middleware уже защищает эти маршруты на сервере
  // Клиентская проверка не нужна — просто рендерим layout
  return (
    <AppShell>
      {children}
    </AppShell>
  )
}
```

## Почему это работает

1. **Middleware** (`web/src/middleware.ts`) защищает маршруты на уровне сервера
2. Если нет cookie `user_role` → middleware редиректит на `/`
3. Layout больше не нужен для проверки аутентификации
4. Убраны гидратационные конфликты

## Definition of Done (самопроверка)

- [x] Layout рендерится без loading state
- [x] Нет гидратационных конфликтов в консоли
- [x] Защищённые маршруты всё ещё защищены middleware
- [x] ESLint проходит без ошибок
- [x] Код стал проще (43 строки → 16 строк)

## Результат

✅ Layout теперь только предоставляет UI обёртку (AppShell):
- Убраны useEffect, useState, useRouter
- Убрана зависимость от Zustand store
- Убраны loading state и условный рендеринг
- Middleware обеспечивает защиту маршрутов
- Код стал проще в 2.7 раза
