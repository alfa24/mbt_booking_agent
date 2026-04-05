# Summary: Ролевые интерфейсы tenant/owner

## Что реализовано

### 1. Tenant-страницы

#### `/tenant/houses/page.tsx`
- Каталог доступных домов (только активные)
- Карточки с названием, описанием, вместимостью
- Кнопка "Подробнее" для перехода к деталям

#### `/tenant/houses/[id]/page.tsx`
- Детальная информация о доме
- Календарь занятости на 3 месяца (зелёный = свободно, красный = занято)
- Кнопка "Забронировать" с переходом на форму

#### `/tenant/bookings/page.tsx`
- Список бронирований текущего пользователя
- Фильтры по статусу (Tabs: Все, Ожидают, Подтверждены, Завершены, Отменены)
- Кнопка отмены для активных бронирований

#### `/tenant/bookings/new/page.tsx`
- Форма создания бронирования
- Выбор дома (или предзаполнено из query param)
- Выбор дат заезда/выезда (с валидацией)
- Выбор состава гостей (тарифы + количество)
- Автоматический расчёт стоимости

### 2. Hooks

#### `use-houses-catalog.ts`
- `useHousesCatalog()` — загрузка активных домов

#### `use-house-details.ts`
- `useHouseDetails(id)` — детали дома
- `useHouseCalendar(id)` — календарь занятости

#### `use-tenant-bookings.ts`
- `useUserBookings(userId)` — бронирования пользователя
- `useCreateBooking()` — создание бронирования
- `useCancelBooking()` — отмена бронирования

### 3. Middleware

#### `middleware.ts`
- Проверка роли из cookie `user_role`
- Редиректы:
  - `/dashboard`, `/leaderboard`, `/houses`, `/bookings` → только owner (tenant → `/tenant/houses`)
  - `/tenant/*` → только tenant (owner → `/dashboard`)
  - `/chat` — доступно обоим
  - `/` (root) → tenant: `/tenant/houses`, owner: `/dashboard`

### 4. Обновления

#### `auth.ts`
- Добавлено сохранение `user_role` и `user_id` в cookies при логине
- Очистка cookies при логауте

#### `sidebar.tsx`
- `ownerNavItems` обновлены: `/dashboard/houses`, `/dashboard/bookings`
- `tenantNavItems` обновлены: `/tenant/houses`, `/tenant/bookings`

## Файлы

### Созданы:
- `web/src/app/(authenticated)/tenant/houses/page.tsx`
- `web/src/app/(authenticated)/tenant/houses/[id]/page.tsx`
- `web/src/app/(authenticated)/tenant/bookings/page.tsx`
- `web/src/app/(authenticated)/tenant/bookings/new/page.tsx`
- `web/src/hooks/use-houses-catalog.ts`
- `web/src/hooks/use-house-details.ts`
- `web/src/hooks/use-tenant-bookings.ts`
- `web/src/middleware.ts`
- `docs/tasks/task-03-role-interfaces/plan.md`
- `docs/tasks/task-03-role-interfaces/summary.md`

### Обновлены:
- `web/src/store/auth.ts`
- `web/src/components/layout/sidebar.tsx`

## Технологии
- Next.js 15 App Router
- TypeScript
- TanStack Query
- shadcn/ui (Card, Button, Badge, Tabs, Select, Input, Label, Skeleton)
- date-fns для работы с датами
- ky для HTTP-запросов
