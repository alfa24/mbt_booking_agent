# План: Function Calling для бота бронирования

## Цель
Добавить поддержку function calling в LLM-сервис для бронирования домов через чат.

## Архитектура

### Текущее состояние
- `LLMService.process_message()` отправляет сообщения в LLM и возвращает ответ
- `RouterAIClient.chat()` уже поддерживает параметр `tools`, но не возвращает `tool_calls`
- `ChatService.send_message()` вызывает LLM и сохраняет ответ
- Существующие сервисы: `BookingService`, `HouseService`, `TariffRepository`

### Изменения

#### 1. Новый файл: `backend/services/llm_tools.py`
Определения инструментов для LLM:
- `list_available_houses` — получить список активных домов
- `check_availability` — проверить доступность дома на даты
- `create_booking` — создать бронирование
- `cancel_booking` — отменить бронирование
- `get_my_bookings` — получить бронирования пользователя

#### 2. Обновление: `backend/services/llm.py`
- `RouterAIClient.chat()` — возвращать полный response с tool_calls
- `LLMService.process_message()` — цикл обработки tool_calls:
  1. Отправить сообщение с tools
  2. Если есть tool_calls — выполнить функции
  3. Отправить результаты обратно в LLM
  4. Повторять пока не будет финальный ответ

#### 3. Обновление: `backend/services/chat.py`
- `ChatService.send_message()` — передавать `user_id` в LLM processing
- Инжектировать `BookingService` и `HouseService` через Depends

#### 4. Обновление: `backend/config.py`
- Новый системный промпт с инструкциями о tools

#### 5. Обновление: `backend/dependencies.py`
- Провайдеры для `BookingService` и `HouseService` в LLMService

## Tools (OpenAI-compatible)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_available_houses",
            "description": "Получить список всех доступных для бронирования домов",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "check_availability",
            "description": "Проверить доступность дома на указанные даты",
            "parameters": {
                "type": "object",
                "properties": {
                    "house_id": {"type": "integer"},
                    "check_in": {"type": "string", "format": "date"},
                    "check_out": {"type": "string", "format": "date"}
                },
                "required": ["house_id", "check_in", "check_out"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Создать бронирование дома",
            "parameters": {
                "type": "object",
                "properties": {
                    "house_id": {"type": "integer"},
                    "check_in": {"type": "string", "format": "date"},
                    "check_out": {"type": "string", "format": "date"},
                    "guests_count": {"type": "integer", "minimum": 1}
                },
                "required": ["house_id", "check_in", "check_out", "guests_count"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Отменить бронирование по ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "integer"}
                },
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_bookings",
            "description": "Получить список бронирований текущего пользователя",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]
```

## Цикл обработки tool calls

```
1. Build messages (system + history + user)
2. Call LLM with tools
3. If response.has_tool_calls:
   a. For each tool_call:
      - Execute function with args
      - Add tool result to messages
   b. Go to step 2
4. Return final content
```

## Используемые существующие сервисы

| Tool | Сервис/Репозиторий |
|------|-------------------|
| list_available_houses | HouseService.list_houses(is_active=True) |
| check_availability | HouseService.get_house_calendar() |
| create_booking | BookingService.create_booking() |
| cancel_booking | BookingService.cancel_booking() |
| get_my_bookings | BookingService.list_bookings(user_id=...) |

## Зависимости

- `TariffRepository` нужен для создания бронирования (дефолтный тариф)
- `BookingRepository` доступен через `BookingService`
- `HouseRepository` доступен через `HouseService`

## Файлы

- Создать: `backend/services/llm_tools.py`
- Изменить: `backend/services/llm.py`
- Изменить: `backend/services/chat.py`
- Изменить: `backend/config.py`
- Изменить: `backend/dependencies.py`
