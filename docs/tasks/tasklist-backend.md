# Backend Tasklist

## Обзор

Tasklist для области backend — ядра системы бронирования загородного жилья.

Backend выступает единой точкой входа для всех клиентов: Telegram-бота, веб-приложения арендаторов и панели управления арендодателя. Вся бизнес-логика (бронирования, тарификация, управление домами) концентрируется здесь, а клиенты отвечают только за отображение и взаимодействие с пользователем.

Backend также интегрируется с внешними сервисами: LLM-провайдером для обработки естественного языка и платёжными системами (на этапе интеграций).

## Связь с plan.md

Этот tasklist покрывает **Этап 1: Backend API и база данных** из [docs/plan.md](../plan.md):

- Выделение ядра системы из MVP-бота
- Создание REST API для всех сущностей (User, House, Booking, Tariff)
- Переход от in-memory хранения к PostgreSQL
- Подготовка foundation для параллельной разработки веб-приложений (этапы 2 и 3)

## Легенда статусов

- 📋 Planned - Запланирован
- 🚧 In Progress - В работе
- ✅ Done - Завершен

## Список задач

| Задача | Описание | Статус | Документы |
|--------|----------|--------|-----------|
| 01 | Выбор backend-стека и ADR | ✅ Done | [план](tasks/task-01-stack-adr/plan.md) \| [summary](tasks/task-01-stack-adr/summary.md) |
| 02 | Генерация каркаса проекта | ✅ Done | [план](tasks/task-02-scaffold/plan.md) \| [summary](tasks/task-02-scaffold/summary.md) |
| 03 | Проектирование API-контрактов | 📋 Planned | [план](tasks/task-03-api-contracts/plan.md) \| [summary](tasks/task-03-api-contracts/summary.md) |
| 04 | Реализация API бронирований | 📋 Planned | [план](tasks/task-04-booking-api/plan.md) \| [summary](tasks/task-04-booking-api/summary.md) |
| 05 | Реализация API домов и пользователей | ✅ Done | [план](tasks/task-05-houses-users-api/plan.md) \| [summary](tasks/task-05-houses-users-api/summary.md) |
| 06 | Подключение PostgreSQL | 📋 Planned | [план](tasks/task-06-database/plan.md) \| [summary](tasks/task-06-database/summary.md) |
| 07 | Рефакторинг бота для работы через API | ✅ Done | [план](tasks/task-07-bot-refactor/plan.md) \| [summary](tasks/task-07-bot-refactor/summary.md) |
| 08 | Актуализация соглашений и документации | 📋 Planned | [план](tasks/task-08-docs-update/plan.md) \| [summary](tasks/task-08-docs-update/summary.md) |

---

## Задача 01: Выбор backend-стека и ADR ✅

### Цель

Определить технологический стек backend и зафиксировать архитектурное решение в ADR.

> **Рекомендация:** Перед выбором выполнить `/find-skills` для поиска подходящих skills (fastapi, django, python-api).

### Состав работ

- [x] Выполнить `/find-skills` для backend-фреймворков
- [x] Сравнение FastAPI vs Django vs другие фреймворки
- [x] Выбор ORM (SQLAlchemy 2.0 / Django ORM / другие)
- [x] Определение подхода к валидации (Pydantic v2)
- [x] Создание ADR-002: Backend Framework
- [x] Утверждение стека
- [x] Актуализация `.qoder/rules/conventions.md` — добавить раздел о backend

### Definition of Done (самопроверка агента)

- [x] ADR создан и содержит обоснование выбора
- [x] Все внешние зависимости зафиксированы с версиями
- [x] Conventions обновлены — структура backend, паттерны, naming

### Проверка пользователем

- [x] Открыть `docs/adr/adr-002-backend-framework.md` — проверить обоснование
- [x] Открыть `.qoder/rules/conventions.md` — проверить раздел о backend
- [x] Убедиться, что выбор согласован

### Артефакты

- `docs/adr/adr-002-backend-framework.md` — архитектурное решение
- `.qoder/rules/conventions.md` — обновлённые соглашения
- Запись в `docs/adr/README.md`

### Документы

- 📋 [План](tasks/task-01-stack-adr/plan.md)
- 📝 [Summary](tasks/task-01-stack-adr/summary.md)

---

## Задача 02: Генерация каркаса проекта 📋

### Цель

Создать структуру backend-проекта с настроенными зависимостями и инструментами разработки.

> **Рекомендация:** Использовать skill для генерации каркаса (`/find-skills` fastapi-template / django-template).

### Состав работ

- [ ] Создание директории `backend/`
- [ ] Настройка `pyproject.toml` с зависимостями
- [ ] Структура модулей: api/, models/, schemas/, services/, config.py
- [ ] Настройка линтеров (ruff) и форматирования
- [ ] Базовый `main.py` с запуском сервера
- [ ] Конфигурация через Pydantic-settings
- [ ] Обновление `.env.example` — добавить переменные backend
- [ ] Обновление `Makefile` — добавить `make run-backend`, `make lint-backend`

