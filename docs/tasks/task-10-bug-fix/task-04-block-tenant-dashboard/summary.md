# Task 04: Заблокировать tenant доступ к /dashboard/*

## Решение

Этот баг был автоматически исправлен в **Task 01** при исправлении логики middleware.

Middleware теперь корректно проверяет роль пользователя (строки 45-52 в `middleware.ts`):

```typescript
// Check owner-only routes
const isOwnerRoute = OWNER_ONLY_ROUTES.some(
  (route) => pathname === route || pathname.startsWith(`${route}/`)
)

if (isOwnerRoute && role === "tenant") {
  return NextResponse.redirect(new URL("/tenant/houses", request.url))
}
```

## Как это работает

1. OWNER_ONLY_ROUTES = `["/dashboard", "/leaderboard", "/houses", "/bookings"]`
2. Middleware проверяет если путь начинается с любого из этих маршрутов
3. Если роль = `"tenant"` → редирект на `/tenant/houses`
4. Tenant больше не может получить доступ к owner dashboard

## Definition of Done (самопроверка)

- [x] Tenant на `/dashboard` → 307 redirect на `/tenant/houses`
- [x] Tenant на `/dashboard/bookings` → 307 redirect на `/tenant/houses`
- [x] Tenant на `/leaderboard` → 307 redirect на `/tenant/houses`
- [x] Owner на `/dashboard` → доступ разрешён
- [x] Both на `/dashboard` → доступ разрешён

## Результат

✅ Ролевая защита работает на уровне middleware:
- Tenant заблокированы от owner маршрутов
- Owner имеют полный доступ к dashboard
- Оба fix (middleware + login redirect) работают вместе
