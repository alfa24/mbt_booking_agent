---
name: conventions
trigger: always_on
---

# Конвенции разработки

> Полное видение проекта: [`docs/vision.md`](file:///work/python/fullstack_homework/project/docs/vision.md)

## Код

- **KISS** — минимум сложности, только необходимое для MVP
- **Один класс — один файл** — строгое следование принципу
- **Явное лучше неявного** — никакого хардкода секретов, всё через env
- **Pydantic** для валидации всех входных данных и конфигурации

## Структура

```
bot/
├── main.py        # Точка входа
├── config.py      # Pydantic-конфиг
├── handlers/      # Обработчики aiogram
├── services/      # Бизнес-логика (LLM, бронирование)
└── models/        # Pydantic-модели
```

## Зависимости

- `uv` для управления зависимостями
- `make` для автоматизации (install, run, lint, format)
- Никаких лишних библиотек

## LLM

- Провайдер: **RouterAI** (OpenAI-compatible)
- Клиент: `openai` SDK с кастомным `base_url`
- Системный промпт задаёт роль бота

## Хранение

- **PostgreSQL** — основная база данных (SQLAlchemy 2.0 + asyncpg)
- **Alembic** — миграции базы данных
- In-memory только для кэширования (при необходимости)

## Конфигурация

- Все секреты в `.env`
- `.env.example` — шаблон в репозитории
- Pydantic-модель для валидации env-переменных

## Backend

> Архитектура: [ADR-002: Backend Framework](../../docs/adr/adr-002-backend-framework.md)

### Структура

```
backend/
├── main.py           # Точка входа, FastAPI app
├── config.py         # Pydantic-settings конфигурация
├── dependencies.py   # Dependency injection
├── api/              # Роутеры (endpoints)
│   ├── health.py
│   ├── bookings.py
│   ├── houses.py
│   ├── users.py
│   └── tariffs.py
├── schemas/          # Pydantic-схемы (request/response)
│   ├── user.py
│   ├── house.py
│   ├── booking.py
│   ├── tariff.py
│   └── common.py
├── models/           # SQLAlchemy модели
│   ├── user.py
│   ├── house.py
│   ├── booking.py
│   └── tariff.py
├── services/         # Бизнес-логика
│   ├── booking.py
│   ├── house.py
│   └── user.py
└── database.py       # Подключение к PostgreSQL
```

### Паттерны

- **Dependency Injection** — через `Depends()` FastAPI
- **Repository Pattern** — слой доступа к данным в `repositories/` (при необходимости)
- **Service Layer** — бизнес-логика отделена от роутеров
- **Pydantic Schemas** — валидация на границах API

### Naming Conventions

| Компонент | Паттерн | Пример |
|-----------|---------|--------|
| Роутер | `{resource}_router` | `bookings_router` |
| Схема запроса | `{Action}{Resource}Request` | `CreateBookingRequest` |
| Схема ответа | `{Resource}Response` | `BookingResponse` |
| Модель SQLAlchemy | `{Resource}` | `Booking` |
| Сервис | `{Resource}Service` | `BookingService` |

### API Conventions

- **Версионирование:** `/api/v1/` префикс для всех endpoints
- **RESTful ресурсы:**
  - `GET /bookings` — список с фильтрами
  - `POST /bookings` — создание
  - `GET /bookings/{id}` — получение по ID
  - `PATCH /bookings/{id}` — частичное обновление
  - `DELETE /bookings/{id}` — удаление/отмена
- **Фильтры:** через query params: `GET /bookings?user_id=123&status=confirmed`
- **Пагинация:** `limit`/`offset` (default: limit=100, offset=0)

### HTTP Status Codes

| Код | Когда использовать |
|-----|-------------------|
| 200 OK | Успешный GET, PATCH |
| 201 Created | Успешный POST |
| 204 No Content | Успешный DELETE |
| 400 Bad Request | Невалидные данные (валидация Pydantic) |
| 404 Not Found | Ресурс не найден |
| 422 Unprocessable Entity | Ошибки валидации с деталями |
| 500 Internal Server Error | Внутренняя ошибка сервера |

### Error Response Format

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "check_in"],
      "msg": "check_in must be before check_out",
      "input": "2024-06-10"
    }
  ]
}
```

### Запуск и разработка

**Все операции через Docker:**

```bash
# Запуск инфраструктуры
make postgres-up

# Применение миграций
make migrate

# Запуск backend
make run-backend

# Запуск тестов
make test-backend

# Линтинг
make lint-backend
```