### Definition of Done (самопроверка агента)

- [ ] Проект запускается без ошибок: `make run-backend` или `uv run python -m backend.main`
- [ ] Линтинг проходит: `make lint-backend`
- [ ] Сервер отвечает на `GET /health` с кодом 200
- [ ] `.env.example` содержит все необходимые переменные

### Проверка пользователем

```
# Запуск backend
make run-backend

# Проверка health endpoint
curl http://localhost:8000/health

# Ожидаемый ответ: {"status": "ok"}
```

### Артефакты

- `backend/` — директория проекта
- `backend/main.py` — точка входа
- `backend/config.py` — конфигурация
- `backend/api/__init__.py` — роутеры
- `backend/schemas/__init__.py` — Pydantic-схемы
- `pyproject.toml` — обновлённый
- `.env.example` — обновлённый
- `Makefile` — обновлённый

### Документы

- 📋 [План](tasks/task-02-scaffold/plan.md)
- 📝 [Summary](tasks/task-02-scaffold/summary.md)

---

## Задача 03: Проектирование API-контрактов 📋

### Цель

Спроектировать и задокументировать REST API endpoints для сценариев

> **Рекомендация:** Использовать skill для API-дизайна (`/find-skills` api-design).

### Состав работ

- [x] Определение ресурсов: users, houses, bookings, tariffs
- [x] Проектирование endpoints (RESTful):
  - `GET /api/v1/users` — список пользователей
  - `GET /api/v1/users/{id}` — получение пользователя
  - `POST /api/v1/users` — создание пользователя (из Telegram)
  - `PUT /api/v1/users/{id}` — полная замена профиля
  - `PATCH /api/v1/users/{id}` — частичное обновление профиля
  - `GET /api/v1/houses` — список домов
  - `GET /api/v1/houses/{id}` — детали дома
  - `GET /api/v1/houses/{id}/calendar` — доступность дома
  - `POST /api/v1/houses` — создание дома
  - `PUT /api/v1/houses/{id}` — полная замена дома
  - `PATCH /api/v1/houses/{id}` — частичное обновление дома
  - `GET /api/v1/bookings` — список бронирований
  - `GET /api/v1/bookings/{id}` — получение бронирования
  - `POST /api/v1/bookings` — создание бронирования
  - `PATCH /api/v1/bookings/{id}` — обновление бронирования
  - `PATCH /api/v1/bookings/{id}/cancel` — отмена бронирования
  - `GET /api/v1/tariffs` — справочник тарифов
  - `GET /api/v1/tariffs/{id}` — детали тарифа
- [x] Определение форматов запросов/ответов (Pydantic схемы)
- [x] Коды ошибок и формат error response
- [x] Версионирование API (`/api/v1/` префикс)
- [x] Документирование в формате OpenAPI/Swagger
- [ ] Актуализация `docs/data-model.md` — уточнить поля сущностей при необходимости

### Definition of Done (самопроверка агента)

- [x] Все схемы валидируются Pydantic
- [x] OpenAPI документация доступна по `/docs` (Swagger UI)
- [x] Все endpoints имеют описание и примеры
- [x] Коды ошибок задокументированы

### Проверка пользователем

```bash
# Запуск backend
make run-backend

# Открытие Swagger UI
open http://localhost:8000/docs

# Проверка: все endpoints отображаются, схемы валидны
```

### Артефакты

- `backend/schemas/user.py` — схемы пользователей
- `backend/schemas/house.py` — схемы домов
- `backend/schemas/booking.py` — схемы бронирований
- `backend/schemas/tariff.py` — схемы тарифов
- `backend/schemas/message.py` — схемы сообщений
- `backend/schemas/common.py` — общие схемы (ErrorResponse, PaginatedResponse)
- `docs/api/openapi.yaml` или автодокументация
- `docs/data-model.md` — обновлённый

### Документы

- 📋 [План](tasks/task-03-api-contracts/plan.md)
- 📝 [Summary](tasks/task-03-api-contracts/summary.md)

---

## Задача 04: Реализация API бронирований ✅

### Цель

Реализовать CRUD endpoints для бронирований с валидацией и базовой бизнес-логикой.

### Состав работ

- [x] `GET /api/v1/bookings` — список бронирований (фильтры: user_id, house_id, status)
- [x] `GET /api/v1/bookings/{id}` — получение бронирования
- [x] `POST /api/v1/bookings` — создание бронирования
- [x] `PATCH /api/v1/bookings/{id}` — обновление бронирования
- [x] `DELETE /api/v1/bookings/{id}` — отмена бронирования
- [x] Валидация дат (check_in < check_out)
- [x] Проверка пересечения дат для одного дома
- [x] Расчёт суммы на основе тарифов и состава гостей
- [x] Базовые API-тесты для всех endpoints (pytest + httpx)

