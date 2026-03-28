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
| 01 | Выбор backend-стека и ADR | 📋 Planned | [план](tasks/task-01-stack-adr/plan.md) \| [summary](tasks/task-01-stack-adr/summary.md) |
| 02 | Генерация каркаса проекта | 📋 Planned | [план](tasks/task-02-scaffold/plan.md) \| [summary](tasks/task-02-scaffold/summary.md) |
| 03 | Проектирование API-контрактов | 📋 Planned | [план](tasks/task-03-api-contracts/plan.md) \| [summary](tasks/task-03-api-contracts/summary.md) |
| 04 | Реализация API бронирований | 📋 Planned | [план](tasks/task-04-booking-api/plan.md) \| [summary](tasks/task-04-booking-api/summary.md) |
| 05 | Реализация API домов и пользователей | 📋 Planned | [план](tasks/task-05-houses-users-api/plan.md) \| [summary](tasks/task-05-houses-users-api/summary.md) |
| 06 | Подключение PostgreSQL | 📋 Planned | [план](tasks/task-06-database/plan.md) \| [summary](tasks/task-06-database/summary.md) |
| 07 | Рефакторинг бота для работы через API | 📋 Planned | [план](tasks/task-07-bot-refactor/plan.md) \| [summary](tasks/task-07-bot-refactor/summary.md) |
| 08 | Актуализация соглашений и документации | 📋 Planned | [план](tasks/task-08-docs-update/plan.md) \| [summary](tasks/task-08-docs-update/summary.md) |

---

## Задача 01: Выбор backend-стека и ADR 📋

### Цель

Определить технологический стек backend и зафиксировать архитектурное решение в ADR.

### Состав работ

- [ ] Сравнение FastAPI vs Flask vs другие фреймворки
- [ ] Выбор ORM (SQLAlchemy 2.0 / Tortoise / другие)
- [ ] Определение подхода к валидации (Pydantic v2)
- [ ] Создание ADR-002: Backend Framework
- [ ] Утверждение стека

### Артефакты

- `docs/adr/adr-002-backend-framework.md` — архитектурное решение
- Запись в `docs/adr/README.md`

### Документы

- 📋 [План](tasks/task-01-stack-adr/plan.md)
- 📝 [Summary](tasks/task-01-stack-adr/summary.md)

---

## Задача 02: Генерация каркаса проекта 📋

### Цель

Создать структуру backend-проекта с настроенными зависимостями и инструментами разработки.

### Состав работ

- [ ] Создание директории `backend/`
- [ ] Настройка pyproject.toml с зависимостями
- [ ] Структура модулей: api/, models/, schemas/, services/, config.py
- [ ] Настройка линтеров (ruff) и форматирования
- [ ] Базовый main.py с запуском сервера
- [ ] Конфигурация через Pydantic-settings

### Артефакты

- `backend/` — директория проекта
- `backend/main.py` — точка входа
- `backend/config.py` — конфигурация
- `backend/api/__init__.py` — роутеры
- `backend/schemas/__init__.py` — Pydantic-схемы
- `pyproject.toml` — обновлённый

### Документы

- 📋 [План](tasks/task-02-scaffold/plan.md)
- 📝 [Summary](tasks/task-02-scaffold/summary.md)

---

## Задача 03: Проектирование API-контрактов 📋

### Цель

Спроектировать и задокументировать REST API endpoints для всех сущностей системы.

### Состав работ

- [ ] Определение ресурсов: users, houses, bookings, tariffs
- [ ] Проектирование endpoints (RESTful)
- [ ] Определение форматов запросов/ответов (Pydantic схемы)
- [ ] Коды ошибок и формат error response
- [ ] Версионирование API (v1 префикс)
- [ ] Документирование в формате OpenAPI/Swagger

### Артефакты

- `backend/schemas/user.py` — схемы пользователей
- `backend/schemas/house.py` — схемы домов
- `backend/schemas/booking.py` — схемы бронирований
- `backend/schemas/tariff.py` — схемы тарифов
- `backend/schemas/common.py` — общие схемы (ErrorResponse, PaginatedResponse)
- `docs/api/openapi.yaml` или автодокументация

### Документы

- 📋 [План](tasks/task-03-api-contracts/plan.md)
- 📝 [Summary](tasks/task-03-api-contracts/summary.md)

---

## Задача 04: Реализация API бронирований 📋

### Цель

Реализовать CRUD endpoints для бронирований с валидацией и базовой бизнес-логикой.

### Состав работ

