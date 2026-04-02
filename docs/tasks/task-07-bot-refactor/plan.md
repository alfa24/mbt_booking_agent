# План итерации: Рефакторинг бота для работы через API

## Цель
Перевести Telegram-бот с прямой логики и in-memory хранения на работу через backend API.

## Артефакты
- `bot/services/backend_client.py` — HTTP-клиент для API
- Обновленные `bot/handlers/message.py`
- Удаленные `bot/services/booking.py`, `bot/models/booking.py`
- Обновленные `bot/config.py`, `bot/main.py`
- `docs/integrations.md` — обновленная схема
- `README.md` — инструкции по запуску

---

## Task 1: Создание HTTP-клиента backend API

**Файлы:**
- Создать `bot/services/backend_client.py`

**Требования:**
- Использовать `httpx.AsyncClient` для async HTTP-запросов
- Базовый URL backend из env (`BACKEND_API_URL=http://backend:8000`)
- Методы:
  - `get_bookings(user_id)` — получить бронирования пользователя
  - `create_booking(data)` — создать бронирование
  - `cancel_booking(booking_id)` — отменить бронирование
  - `update_booking(booking_id, data)` — обновить бронирование
  - `get_houses()` — получить список домов
  - `get_house_calendar(house_id)` — получить календарь дома
- Обработка ошибок API (4xx, 5xx) с понятными сообщениями
- Таймауты и retry-логика для resilience

**Конфигурация:**
- Добавить в `bot/config.py`: `backend_api_url: str = "http://backend:8000"`

---

## Task 2: Рефакторинг bot/handlers/message.py

**Изменения:**
- Заменить `BookingService` на `BackendClient`
- Обновить `_create_booking()` — вызывать API вместо локального сервиса
- Обновить `_cancel_booking()` — вызывать API
- Обновить `_update_booking()` — вызывать API
- Обновить `cmd_bookings()` — получать список через API
- Обновить `handle_message()` — передавать `backend_client` в `_execute_action()`
- Удалить `format_context()` — больше не нужен, LLM получает данные иначе

**Важно:**
- Сохранить логику парсинга ответа LLM
- Сохранить обработку ошибок и валидацию
- Обновить системный промпт — убрать упоминание "хранится в памяти бота"

---

## Task 3: Обновление bot/main.py

**Изменения:**
- Заменить `BookingService()` на `BackendClient()` в DI
- Удалить импорты `BookingService`
- Добавить импорт `BackendClient`

---

## Task 4: Удаление in-memory кода

**Удалить файлы:**
- `bot/services/booking.py`
- `bot/models/booking.py`

**Обновить:**
- `bot/services/__init__.py` — убрать экспорты
- `bot/models/__init__.py` — убрать экспорты

---

## Task 5: Обновление конфигурации

**bot/config.py:**
- Добавить `backend_api_url: str = "http://backend:8000"`
- Обновить системный промпт — убрать "всё хранится в памяти бота"

**.env.example:**
- Добавить `BACKEND_API_URL=http://backend:8000`

---

## Task 6: Тестирование в Docker

**Команды:**
```bash
# Запуск инфраструктуры
docker compose up -d postgres
make migrate

# Запуск backend
make run-backend

# Проверка API доступен
curl http://localhost:8001/api/v1/health

# Запуск бота (в отдельном терминале)
make run
```

**Проверки:**
1. Backend отвечает на `/health`
2. Создание бронирования через API работает
3. Бот запускается без ошибок
4. Бот подключается к backend

---

## Task 7: Ревью кода через /fastapi-templates

**Действия:**
1. Вызвать `/fastapi-templates` skill
2. Предоставить измененные файлы:
   - `bot/services/backend_client.py`
   - `bot/handlers/message.py`
   - `bot/main.py`
3. Применить замечания по:
   - Структуре async-кода
   - Обработке ошибок
   - Таймаутам и resilience
   - Типизации

---

## Task 8: Ревью тестов через /python-testing-patterns

**Действия:**
1. Вызвать `/python-testing-patterns` skill
2. Предоставить тесты (если есть) или запросить рекомендации по тестированию HTTP-клиента
3. Применить замечания

---

## Task 9: Актуализация документации

**docs/integrations.md:**
- Обновить схему Mermaid — добавить связь BOT -> BACKEND API
- Добавить описание взаимодействия бота с backend

**README.md:**
- Добавить инструкции по запуску обоих сервисов
- Обновить переменные окружения

---

## Task 10: Создание plan.md и актуализация summary/tasklist

**Создать:**
- `docs/tasks/task-07-bot-refactor/plan.md` — сохранить этот план
- `docs/tasks/task-07-bot-refactor/summary.md` — результаты выполнения

**Обновить:**
- `docs/tasks/tasklist-backend.md` строки 387-402 — отметить выполненные пункты

---

## Definition of Done

- [ ] HTTP-клиент создан и работает
- [ ] Handlers используют API вместо in-memory
- [ ] In-memory код удален
- [ ] Бот запускается в Docker
- [ ] End-to-end тест проходит: сообщение -> бот -> backend -> БД
- [ ] Код прошел ревью /fastapi-templates
- [ ] Тесты прошли ревью /python-testing-patterns
- [ ] Документация обновлена
- [ ] Summary создан, tasklist обновлен
