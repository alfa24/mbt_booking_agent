# Результат: Панель арендодателя (Dashboard)

## Что реализовано

### 1. Dashboard KPI страница (`src/app/(authenticated)/dashboard/page.tsx`)
- Server Component с fetch на сервере
- 4 KPI-карточки с форматированием чисел и валют
- График доходности с recharts
- Fallback на mock-данные при недоступности API

### 2. TanStack Query hooks (`src/hooks/`)
- `use-dashboard.ts` — useOwnerDashboard, useHouseStats
- `use-houses.ts` — CRUD операции для домов
- `use-bookings.ts` — фильтрация и управление бронированиями
- `use-tariffs.ts` — CRUD операции для тарифов
- `use-consumables.ts` — CRUD операции для заметок

### 3. Подстраницы Dashboard
Создана полная файловая структура:
```
src/app/(authenticated)/dashboard/
├── page.tsx
├── layout.tsx
├── loading.tsx
├── error.tsx
├── houses/page.tsx
├── bookings/page.tsx
├── tariffs/page.tsx
└── consumables/page.tsx
```

### 4. Dashboard layout (`src/app/(authenticated)/dashboard/layout.tsx`)
- Tabs навигация с 5 вкладками
- Подсветка активной вкладки через usePathname
- Интеграция с Link для навигации

### 5. Компоненты (`src/components/dashboard/`)
- `kpi-cards.tsx` — 4 карточки KPI с иконками
- `revenue-chart.tsx` — BarChart с recharts
- `houses-table.tsx` — таблица с CRUD
- `house-form-dialog.tsx` — форма дома
- `bookings-table.tsx` — таблица с фильтрами
- `booking-detail-dialog.tsx` — Sheet с деталями
- `tariffs-list.tsx` — список карточек
- `tariff-form-dialog.tsx` — форма тарифа
- `consumables-list.tsx` — группировка по домам
- `consumable-form-dialog.tsx` — форма заметки

### 6. UI компоненты (`src/components/ui/`)
Добавлены:
- dialog.tsx
- select.tsx
- tabs.tsx
- badge.tsx
- textarea.tsx
- table.tsx
- sheet.tsx
- separator.tsx
- scroll-area.tsx

## Архитектура

### Server Components
- `dashboard/page.tsx` — загрузка KPI на сервере

### Client Components
- Все таблицы и формы (требуют интерактивности)
- Все диалоги и sheet-компоненты

### Data Flow
1. Server Component загружает начальные данные
2. Client Components используют TanStack Query
3. Мутации с invalidateQueries и toast-уведомлениями

## API Integration
- `GET /api/v1/dashboard/owner` — KPI данные
- `GET /api/v1/houses` — список домов
- `GET /api/v1/bookings` — бронирования с фильтрами
- `GET /api/v1/tariffs` — тарифы
- `GET /api/v1/consumable-notes` — заметки

## Фичи
- Фильтрация бронирований по дому и статусу
- Группировка заметок по домам
- Форматирование дат (date-fns, ru locale)
- Форматирование валют (Intl.NumberFormat)
- Skeleton-загрузки
- Error boundaries
- Toast-уведомления при операциях