- [ ] GET /api/v1/bookings — список бронирований (фильтры: user_id, house_id, status)
- [ ] GET /api/v1/bookings/{id} — получение бронирования
- [ ] POST /api/v1/bookings — создание бронирования
- [ ] PATCH /api/v1/bookings/{id} — обновление бронирования
- [ ] DELETE /api/v1/bookings/{id} — отмена бронирования
- [ ] Валидация дат (check_in < check_out)
- [ ] Проверка пересечения дат для одного дома
- [ ] Расчёт суммы на основе тарифов и состава гостей

### Артефакты

- `backend/api/bookings.py` — роутеры бронирований
- `backend/services/booking.py` — бизнес-логика
- `backend/models/booking.py` — SQLAlchemy модель (или in-memory заглушка)

### Документы

- 📋 [План](tasks/task-04-booking-api/plan.md)
- 📝 [Summary](tasks/task-04-booking-api/summary.md)

---

## Задача 05: Реализация API домов и пользователей 📋

### Цель

Реализовать endpoints для управления домами, пользователями и тарифами.

### Состав работ

- [ ] GET /api/v1/houses — список домов
- [ ] GET /api/v1/houses/{id} — детали дома
- [ ] GET /api/v1/houses/{id}/calendar — доступность дома
- [ ] GET /api/v1/users/{id} — профиль пользователя
- [ ] POST /api/v1/users — создание пользователя (из Telegram)
- [ ] GET /api/v1/tariffs — справочник тарифов
- [ ] GET /api/v1/tariffs/{id} — детали тарифа

### Артефакты

- `backend/api/houses.py` — роутеры домов
- `backend/api/users.py` — роутеры пользователей
- `backend/api/tariffs.py` — роутеры тарифов
- `backend/services/house.py` — бизнес-логика домов
- `backend/services/user.py` — бизнес-логика пользователей

### Документы

- 📋 [План](tasks/task-05-houses-users-api/plan.md)
- 📝 [Summary](tasks/task-05-houses-users-api/summary.md)

---

## Задача 06: Подключение PostgreSQL 📋

### Цель

Заменить in-memory хранение на PostgreSQL с миграциями.

### Состав работ

- [ ] Настройка SQLAlchemy 2.0 с asyncpg
- [ ] Создание моделей: User, House, Booking, Tariff
- [ ] Настройка Alembic для миграций
- [ ] Создание начальной миграции
- [ ] Реализация репозиториев/DAO
- [ ] Обновление docker-compose.yaml с PostgreSQL
- [ ] Перенос существующих данных (если есть)

### Артефакты

- `backend/database.py` — подключение к БД
- `backend/models/user.py` — модель пользователя
- `backend/models/house.py` — модель дома
- `backend/models/booking.py` — модель бронирования
- `backend/models/tariff.py` — модель тарифа
- `backend/repositories/` — слой доступа к данным
- `alembic/` — миграции
- `docker-compose.yaml` — обновлённый с postgres

### Документы

- 📋 [План](tasks/task-06-database/plan.md)
- 📝 [Summary](tasks/task-06-database/summary.md)

---

## Задача 07: Рефакторинг бота для работы через API 📋

### Цель

Перевести Telegram-бот с прямой логики на работу через backend API.

### Состав работ

- [ ] Создание HTTP-клиента для backend API в боте
- [ ] Рефакторинг handlers: замена прямых вызовов на API-запросы
- [ ] Удаление in-memory хранения из бота
- [ ] Обработка ошибок API в боте
- [ ] Тестирование end-to-end: бот -> backend -> БД

### Артефакты

- `bot/services/backend_client.py` — HTTP-клиент для API
- Обновлённые `bot/handlers/message.py`
- Удалённые `bot/services/booking.py` (in-memory логика)
- Обновлённые `bot/models/booking.py` (если нужны)

### Документы

- 📋 [План](tasks/task-07-bot-refactor/plan.md)
- 📝 [Summary](tasks/task-07-bot-refactor/summary.md)

---

## Задача 08: Актуализация соглашений и документации 📋

### Цель

Обновить проектную документацию на основе реализованного backend.

### Состав работ

- [ ] Актуализация `docs/vision.md` — отразить выделенный backend
- [ ] Актуализация `docs/data-model.md` — точные поля моделей
- [ ] Актуализация `docs/integrations.md` — backend как точка интеграции
- [ ] Фиксация соглашений: форматы запросов, коды ошибок
- [ ] Фиксация версионирования API (v1)
- [ ] Обновление README с командами запуска
- [ ] Создание Makefile команд: `make run-backend`, `make migrate`

### Артефакты

- Обновлённые `docs/vision.md`, `docs/data-model.md`, `docs/integrations.md`
- Обновлённый `README.md`
- Обновлённый `Makefile`

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
