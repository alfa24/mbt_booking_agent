# План: Реализация API для frontend + вынос LLM в backend

## Цель
Реализовать полноценный API для frontend и перенести LLM-логику из бота в backend для централизованного управления.

## Состав работ

### Часть 1: Вынос LLM-сервиса в backend
- [x] Создать `backend/services/llm.py` с абстракцией LLMClient
- [x] Реализовать RouterAIClient для OpenAI-compatible API
- [x] Реализовать LLMService с поддержкой system prompt и контекста
- [x] Добавить LLM env-переменные в `backend/config.py`

### Часть 2: Новые модели
- [x] Создать `backend/models/chat.py` (Chat, ChatMessage)
- [x] Создать `backend/models/consumable_note.py` (ConsumableNote)
- [x] Обновить `backend/models/__init__.py`

### Часть 3: Схемы
- [x] Создать `backend/schemas/chat.py`
- [x] Создать `backend/schemas/consumable_note.py`
- [x] Создать `backend/schemas/dashboard.py`
- [x] Обновить `backend/schemas/__init__.py`

### Часть 4: Репозитории и сервисы
- [x] Создать `backend/repositories/chat.py`
- [x] Создать `backend/repositories/consumable_note.py`
- [x] Обновить `backend/repositories/__init__.py`
- [x] Создать `backend/services/chat.py`
- [x] Создать `backend/services/consumable_note.py`
- [x] Создать `backend/services/dashboard.py`

### Часть 5: API роутеры
- [x] Создать `backend/api/chat.py`
- [x] Создать `backend/api/dashboard.py`
- [x] Создать `backend/api/consumable_notes.py`
- [x] Обновить `backend/api/__init__.py`

### Часть 6: Рефакторинг бота
- [x] Добавить методы `create_chat` и `send_chat_message` в `bot/services/backend_client.py`
- [x] Обновить `bot/services/llm.py` для работы через backend API
- [x] Обновить `bot/handlers/message.py` для использования backend chat API
- [x] Обновить `bot/main.py` для передачи backend клиента в LLMService

### Часть 7: Миграции Alembic
- [x] Создать миграцию для таблиц chats и chat_messages
- [x] Создать миграцию для таблицы consumable_notes
- [x] Создать миграцию с demo данными (дома, тарифы, бронирования, заметки)

### Часть 8: Тесты
- [x] Создать `backend/tests/test_chat.py`
- [x] Создать `backend/tests/test_consumable_notes.py`
- [x] Создать `backend/tests/test_dashboard.py`
- [x] Обновить `backend/tests/conftest.py` для очистки новых таблиц

### Часть 9: Документация
- [x] Создать `docs/tasks/task-01-frontend-api/plan.md`
- [x] Создать `docs/tasks/task-01-frontend-api/summary.md`

## Новые endpoints

### Chat API
- `POST /api/v1/chats` - создание чата (201)
- `GET /api/v1/chats/{chat_id}/messages` - история сообщений (200)
- `POST /api/v1/chats/{chat_id}/messages` - отправка сообщения (201)

### Dashboard API
- `GET /api/v1/dashboard/owner` - KPI для владельца (200)
- `GET /api/v1/dashboard/leaderboard` - агрегации (200)
- `GET /api/v1/dashboard/houses/{house_id}/stats?period=` - статистика дома (200)

### Consumable Notes API
- `GET /api/v1/consumable-notes?house_id=` - список заметок (200)
- `POST /api/v1/consumable-notes` - создание заметки (201)
- `PATCH /api/v1/consumable-notes/{id}` - обновление (200)
- `DELETE /api/v1/consumable-notes/{id}` - удаление (204)

## Архитектура

```
┌─────────────┐     HTTP      ┌─────────────────────────────────────┐
│   Telegram  │ ◄────────────►│           Backend API               │
│    Bot      │               │  ┌─────────┐ ┌─────────┐ ┌────────┐ │
└─────────────┘               │  │  Chat   │ │Consumable│ │Dashboard│ │
                              │  │ Service │ │ Notes   │ │ Service│ │
                              │  └────┬────┘ └────┬────┘ └────────┘ │
                              │       │           │                 │
                              │  ┌────┴────┐ ┌────┴────┐            │
                              │  │ChatRepo │ │NoteRepo │            │
                              │  └────┬────┘ └────┬────┘            │
                              │       │           │                 │
                              │  ┌────┴───────────┴────┐            │
                              │  │    LLM Service      │            │
                              │  │  (RouterAIClient)   │            │
                              │  └─────────────────────┘            │
                              └─────────────────────────────────────┘
```

## Зависимости
- `openai` SDK для LLM
- SQLAlchemy 2.0 для работы с БД
- Alembic для миграций
