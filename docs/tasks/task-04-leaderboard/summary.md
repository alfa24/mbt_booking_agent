# Summary: Страница Лидерборд (Task 04)

## Реализовано

### Hooks
- `web/src/hooks/use-leaderboard.ts` — hook для получения данных лидерборда с API `/dashboard/leaderboard`

### Компоненты (`web/src/components/leaderboard/`)
1. `view-toggle.tsx` — Tabs для переключения между табличным и календарным видом
2. `filters.tsx` — фильтры по дому и статусу бронирования
3. `bookings-table.tsx` — расширенная таблица бронирований с колонкой суммы
4. `calendar-view.tsx` — календарное представление (CSS Grid):
   - Строки = дома
   - Столбцы = дни месяца
   - Badge с цветовой индикацией статуса
   - Навигация по месяцам
5. `revenue-chart.tsx` — график выручки по домам (recharts BarChart)
6. `csv-export-button.tsx` — клиентский экспорт бронирований в CSV

### Страница
- `web/src/app/(authenticated)/leaderboard/page.tsx` — полная реализация с:
  - Переключением видов (таблица/календарь)
  - Фильтрами по дому и статусу
  - Графиком выручки
  - Экспортом CSV

## Используемые технологии
- shadcn/ui: Tabs, Select, Button, Badge, Card, Table, ScrollArea
- date-fns для работы с датами
- recharts для графиков
- TanStack Query для загрузки данных

## API Endpoints
- `GET /api/v1/dashboard/leaderboard` — данные лидерборда
- `GET /api/v1/bookings?house_id=...&status=...` — бронирования с фильтрами

## Конвенции
- Соблюдены все конвенции shadcn/ui
- Использован `gap-*` вместо `space-y-*`
- `size-*` для квадратных элементов
- `cn()` для условных классов
- `data-icon` на иконках в Button
