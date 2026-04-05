# План: Ролевые интерфейсы tenant/owner

## Цель
Создать разделённые интерфейсы для арендатора (tenant) и арендодателя (owner) с middleware для контроля доступа.

## Состав работ

### 1. Создать tenant-страницы

#### 1.1 `/tenant/houses/page.tsx` — каталог домов
- Список активных домов карточками
- Информация: название, описание, вместимость
- Кнопка "Подробнее" для перехода к деталям

#### 1.2 `/tenant/houses/[id]/page.tsx` — детали дома
- Полная информация о доме
- Календарь занятости (занятые даты)
- Кнопка "Забронировать" → переход на создание бронирования

#### 1.3 `/tenant/bookings/page.tsx` — мои бронирования
- Список бронирований текущего пользователя
- Фильтры по статусу (tabs)
- Кнопка отмены для активных бронирований

#### 1.4 `/tenant/bookings/new/page.tsx` — создание бронирования
- Выбор дома (dropdown или предзаполнено)
- Выбор дат заезда/выезда
- Выбор состава гостей (тарифы + количество)
- Расчёт стоимости
- Подтверждение

### 2. Создать hooks

#### 2.1 `use-houses-catalog.ts`
- Загрузка списка домов (только активные)
- TanStack Query

#### 2.2 `use-house-details.ts`
- Детали дома по ID
- Календарь занятости (через API /houses/{id}/calendar)

#### 2.3 `use-create-booking.ts`
- Мутация создания бронирования
- Инвалидация кэша bookings

### 3. Создать middleware

#### 3.1 `web/src/middleware.ts`
- Проверка роли из cookie
- Редиректы:
  - /dashboard, /leaderboard → только owner (tenant → /tenant/houses)
  - /tenant/* → только tenant (owner → /dashboard)
  - /chat — доступно обоим
  - / (root) → owner: /dashboard, tenant: /tenant/houses

#### 3.2 Обновить auth store
- Сохранять role в cookie при логине
- Очищать cookie при логауте

### 4. Обновить навигацию

#### 4.1 Sidebar
- tenantNavItems: /tenant/houses, /tenant/bookings, /chat
- ownerNavItems: /dashboard, /houses, /bookings, /leaderboard, /chat

## Артефакты

### Файлы для создания:
1. `web/src/app/(authenticated)/tenant/houses/page.tsx`
2. `web/src/app/(authenticated)/tenant/houses/[id]/page.tsx`
3. `web/src/app/(authenticated)/tenant/bookings/page.tsx`
4. `web/src/app/(authenticated)/tenant/bookings/new/page.tsx`
5. `web/src/hooks/use-houses-catalog.ts`
6. `web/src/hooks/use-house-details.ts`
7. `web/src/hooks/use-create-booking.ts`
8. `web/src/middleware.ts`

### Файлы для обновления:
1. `web/src/store/auth.ts` — добавить cookie
2. `web/src/components/layout/sidebar.tsx` — обновить пути

## Технические детали

### API Endpoints
- GET /api/v1/houses — список домов
- GET /api/v1/houses/{id} — детали дома
- GET /api/v1/houses/{id}/calendar — календарь
- GET /api/v1/bookings?user_id={id} — бронирования пользователя
- POST /api/v1/bookings — создание
- PATCH /api/v1/bookings/{id}/cancel — отмена
- GET /api/v1/tariffs — тарифы для расчёта

### Компоненты shadcn/ui
- Card, CardHeader, CardContent, CardTitle, CardDescription
- Button
- Badge
- Table
- Tabs
- Calendar (date-fns)
- Select
- Dialog
- Skeleton