### Definition of Done (самопроверка агента)

- [x] Все endpoints возвращают корректные HTTP-коды (200, 201, 400, 404, 422)
- [x] Валидация работает — невалидные данные отклоняются
- [x] Тесты проходят: `docker compose exec backend uv run pytest backend/tests/test_bookings.py -v`
- [x] Покрытие бронирований > 80% (24 теста)

### Проверка пользователем

```bash
# Запуск backend в Docker
docker compose up -d backend

# Запуск тестов в контейнере
docker compose exec backend uv run pytest backend/tests/test_bookings.py -v

# Ручная проверка через Swagger (http://localhost:8001/docs)
curl -X POST http://localhost:8001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"house_id": 1, "check_in": "2024-06-01", "check_out": "2024-06-03", "guests": [{"tariff_id": 2, "count": 2}]}'
```

### Артефакты

- `backend/api/bookings.py` — роутеры бронирований
- `backend/services/booking.py` — бизнес-логика
- `backend/repositories/booking.py` — in-memory репозиторий
- `backend/exceptions.py` — кастомные исключения
- `backend/tests/test_bookings.py` — тесты (24 шт.)

### Документы

- 📋 [План](tasks/task-04-booking-api/plan.md)
- 📝 [Summary](tasks/task-04-booking-api/summary.md)

---

## Задача 05: Реализация API домов и пользователей ✅

### Цель

Реализовать endpoints для управления домами, пользователями и тарифами.

### Состав работ

- [x] `GET /api/v1/houses` — список домов
- [x] `GET /api/v1/houses/{id}` — детали дома
- [x] `GET /api/v1/houses/{id}/calendar` — доступность дома
- [x] `GET /api/v1/users/{id}` — профиль пользователя
- [x] `POST /api/v1/users` — создание пользователя (из Telegram)
- [x] `GET /api/v1/tariffs` — справочник тарифов
- [x] `GET /api/v1/tariffs/{id}` — детали тарифа
- [x] API-тесты для всех endpoints

### Definition of Done (самопроверка агента)

- [x] Все endpoints работают корректно
- [x] Тесты проходят: `docker compose exec backend uv run pytest backend/tests/test_houses.py backend/tests/test_users.py backend/tests/test_tariffs.py -v`
- [x] Swagger UI отображает все endpoints

### Проверка пользователем

```bash
# Запуск тестов
pytest backend/tests/test_houses.py backend/tests/test_users.py -v

# Проверка списка домов
curl http://localhost:8000/api/v1/houses
```

### Артефакты

- `backend/api/houses.py` — роутеры домов
- `backend/api/users.py` — роутеры пользователей
- `backend/api/tariffs.py` — роутеры тарифов
- `backend/services/house.py` — бизнес-логика домов
- `backend/services/user.py` — бизнес-логика пользователей
- `backend/tests/test_houses.py` — тесты домов
- `backend/tests/test_users.py` — тесты пользователей

### Документы

- 📋 [План](tasks/task-05-houses-users-api/plan.md)
- 📝 [Summary](tasks/task-05-houses-users-api/summary.md)

---

## Задача 06: Подключение PostgreSQL ✅

### Цель

Заменить in-memory хранение на PostgreSQL с миграциями.

### Состав работ

- [x] Настройка SQLAlchemy 2.0 с asyncpg
- [x] Создание моделей: User, House, Booking, Tariff
- [x] Настройка Alembic для миграций
- [x] Создание начальной миграции
- [x] Реализация репозиториев/DAO
- [x] Обновление `docker-compose.yaml` с PostgreSQL
- [x] Обновление `.env.example` — добавить переменные БД
- [x] Обновление `Makefile` — добавить `make migrate`, `make migrate-create`

### Definition of Done (самопроверка агента)

- [x] БД поднимается: `docker compose up postgres`
- [x] Миграции применяются: `make migrate`
- [x] API работает с БД — данные сохраняются между перезапусками
- [x] Тесты проходят с тестовой БД (user tests: 21/21 passing)

### Проверка пользователем

```bash
# Запуск инфраструктуры
docker compose up -d postgres

# Применение миграций
make migrate

# Проверка: создать бронирование, перезапустить сервер, проверить что данные на месте
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"house_id": 1, "check_in": "2024-06-01", "check_out": "2024-06-03", "guests": [{"type": "adult", "count": 2}]}'

# Перезапуск сервера и проверка
make run-backend
curl http://localhost:8000/api/v1/bookings
```

### Артефакты

