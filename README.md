# Система бронирования загородного жилья

Платформа для бронирования гостевых домов естественным языком. Telegram-бот и веб-приложение — клиенты единого backend API.

## О проекте

Организация загородного отдыха через переписки и таблицы — боль. Эта система заменяет их на естественный разговор: пользователь пишет *"Забронируй старый дом на следующие выходные, 6 человек"*, а система понимает, уточняет детали и фиксирует бронирование.

**Ключевые пользователи:**
- **Арендаторы (Tenants)** — бронируют дома, управляют своими бронированиями
- **Арендодатели (Owners)** — управляют календарём, тарифами, аналитикой и расходниками

**Реализованные компоненты:**
- ✅ Telegram-бот с естественноязыковым интерфейсом
- ✅ Backend API с бизнес-логикой и LLM-интеграцией
- ✅ Веб-приложение с dashboard, чатом, лидербордом и голосовым вводом
- ✅ Text-to-SQL для аналитических запросов

## Архитектура

Высокоуровневая схема системы:

```mermaid
graph TB
    subgraph Клиенты
        TG[Telegram-бот<br/>Python + aiogram]
        WEB[Веб-приложение<br/>Next.js 15 + React 19]
    end

    subgraph Backend API
        API[FastAPI + SQLAlchemy 2.0]
        LLM[LLM Service<br/>RouterAI]
    end

    subgraph Данные
        DB[(PostgreSQL 16)]
    end

    TG -->|HTTP| API
    WEB -->|HTTP| API
    API --> DB
    API -.-> LLM
```

📖 **Детальная архитектура:** [docs/architecture.md](docs/architecture.md)  
📖 **Техническое видение:** [docs/vision.md](docs/vision.md)  
📖 **Модель данных:** [docs/data-model.md](docs/data-model.md)

## Статус проекта

| Этап | Название | Статус |
|------|----------|--------|
| 0 | MVP Telegram-бот | ✅ Done |
| 1 | Backend API и база данных | ✅ Done |
| 2 | Веб-приложение для арендаторов | ✅ Done |
| 3 | Панель управления арендодателя | ✅ Done |
| 4 | Интеграции и автоматизация | 📋 Planned |

**Реализовано:**
- Telegram-бот с LLM-интерфейсом
- Backend API (Users, Houses, Bookings, Tariffs, Dashboard, Chat, Consumable Notes, Text-to-SQL)
- Tenant Dashboard с KPI и графиками
- Owner Dashboard с аналитикой
- Полноэкранный чат с LLM
- Leaderboard с календарём бронирований
- Voice input (Web Speech API)
- Text-to-SQL queries для аналитики
- Consumable Notes для учёта расходников

## Системные требования

| Зависимость | Версия | Назначение |
|-------------|--------|------------|
| Docker | 24+ | Контейнеризация всех сервисов |
| Docker Compose | 2.20+ | Оркестрация контейнеров |
| Python | 3.12+ | Backend и бот |
| Node.js | 20+ | Frontend |
| Make | любая | Автоматизация команд |

**Проверка версий:**
```bash
node --version    # v20+
python3 --version # 3.12+
docker --version  # 24+
make --version
```

## Быстрый старт (5 минут)

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd project
cp .env.example .env
```

Отредактируйте `.env` — добавьте токены:
- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather
- `ROUTERAI_API_KEY` — API ключ LLM провайдера

📖 **Подробный гид по получению токенов:** [docs/how-to-get-tokens.md](docs/how-to-get-tokens.md)

### 2. Запуск системы

```bash
# Запуск PostgreSQL
make postgres-up

# Применение миграций
make migrate

# Загрузка демо-данных (опционально)
make backend-fixtures

# Запуск backend
make run-backend

# Запуск frontend (в другом терминале)
make run-frontend

# Запуск бота (в другом терминале)
make run
```

### 3. Проверка

| Сервис | URL | Проверка |
|--------|-----|----------|
| Backend API | http://localhost:8000 | `curl http://localhost:8000/api/v1/health` |
| Swagger UI | http://localhost:8000/docs | Откроется документация API |
| Frontend | http://localhost:3000 | Загрузится страница авторизации |
| Bot | Telegram | Отправьте `/start` своему боту |

📖 **Пошаговый гайд для новых участников:** [docs/onboarding.md](docs/onboarding.md)

## Компоненты системы

### Backend API

**Технологии:** FastAPI, SQLAlchemy 2.0 (async), Pydantic V2, Alembic

```bash
# Запуск
make run-backend

# Логи
make run-backend-logs

# Тесты
make test-backend
make test-backend-cov  # с coverage

# Линтинг и форматирование
make lint-backend
make format-backend
```

📖 **Документация API:** http://localhost:8000/docs (Swagger UI)

### Frontend (Web Dashboard)

**Технологии:** Next.js 15, React 19, TypeScript 5, Tailwind CSS v4, shadcn/ui

```bash
# Установка зависимостей
make install-frontend

# Запуск dev-сервера
make run-frontend

# Production сборка
make build-frontend

# Линтинг
make lint-frontend
```

**Доступ:** http://localhost:3000

### Telegram-бот

