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

- In-memory (dict) для MVP — без БД
- Состояние теряется при перезапуске

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

- Префикс: `/api/v1/`
- RESTful ресурсы: `GET /bookings`, `POST /bookings`, `GET /bookings/{id}`
- Фильтры через query params: `GET /bookings?user_id=123&status=active`
- Пагинация: `limit`/`offset` или `page`/`page_size`
- Error response формат:
  ```json
  {
    "error": "validation_error",
    "message": "Invalid input data",
    "details": [{"field": "check_in", "msg": "must be in the future"}]
  }
  ```
