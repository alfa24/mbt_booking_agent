# Plan: Исправить middleware PUBLIC_ROUTES логику

## Проблема

Middleware использует `pathname.startsWith(route)` для PUBLIC_ROUTES `["/", "/chat", "/api"]`. Поскольку ВСЕ пути начинаются с `/`, проверка всегда возвращает true и middleware пропускает все запросы без аутентификации.

**Файл:** `web/src/middleware.ts` строка 19

## Цель

Middleware должен корректно определять публичные маршруты:
- `/` — точное совпадение
- `/chat/*` — prefix match
- `/api/*` — prefix match

Все остальные маршруты должны требовать аутентификации.

## Состав работ

- [ ] Исправить логику PUBLIC_ROUTES в `web/src/middleware.ts`
  - Разделить exact match (`/`) и prefix match (`/api`, `/chat`)
  - Использовать корректную проверку для каждого типа маршрута
- [ ] Протестировать что публичные маршруты доступны без авторизации
  - `/` → доступен
  - `/chat` → доступен
  - `/api/v1/health` → доступен
- [ ] Протестировать что защищённые маршруты требуют авторизации
  - `/tenant/houses` → редирект на `/`
  - `/dashboard` → редирект на `/`
  - `/tenant/bookings` → редирект на `/`
- [ ] Проверить что существующие тесты проходят

## Definition of Done (самопроверка)

- [ ] `/` без авторизации → 200 OK (страница входа)
- [ ] `/chat` без авторизации → 200 OK
- [ ] `/api/v1/health` без авторизации → 200 OK
- [ ] `/tenant/houses` без авторизации → 307 redirect на `/`
- [ ] `/dashboard` без авторизации → 307 redirect на `/`
- [ ] `/tenant/bookings` без авторизации → 307 redirect на `/`
- [ ] Консоль браузера без ошибок middleware
- [ ] `make lint-frontend` проходит без ошибок

## Связанные файлы

- `web/src/middleware.ts` — исправить логику PUBLIC_ROUTES
- `web/src/app/(authenticated)/layout.tsx` — возможно потребуется cleanup после фикса middleware

## Spec Reference

- [screenflow.md#route-protection](../../specs/screenflow.md)
- [bug-report.md#bug-1](../bug-report.md#bug-1)

## Технические детали

### Текущий код (НЕПРАВИЛЬНО)

```typescript
const PUBLIC_ROUTES = ["/", "/chat", "/api"];

if (PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(route))) {
  return; // Пропускаем все запросы!
}
```

Проблема: `pathname.startsWith("/")` всегда true для любого пути.

### Исправленный код (ПРАВИЛЬНО)

```typescript
const PUBLIC_ROUTES = ["/", "/chat", "/api"];

const isPublicRoute = PUBLIC_ROUTES.some((route) => {
  // Exact match для "/"
  if (route === "/") {
    return pathname === "/";
  }
  // Prefix match для "/chat", "/api"
  return pathname.startsWith(route);
});

if (isPublicRoute) {
  return;
}
```

### Тестовые сценарии

| Path | Ожидаемый результат |
|------|---------------------|
| `/` | ✅ Public (exact match) |
| `/chat` | ✅ Public (prefix match) |
| `/chat/123` | ✅ Public (prefix match) |
| `/api/v1/health` | ✅ Public (prefix match) |
| `/tenant/houses` | ❌ Protected → redirect |
| `/dashboard` | ❌ Protected → redirect |
| `/tenant/bookings/42` | ❌ Protected → redirect |