**Технологии:** Python 3.12+, aiogram 3.x, RouterAI LLM

```bash
# Запуск
make run

# Линтинг (вместе с backend)
make lint
make format
```

## Переменные окружения

### Обязательные

| Переменная | Описание | Пример |
|------------|----------|--------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | `123456789:ABCdef...` |
| `ROUTERAI_API_KEY` | API ключ LLM провайдера | `your_api_key` |
| `BOT_USERNAME` | Username бота | `my_booking_bot` |

### Backend

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BACKEND_HOST` | Хост backend | `0.0.0.0` |
| `BACKEND_PORT` | Порт backend | `8000` |
| `BACKEND_DATABASE_URL` | URL базы данных | `postgresql+asyncpg://booking:booking@postgres/booking` |

### Database (Docker)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_USER` | Пользователь PostgreSQL | `booking` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `booking` |
| `POSTGRES_DB` | Имя базы данных | `booking` |

### Frontend

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `NEXT_PUBLIC_API_URL` | URL backend API для браузера | `http://backend:8000/api/v1` |

⚠️ **Важно:** `NEXT_PUBLIC_API_URL` должен быть доступен с хоста при разработке вне Docker.

📖 **Гид по получению токенов:** [docs/how-to-get-tokens.md](docs/how-to-get-tokens.md)

## Команды Makefile

### Основные

| Команда | Описание |
|---------|----------|
| `make postgres-up` | Запуск PostgreSQL |
| `make postgres-logs` | Логи PostgreSQL |
| `make migrate` | Применение миграций |
| `make migrate-create name="..."` | Создание новой миграции |
| `make migrate-down` | Откат последней миграции |
| `make backend-fixtures` | Загрузка демо-данных |

### Backend

| Команда | Описание |
|---------|----------|
| `make run-backend` | Запуск backend в Docker |
| `make run-backend-logs` | Логи backend |
| `make stop-backend` | Остановка backend |
| `make build-backend` | Пересборка backend |
| `make test-backend` | Запуск тестов |
| `make test-backend-cov` | Тесты с coverage |
| `make lint-backend` | Линтинг (ruff) |
| `make format-backend` | Форматирование (ruff) |

### Frontend

| Команда | Описание |
|---------|----------|
| `make install-frontend` | Установка зависимостей (npm) |
| `make run-frontend` | Запуск dev-сервера |
| `make build-frontend` | Production сборка |
| `make lint-frontend` | Линтинг (ESLint) |

### Bot

| Команда | Описание |
|---------|----------|
| `make run` | Запуск бота |
| `make lint` | Линтинг (ruff) |
| `make format` | Форматирование (ruff) |

### Docker

| Команда | Описание |
|---------|----------|
| `make docker-build` | Пересборка всех сервисов |
| `make docker-run` | Запуск всех сервисов |
| `make docker-down` | Остановка всех сервисов |
| `make docker-restart` | Перезапуск всех сервисов |

## Проверка качества кода

| Компонент | Линтинг | Форматирование | Тесты |
|-----------|---------|----------------|-------|
| Backend | `make lint-backend` | `make format-backend` | `make test-backend` |
| Frontend | `make lint-frontend` | (автоматически) | — |
| Bot | `make lint` | `make format` | — |

**Запуск всех проверок:**
```bash
make lint-backend && make format-backend && make test-backend
make lint-frontend
make lint && make format
```

## Документация

### Для новых участников
- [**Onboarding гайд**](docs/onboarding.md) — пошаговая инструкция по запуску
- [**Архитектура**](docs/architecture.md) — компоненты и взаимодействия
- [**Техническое видение**](docs/vision.md) — продуктовое видение и эволюция

### Технические спецификации
- [**Модель данных**](docs/data-model.md) — ER-диаграмма и схемы БД
- [**API контракты**](docs/tech/api-contracts.md) — документация всех endpoints
- [**UI спецификация**](docs/specs/screenflow.md) — экраны и переходы
- [**Сценарии чата**](docs/specs/chatflow.md) — маппинг интентов LLM
- [**Интеграции**](docs/integrations.md) — внешние сервисы

### Процесс разработки
- [**Задачи**](docs/tasks/) — tasklist'ы и планы итераций
- [**ADR**](docs/adr/) — архитектурные решения
- [**Как получить токены**](docs/how-to-get-tokens.md) — гид по настройке

## Примеры API-запросов

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Список домов
curl http://localhost:8000/api/v1/houses

# Создание бронирования
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "house_id": 1,
    "tenant_id": 1,
    "check_in": "2024-06-01",
    "check_out": "2024-06-03",
    "guests_planned": [{"tariff_id": 1, "count": 2}]
  }'

# Список бронирований с фильтрами
curl "http://localhost:8000/api/v1/bookings?house_id=1&status=confirmed"
```

---

**Требования:** Python 3.12+, Node.js 20+, Docker 24+, [uv](https://docs.astral.sh/uv/)

**Перед запуском:** скопируйте `.env.example` в `.env` и заполните токены.

> **Есть вопросы?** См. [docs/onboarding.md](docs/onboarding.md) или создавайте issue в репозитории.
