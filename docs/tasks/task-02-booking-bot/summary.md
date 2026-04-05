# Summary: Function Calling для бота бронирования

## Реализовано

### 1. Новый файл: `backend/services/llm_tools.py`
- Определения 5 инструментов для OpenAI-compatible API:
  - `list_available_houses` — получить список активных домов
  - `check_availability` — проверить доступность дома на даты
  - `create_booking` — создать бронирование
  - `cancel_booking` — отменить бронирование
  - `get_my_bookings` — получить бронирования пользователя
- `BookingToolExecutor` — класс для выполнения tools через существующие сервисы
- `execute_tool_call()` — функция для dispatch tool calls

### 2. Обновлён: `backend/services/llm.py`
- `RouterAIClient.chat()` теперь возвращает `tool_calls` из ответа LLM
- `LLMService.process_message()` реализует цикл обработки tool calls:
  1. Отправляет сообщение с tools
  2. Если есть tool_calls — выполняет функции через executor
  3. Добавляет результаты в сообщения
  4. Повторяет до получения финального ответа
- Добавлен параметр `tool_executor` в `process_message()`
- Ограничение на 10 итераций цикла (MAX_TOOL_ITERATIONS)

### 3. Обновлён: `backend/services/chat.py`
- Инъекция `BookingService`, `HouseService`, `TariffRepository`
- Метод `_create_tool_executor()` для создания executor с user_id
- `send_message()` передаёт tool_executor в LLMService

### 4. Обновлён: `backend/config.py`
- Новый системный промпт для работы с tools
- Убран JSON-формат ответа (теперь используется function calling)
- Инструкции по использованию инструментов

## Архитектура

```
User Message
    ↓
ChatService.send_message()
    ↓
LLMService.process_message(tool_executor=...)
    ↓
RouterAIClient.chat(tools=BOOKING_TOOLS)
    ↓
Tool Calls? ──→ BookingToolExecutor → Tools → Services → Repositories
    ↓                                                    ↓
Final Response ←──────────────────────────────────── Tool Results
```

## Используемые сервисы

| Tool | Сервис |
|------|--------|
| list_available_houses | HouseService.list_houses() |
| check_availability | HouseService.get_house_calendar() |
| create_booking | BookingService.create_booking() |
| cancel_booking | BookingService.cancel_booking() |
| get_my_bookings | BookingService.list_bookings() |

## Тесты

Все 126 тестов прошли успешно после изменений.

## Файлы

- Создан: `backend/services/llm_tools.py`
- Изменён: `backend/services/llm.py`
- Изменён: `backend/services/chat.py`
- Изменён: `backend/config.py`
- Создан: `docs/tasks/task-02-booking-bot/plan.md`