- `backend/database.py` — подключение к БД
- `backend/models/user.py` — модель пользователя
- `backend/models/house.py` — модель дома
- `backend/models/booking.py` — модель бронирования
- `backend/models/tariff.py` — модель тарифа
- `backend/repositories/` — слой доступа к данным
- `alembic/` — миграции
- `docker-compose.yaml` — обновлённый с postgres
- `.env.example` — обновлённый
- `Makefile` — обновлённый

### Документы

- 📋 [План](tasks/task-06-database/plan.md)
- 📝 [Summary](tasks/task-06-database/summary.md)

---

## Задача 07: Рефакторинг бота для работы через API 📋

### Цель

Перевести Telegram-бот с прямой логики на работу через backend API.

### Состав работ

- [x] Создание HTTP-клиента для backend API в боте
- [x] Рефакторинг handlers: замена прямых вызовов на API-запросы
- [x] Удаление in-memory хранения из бота
- [x] Обработка ошибок API в боте
- [x] Тестирование end-to-end: бот -> backend -> БД
- [x] Актуализация `docs/integrations.md` — добавить схему взаимодействия бота с backend
- [x] Обновление `README.md` — инструкции по запуску обоих сервисов

### Definition of Done (самопроверка агента)

- [x] Бот запускается и подключается к backend
- [x] Сообщения от бота проходят через backend API
- [x] Данные сохраняются в БД (не в памяти бота)
- [x] End-to-end тест проходит: сообщение в бот -> backend -> БД -> ответ

### Проверка пользователем

```bash
# Запуск всей системы
make run-backend  # в одном терминале
make run          # бот в другом терминале

# Проверка: отправить сообщение боту в Telegram
# Ожидаемый результат: бот отвечает, данные сохраняются в БД

# Проверка через API
curl http://localhost:8000/api/v1/bookings
# Должны отображаться бронирования, созданные через бота
```

### Артефакты

- `bot/services/backend_client.py` — HTTP-клиент для API
- Обновлённые `bot/handlers/message.py`
- Удалённые `bot/services/booking.py` (in-memory логика)
- Обновлённые `bot/models/booking.py` (если нужны)
- `docs/integrations.md` — обновлённый
- `README.md` — обновлённый

### Документы

- 📋 [План](tasks/task-07-bot-refactor/plan.md)
- 📝 [Summary](tasks/task-07-bot-refactor/summary.md)

---

## Задача 08: Актуализация соглашений и документации ✅

### Цель

Обновить проектную документацию на основе реализованного backend.

### Состав работ

- [x] Актуализация `docs/vision.md` — отразить выделенный backend
- [x] Актуализация `docs/data-model.md` — точные поля моделей
- [x] Актуализация `docs/integrations.md` — backend как точка интеграции
- [x] Актуализация `docs/plan.md` — обновить статус этапа 1
- [x] Фиксация соглашений в `.qoder/rules/conventions.md`: форматы запросов, коды ошибок
- [x] Фиксация версионирования API (v1)
- [x] Обновление `README.md` с командами запуска backend
- [x] Проверка `Makefile` — все команды актуальны
- [x] Проверка `.env.example` — все переменные описаны

### Definition of Done (самопроверка агента)

- [x] Все документы отражают текущее состояние системы
- [x] README содержит инструкции по запуску backend и бота
- [x] Conventions содержат правила для backend-разработки
- [x] Новый участник может развернуть систему по README

### Проверка пользователем

```bash
# Проверка полноты документации
cat README.md | grep -E "(run-backend|migrate|docker)"

# Проверка env переменных
cat .env.example

# Проверка make-команд
make help  # или просмотр Makefile
```

### Артефакты

- `docs/vision.md` — обновлённый
- `docs/data-model.md` — обновлённый
- `docs/integrations.md` — обновлённый
- `docs/plan.md` — обновлённый
- `.qoder/rules/conventions.md` — обновлённый
- `README.md` — обновлённый
- `Makefile` — проверенный
- `.env.example` — проверенный

### Документы

- 📋 [План](tasks/task-08-docs-update/plan.md)
- 📝 [Summary](tasks/task-08-docs-update/summary.md)

---

## Качество и инженерные практики

### Тестирование

- Unit-тесты для сервисов (pytest)
- Интеграционные тесты для API endpoints (httpx + pytest-asyncio)
- Фикстуры для тестовой БД

### Линтинг и форматирование

- Ruff для линтинга и форматирования
- MyPy для статической типизации
- Pre-commit hooks

### Наблюдаемость

- Структурированное логирование (structlog)
- Базовые метрики (prometheus-client)
- Health check endpoint: GET /health

### Правила изменений контрактов

- Семантическое версионирование API (/api/v1/, /api/v2/)
- Обратная совместимость в рамках мажорной версии
- Deprecation policy: минимум 1 версия с warning
- Документирование breaking changes
