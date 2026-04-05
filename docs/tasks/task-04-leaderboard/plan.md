# План: Страница Лидерборд (Task 04)

## Цель
Реализация страницы Leaderboard с табличным и календарным представлением бронирований, графиком выручки и экспортом CSV.

## Архитектура

### API Endpoints
- `GET /api/v1/dashboard/leaderboard` — данные лидерборда (LeaderboardResponse)
- `GET /api/v1/bookings?house_id=...&status=...` — бронирования с фильтрами

### Файлы

#### Hooks
- `web/src/hooks/use-leaderboard.ts` — `useLeaderboardData()` для получения данных лидерборда

#### Компоненты (`web/src/components/leaderboard/`)
1. `view-toggle.tsx` — Tabs компонент для переключения Таблица/Календарь
2. `bookings-table.tsx` — таблица бронирований (расширенная версия из dashboard)
3. `calendar-view.tsx` — календарное представление (CSS Grid, строки=дома, столбцы=дни)
4. `revenue-chart.tsx` — график выручки по домам (recharts BarChart)
5. `csv-export-button.tsx` — кнопка экспорта в CSV
6. `filters.tsx` — фильтры по дому, периоду, статусу

#### Страница
- `web/src/app/(authenticated)/leaderboard/page.tsx` — Server Component с начальной загрузкой

## Детали реализации

### LeaderboardResponse (из backend/schemas/dashboard.py)
```typescript
interface RevenueByHouse {
  house_id: number
  house_name: string
  revenue: number
}

interface BookingsByMonth {
  month: string
  count: number
}

interface LeaderboardResponse {
  bookings_by_month: BookingsByMonth[]
  revenue_by_house: RevenueByHouse[]
}
```

### Calendar View
- CSS Grid без внешних библиотек
- Навигация по месяцам (стрелки + заголовок)
- Строки = дома (house_name)
- Столбцы = дни месяца
- Badge для бронирований:
  - `variant="default"` = confirmed
  - `variant="secondary"` = pending
  - `variant="outline"` = completed

### CSV Export
- Клиентская генерация через Blob
- Колонки: ID, Дом, Заезд, Выезд, Статус, Сумма

## Конвенции
- shadcn Tabs, Select, Button, Badge, Card, Table
- `gap-*` вместо `space-y-*`
- `size-*` для квадратных элементов
- `cn()` для условных классов
- sonner для тостов
