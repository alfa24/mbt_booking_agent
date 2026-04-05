# План: Панель арендодателя (Dashboard)

## Цель
Создать полноценную панель управления для арендодателя с KPI, управлением домами, бронированиями, тарифами и заметками по расходникам.

## Состав работ

### 1. Dashboard KPI страница
- Server Component для загрузки данных с API
- 4 KPI-карточки: total_bookings, total_revenue, occupancy_rate, active_bookings
- График доходности с Suspense boundary
- Fallback на mock-данные при недоступности API

### 2. TanStack Query hooks
Создать hooks в `src/hooks/`:
- `use-dashboard.ts` — useOwnerDashboard(), useHouseStats()
- `use-houses.ts` — useHouses(), useCreateHouse(), useUpdateHouse(), useDeleteHouse()
- `use-bookings.ts` — useBookings(filters), useUpdateBooking(), useCancelBooking()
- `use-tariffs.ts` — useTariffs(), useCreateTariff(), useUpdateTariff(), useDeleteTariff()
- `use-consumables.ts` — useConsumableNotes(), useCreateNote(), useUpdateNote(), useDeleteNote()

### 3. Подстраницы Dashboard
Создать файловую структуру:
```
src/app/(authenticated)/dashboard/
├── page.tsx           # KPI + график
├── layout.tsx         # Tabs навигация
├── loading.tsx        # Skeleton
├── error.tsx          # Error boundary
├── houses/
│   ├── page.tsx
│   ├── loading.tsx
│   └── error.tsx
├── bookings/
│   ├── page.tsx
│   ├── loading.tsx
│   └── error.tsx
├── tariffs/
│   ├── page.tsx
│   ├── loading.tsx
│   └── error.tsx
└── consumables/
    ├── page.tsx
    ├── loading.tsx
    └── error.tsx
```

### 4. Dashboard layout
- Tabs навигация с 5 вкладками
- Подсветка активной вкладки через pathname
- Link + usePathname для навигации

### 5. Компоненты
Создать в `src/components/dashboard/`:
- `kpi-cards.tsx` — 4 карточки KPI
- `revenue-chart.tsx` — график доходов (recharts)
- `houses-table.tsx` — таблица домов
- `house-form-dialog.tsx` — форма создания/редактирования дома
- `bookings-table.tsx` — таблица бронирований с фильтрами
- `booking-detail-dialog.tsx` — детали бронирования (Sheet)
- `tariffs-list.tsx` — список тарифов
- `tariff-form-dialog.tsx` — форма тарифа
- `consumables-list.tsx` — список заметок по домам
- `consumable-form-dialog.tsx` — форма заметки

### 6. UI компоненты
Добавить shadcn компоненты:
- table, dialog, sheet, tabs, select, badge, textarea, separator, scroll-area

## Технологии
- Next.js 15 App Router
- React Server Components
- TanStack Query
- shadcn/ui + Radix UI
- recharts для графиков
- ky для HTTP-запросов
- sonner для уведомлений

## Конвенции
- Server Components по умолчанию
- 'use client' только для интерактивности
- gap-* вместо space-y-*
- size-* для квадратных элементов
- Семантические цвета
- cn() для условных классов
- data-icon на иконках в Button
