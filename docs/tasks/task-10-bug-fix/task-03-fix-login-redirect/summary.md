# Task 03: Исправить login redirect по роли

## Проблема

После успешного логина **все** пользователи редиректились на `/dashboard`:

```typescript
router.push("/dashboard")  // НЕПРАВИЛЬНО для tenant
```

Tenant пользователи должны попадать на `/tenant/houses`, а не на owner dashboard.

## Решение

Добавил проверку роли пользователя перед редиректом:

**Было:**
```typescript
if (user) {
  login(user)
  toast.success("Успешный вход")
  router.push("/dashboard")  // Все идут на dashboard
}
```

**Стало:**
```typescript
if (user) {
  login(user)
  toast.success("Успешный вход")
  
  // Redirect based on user role
  if (user.role === "tenant") {
    router.push("/tenant/houses")
  } else {
    // owner или both → dashboard
    router.push("/dashboard")
  }
}
```

## Логика редиректа

| Роль | Куда редиректит | Обоснование |
|------|----------------|-------------|
| `tenant` | `/tenant/houses` | Каталог домов для бронирования |
| `owner` | `/dashboard` | Панель управления объектами |
| `both` | `/dashboard` | По умолчанию owner функционал |

## Definition of Done (самопроверка)

- [x] Tenant после логина → `/tenant/houses`
- [x] Owner после логина → `/dashboard`
- [x] Both после логина → `/dashboard`
- [x] ESLint проходит без ошибок
- [x] Нет ошибок TypeScript

## Результат

✅ Login страница теперь корректно распределяет пользователей по ролям:
- Tenant видят каталог домов для бронирования
- Owner видят панель управления с KPI
- Соответствует user scenarios из spec
