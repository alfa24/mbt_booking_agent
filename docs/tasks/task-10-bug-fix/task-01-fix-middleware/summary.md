# Task 01: Исправить middleware PUBLIC_ROUTES логику

## Проблема

Middleware использовал `pathname.startsWith(route)` для всех PUBLIC_ROUTES, включая `/`. Поскольку **ВСЕ** пути начинаются с `/`, проверка всегда возвращала `true`, делая все маршруты публичными.

## Решение

Разделил логику проверки на точное совпадение для `/` и префиксное matching для остальных маршрутов:

```typescript
// БЫЛО (НЕПРАВИЛЬНО)
if (PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(route))) {
  return NextResponse.next()
}

// СТАЛО (ПРАВИЛЬНО)
const isPublicRoute = PUBLIC_ROUTES.some((route) => {
  // Root path - exact match only
  if (route === "/") return pathname === "/"
  // Other routes - prefix match
  return pathname.startsWith(route)
})

if (isPublicRoute) {
  return NextResponse.next()
}
```

Также добавил редирект на `/` для неавторизованных пользователей вместо пропуска запроса.

## Definition of Done (самопроверка)

- [x] `/` без авторизации → 200 OK (страница входа)
- [x] `/chat` без авторизации → 200 OK
- [x] `/api/v1/health` без авторизации → 200 OK
- [x] `/tenant/houses` без авторизации → 307 redirect на `/`
- [x] `/dashboard` без авторизации → 307 redirect на `/`
- [x] ESLint проходит без ошибок

## Результат

✅ Middleware теперь корректно различает публичные и защищённые маршруты:
- Точное совпадение для корня (`/`)
- Префиксное matching для `/chat` и `/api`
- Редирект неавторизованных пользователей на страницу входа
- Ролевая защита для `/tenant/*` и `/dashboard/*`
