# Summary: Требования к UI и API-контракты

## Что было сделано

Создана документация для frontend-разработки системы бронирования:

### 1. ui-requirements.md
Функциональные требования для 4 зон интерфейса:

- **Панель арендодателя (Dashboard)** — KPI-карточки, графики, CRUD для домов/бронирований/тарифов/расходников
- **Лидерборд (/leaderboard)** — таблица/календарь с фильтрами, график доходности, экспорт CSV
- **Глобальный чат (виджет)** — плавающая кнопка, Sheet с чатом, polling, оптимистичное обновление
- **Полноэкранный чат (/chat)** — двухколоночный layout, список диалогов, группировка сообщений по дате

Также описан механизм авторизации через Telegram username с сохранением в Zustand store.

### 2. ui-style-guide.md
Гайд по стилю интерфейса:

- Цветовая палитра через CSS variables (primary — зелёный, accent — песочный)
- Типографика (Inter, шкала размеров)
- Tailwind CSS v4 паттерны (`@theme inline`, `gap-*`, `size-*`)
- shadcn/ui конвенции (семантические цвета)
- Формы и валидация (`data-invalid`, `aria-invalid`)
- Toast-уведомления (sonner)
- Accessibility (Dialog/Sheet с Title, `data-icon`)

### 3. api-contracts.md (обновлён)
Добавлены новые endpoint'ы:

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/v1/dashboard/owner` | GET | KPI: total_bookings, total_revenue, occupancy_rate, active_bookings, monthly_revenue[] |
| `/api/v1/dashboard/leaderboard` | GET | bookings_by_month, revenue_by_house |
| `/api/v1/houses/{id}/stats` | GET | occupancy_rate, total_revenue, total_bookings за период |
| `/api/v1/consumable-notes` | GET | Список заметок (фильтр house_id) |
| `/api/v1/consumable-notes` | POST | Создание заметки |
| `/api/v1/consumable-notes/{id}` | PATCH | Обновление заметки |
| `/api/v1/consumable-notes/{id}` | DELETE | Удаление заметки |
| `/api/v1/chats` | POST | Создание нового чата (возвращает chat_id) |
| `/api/v1/chats/{id}/messages` | GET | История сообщений (cursor-based: ?cursor=...&limit=50) |
| `/api/v1/chats/{id}/messages` | POST | Отправка сообщения → LLM → ответ |

Для каждого endpoint описаны: request body/params, response schema, HTTP status codes.

## Артефакты

- `docs/tasks/task-00-ui-requirements/plan.md`
- `docs/tasks/task-00-ui-requirements/ui-requirements.md`
- `docs/tasks/task-00-ui-requirements/ui-style-guide.md`
- `docs/tasks/task-00-ui-requirements/summary.md` (этот файл)
- Обновлённый `docs/tech/api-contracts.md`
