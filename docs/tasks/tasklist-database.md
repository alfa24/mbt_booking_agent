# Database Tasklist

## Обзор

Tasklist для внедрения полноценного слоя данных на текущем этапе проекта. Замена in-memory хранения на PostgreSQL с полным циклом проектирования, миграций и интеграции в backend.

## Легенда статусов

- 📋 Planned - Запланирован
- 🚧 In Progress - В работе
- ✅ Done - Завершен

## Список задач

| Задача | Описание | Статус | Документы |
|--------|----------|--------|-----------|
| 01 | Сценарии пользователей и требования к данным | ✅ Done | [план](tasks/task-01-user-scenarios/plan.md) \| [summary](tasks/task-01-user-scenarios/summary.md) |
| 02 | Проектирование схемы данных | ✅ Done | [план](tasks/task-02-schema-design/plan.md) \| [summary](tasks/task-02-schema-design/summary.md) |
| 03 | Выбор инструментов миграций и доступа к БД | ✅ Done | [план](tasks/task-03-db-tools/plan.md) \| [summary](tasks/task-03-db-tools/summary.md) |
| 04 | Инфраструктура БД, миграции и наполнение данными | ✅ Done | [план](tasks/task-04-db-infrastructure/plan.md) \| [summary](tasks/task-04-db-infrastructure/summary.md) |
| 05 | ORM-модели, репозитории и интеграция в backend | ✅ Done | [план](tasks/task-05-orm-integration/plan.md) \| [summary](tasks/task-05-orm-integration/summary.md) |
| 06 | Ревью реализованных решений | ✅ Done | [план](tasks/task-06-code-review/plan.md) \| [summary](tasks/task-06-code-review/summary.md) |
| 07 | Устранение замечаний по ревью | ✅ Done | [план](tasks/task-07-fix-review/plan.md) \| [summary](tasks/task-07-fix-review/summary.md) |

---

## Задача 06: Ревью реализованных решений ✅

### Цель

Провести ревью реализованных решений с помощью специализированных скиллов и задокументировать выявленные замечания.

### Состав работ

- [x] Ревью схемы БД через skill `postgresql-table-design`
- [x] Ревью подключения к БД через skill `fastapi-templates`
- [x] Ревью Python-кода через skill `modern-python`
- [x] Создание документа с замечаниями

### Ключевые замечания

**Критичные:**
1. Отсутствуют FK индексы (house_id, tenant_id, owner_id)
2. Нет lifespan для управления соединениями
3. Нет настройки connection pooling

**Желательные:**
4. Устаревший синтаксис type hints (Optional[X] вместо X | None)
5. Нет CHECK constraints
6. PK тип INTEGER вместо BIGINT

### Артефакты

- `docs/tasks/task-06-code-review/plan.md` — план ревью
- `docs/tasks/task-06-code-review/summary.md` — результаты с замечаниями

### Документы

- 📋 [План](tasks/task-06-code-review/plan.md)
- 📝 [Summary](tasks/task-06-code-review/summary.md)

---

## Задача 07: Устранение замечаний по ревью ✅

### Цель

Устранить замечания, выявленные в ходе ревью (Задача 06).

### Состав работ

#### 1. Исправления схемы БД ✅

- [x] Добавить FK индексы:
  - [x] Индекс на bookings.house_id
  - [x] Индекс на bookings.tenant_id
  - [x] Индекс на houses.owner_id
- [x] Добавить CHECK constraints:
  - [x] CHECK (capacity > 0) для houses
  - [x] CHECK (amount >= 0) для tariffs
  - [x] CHECK (check_out > check_in) для bookings

#### 2. Исправления подключения к БД ✅

- [x] Добавить lifespan в main.py — добавлен `await engine.dispose()`
- [x] Настроить connection pooling — добавлены `pool_size`, `max_overflow`
- [x] Сделать echo настраиваемым через env — добавлен `db_echo`

#### 3. Исправления Python-кода ✅

- [x] Добавить `from __future__ import annotations` в репозитории
- [x] Заменить `Optional[X]` на `X | None`
- [x] Заменить `List[X]` на `list[X]`

### Definition of Done

- [x] Все критичные замечания устранены
- [x] Миграции созданы и применены
- [x] Тесты проходят (89 passed)
- [x] Код проходит линтинг (ruff)

### Артефакты

- `backend/config.py` — добавлены настройки пула и echo
- `backend/database.py` — настройки пула через settings
- `backend/main.py` — lifespan с `engine.dispose()`
- `backend/repositories/*.py` — обновлены type hints
- `alembic/versions/8e3c7a9b2f1d_add_indexes_and_constraints.py` — миграция с индексами и constraints

### Документы

- 📋 [План](tasks/task-07-fix-review/plan.md)
- 📝 [Summary](tasks/task-07-fix-review/summary.md)

---

## Задача 01: Сценарии пользователей и требования к данным ✅

### Цель

Определить сценарии использования системы для арендаторов и арендодателей, чтобы заложить основу под будущий frontend и понять, какие данные и связи точно понадобятся.

### Состав работ

- [x] Описать сценарии арендатора:
  - [x] Просмотр списка доступных домов
  - [x] Просмотр деталей дома и календаря занятости
  - [x] Создание бронирования с указанием дат и состава группы
  - [x] Просмотр своих бронирований (история и предстоящие)
  - [x] Отмена бронирования
  - [x] Фиксация результатов поездки (фактический состав, заметки)
- [x] Описать сценарии арендодателя:
  - [x] Просмотр всех своих домов
  - [x] Управление календарём доступности (закрытие/открытие дат)
  - [x] Просмотр всех бронирований с фильтрами
  - [x] Управление тарифами для типов гостей
  - [x] Контроль остатков расходников в домах
- [x] Выделить данные, необходимые для каждого сценария
- [x] Определить связи между сущностями для поддержки сценариев
- [x] Актуализация `docs/data-model.md` — уточнить поля и связи

### Definition of Done (самопроверка агента)

- [x] Описаны все ключевые сценарии для обеих ролей
- [x] Для каждого сценария указаны необходимые данные
- [x] Схема связей между сущностями согласована со сценариями
- [x] Документ `docs/data-model.md` актуализирован

### Проверка пользователем

- [x] Открыть `docs/data-model.md` — проверить описание сущностей
- [x] Проверить, что все сценарии из `docs/vision.md` покрыты данными
- [x] Убедиться, что связи между сущностями логичны

### Артефакты

- `docs/data-model.md` — обновлённый документ с уточнённой моделью данных
- `docs/tasks/task-01-user-scenarios/scenarios.md` — описание сценариев (опционально)

### Документы

- 📋 [План](tasks/task-01-user-scenarios/plan.md)
- 📝 [Summary](tasks/task-01-user-scenarios/summary.md)

---

## Задача 02: Проектирование схемы данных ✅

### Цель

Актуализировать логическую и физическую модель данных, создать физическую ER-диаграмму и провести ревью схемы.

### Состав работ

- [x] Актуализация логической модели на основе сценариев:
  - [x] User — поля, типы, constraints
  - [x] House — поля, типы, constraints
  - [x] Booking — поля, типы, constraints
  - [x] Tariff — поля, типы, constraints
  - [x] ConsumableNote — поля, типы, constraints (если нужна)
  - [x] StayRecord — поля, типы, constraints (если нужна)
- [x] Проектирование физической модели:
  - [x] Типы данных PostgreSQL для каждого поля
  - [x] Индексы для частых запросов
  - [x] Foreign keys и constraints
  - [x] JSON-поля для гибких структур (guests_planned, guests_actual)
- [x] Создание физической ER-диаграммы (mermaid или другой формат)
- [x] Ревью схемы через skill `postgresql-table-design`:
  - [x] Вызвать skill для проверки best practices
  - [x] Применить рекомендации по индексам
  - [x] Применить рекомендации по типам данных
- [x] Актуализация `docs/data-model.md` — добавить физическую модель

### Definition of Done (самопроверка агента)

- [x] Физическая модель содержит все поля с типами PostgreSQL
- [x] Определены индексы для частых запросов (по telegram_id, house_id, датам)
- [x] ER-диаграмма отображает все сущности и связи
- [x] Ревью через skill выполнено, замечания учтены
- [x] Документ `docs/data-model.md` содержит физическую модель

### Проверка пользователем

- [x] Открыть `docs/data-model.md` — проверить раздел физической модели
- [x] Проверить ER-диаграмму на корректность связей
- [x] Убедиться, что индексы покрывают сценарии из Задачи 01

### Артефакты

- `docs/data-model.md` — обновлённый с физической моделью
- ER-диаграмма в документе

### Документы

- 📋 [План](tasks/task-02-schema-design/plan.md)
- 📝 [Summary](tasks/task-02-schema-design/summary.md)

---

## Задача 03: Выбор инструментов миграций и доступа к БД ✅

### Цель

Подготовить ADR с обоснованием выбора инструментов для миграций и доступа к БД, а также практическую справку по их использованию.

### Состав работ

- [x] Исследование вариантов миграций:
  - [x] Alembic (SQLAlchemy)
  - [x] Migrate (Django-style)
  - [x] Ручные SQL-скрипты
- [x] Исследование вариантов ORM/доступа к БД:
  - [x] SQLAlchemy 2.0 + asyncpg
  - [x] psycopg3 (raw/async)
  - [x] databases + sqlalchemy-core
- [x] Создание ADR-003: Database Tools:
  - [x] Обоснование выбора Alembic для миграций
  - [x] Обоснование выбора SQLAlchemy 2.0 + asyncpg
  - [x] Сравнение с альтернативами
  - [x] Trade-offs и риски
- [x] Создание практической справки:
  - [x] Как устроен Alembic в проекте
  - [x] Команды для создания и применения миграций
  - [x] Как устроен SQLAlchemy 2.0 с asyncpg
  - [x] Паттерны использования (engine, session, models)
- [x] Актуализация `docs/adr/README.md` — добавить ссылку на ADR-003

### Definition of Done (самопроверка агента)

- [x] ADR-003 создан и содержит обоснование выбора
- [x] Практическая справка описывает использование инструментов
- [x] Все внешние зависимости зафиксированы с версиями
- [x] Справка содержит примеры команд для типовых операций

### Проверка пользователем

- [x] Открыть `docs/adr/adr-003-database-tools.md` — проверить обоснование
- [x] Проверить практическую справку на полноту
- [x] Убедиться, что выбор согласован с существующими ADR

### Артефакты

- `docs/adr/adr-003-database-tools.md` — архитектурное решение
- `docs/tech/database-guide.md` — практическая справка (опционально)
- `docs/adr/README.md` — обновлённый

### Документы

- 📋 [План](tasks/task-03-db-tools/plan.md)
- 📝 [Summary](tasks/task-03-db-tools/summary.md)

---

## Задача 04: Инфраструктура БД, миграции и наполнение данными ✅

### Цель

Настроить инфраструктуру PostgreSQL, создать миграции, подготовить команды для работы с БД и наполнить данными из реальной выгрузки.

### Состав работ

- [x] Настройка Docker-инфраструктуры:
  - [x] Обновление `docker-compose.yaml` — добавить сервис postgres
  - [x] Настройка healthcheck для postgres
  - [x] Настройка volumes для персистентности данных
  - [x] Обновление `.env.example` — добавить переменные БД
- [x] Настройка Alembic:
  - [x] Инициализация Alembic в Docker
  - [x] Настройка `alembic/env.py` для asyncpg
  - [x] Настройка `alembic.ini`
- [x] Создание начальной миграции:
  - [x] Генерация миграции с моделями User, House, Booking, Tariff
  - [x] Проверка миграции (upgrade/downgrade)
  - [x] Применение миграции
- [x] Подготовка команд для работы с БД:
  - [x] Обновление `Makefile` — добавить `postgres-up`, `postgres-down`
  - [x] Обновление `Makefile` — добавить `migrate`, `migrate-create`, `migrate-down`
  - [x] Обновление `Makefile` — добавить `psql` для подключения к БД
  - [x] Скрипты для просмотра данных (опционально)
- [x] Начальное наполнение данными:
  - [x] Подготовка данных из `data/progress-import.v1.json`
  - [x] Создание seed-миграции или скрипта для импорта
  - [x] Импорт пользователей, домов, тарифов
  - [x] Импорт бронирований (при наличии)
- [x] Проверка инфраструктуры:
  - [x] БД поднимается: `make postgres-up`
  - [x] Миграции применяются: `make migrate`
  - [x] Данные доступны через `make psql`

### Definition of Done (самопроверка агента)

- [x] PostgreSQL запускается через `make postgres-up`
- [x] Миграции создаются и применяются без ошибок
- [x] Данные из `data/progress-import.v1.json` импортированы
- [x] Команды `Makefile` работают корректно
- [x] Данные сохраняются между перезапусками контейнера

### Проверка пользователем

```bash
# Запуск инфраструктуры
make postgres-up

# Применение миграций
make migrate

# Проверка данных
make psql
# В psql: \dt — должны быть таблицы users, houses, bookings, tariffs

# Просмотр импортированных данных
# В psql: SELECT * FROM houses;
```

### Артефакты

- `docker-compose.yaml` — обновлённый с postgres
- `.env.example` — обновлённый с переменными БД
- `Makefile` — обновлённый с командами БД
- `alembic/` — настроенная директория миграций
- `alembic/versions/xxx_initial.py` — начальная миграция
- `backend/seeds/` — скрипты для импорта данных (опционально)

### Документы

- 📋 [План](tasks/task-04-db-infrastructure/plan.md)
- 📝 [Summary](tasks/task-04-db-infrastructure/summary.md)

---

## Задача 05: ORM-модели, репозитории и интеграция в backend ✅

### Цель

Реализовать ORM-модели, слой доступа к данным (репозитории) и интегрировать их в backend для замены in-memory хранения.

### Состав работ

- [x] Создание SQLAlchemy моделей:
  - [x] `backend/database.py` — подключение к БД, engine, session
  - [x] `backend/models/user.py` — модель User
  - [x] `backend/models/house.py` — модель House
  - [x] `backend/models/booking.py` — модель Booking
  - [x] `backend/models/tariff.py` — модель Tariff
  - [x] `backend/models/__init__.py` — экспорт всех моделей
- [x] Реализация репозиториев:
  - [x] `backend/repositories/user.py` — CRUD + поиск по telegram_id
  - [x] `backend/repositories/house.py` — CRUD + фильтры
  - [x] `backend/repositories/booking.py` — CRUD + проверка пересечения дат
  - [x] `backend/repositories/tariff.py` — CRUD
  - [x] `backend/repositories/__init__.py` — экспорт
- [x] Обновление сервисов:
  - [x] `backend/services/user.py` — интеграция с UserRepository
  - [x] `backend/services/house.py` — интеграция с HouseRepository
  - [x] `backend/services/booking.py` — интеграция с BookingRepository
  - [x] `backend/services/tariff.py` — интеграция с TariffRepository
- [x] Обновление API роутеров:
  - [x] `backend/api/users.py` — использование сервисов с БД
  - [x] `backend/api/houses.py` — использование сервисов с БД
  - [x] `backend/api/bookings.py` — использование сервисов с БД
  - [x] `backend/api/tariffs.py` — использование сервисов с БД
  - [x] `backend/dependencies.py` — dependency injection для БД
- [x] Обновление `backend/main.py`:
  - [x] Интеграция lifespan для инициализации/закрытия БД
  - [x] Подключение зависимостей
- [x] Обновление тестов:
  - [x] `backend/tests/conftest.py` — фикстуры для тестовой БД
  - [x] Обновление тестов для работы с async БД
- [x] Удаление in-memory хранения:
  - [x] Удаление старых in-memory репозиториев
  - [x] Проверка, что нет остатков in-memory логики
- [x] Проверка работы:
  - [x] Запуск backend с PostgreSQL
  - [x] Создание бронирования через API
  - [x] Перезапуск backend — данные на месте
  - [x] Тесты проходят с тестовой БД

### Definition of Done (самопроверка агента)

- [x] Все ORM-модели созданы и соответствуют физической модели
- [x] Репозитории реализуют весь необходимый функционал
- [x] API работает с PostgreSQL — данные сохраняются между перезапусками
- [x] Тесты проходят с тестовой БД
- [x] In-memory хранение полностью удалено

### Проверка пользователем

```bash
# Запуск инфраструктуры
make postgres-up
make migrate

# Запуск backend
make run-backend

# Создание бронирования
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"house_id": 1, "check_in": "2024-06-01", "check_out": "2024-06-03", "guests": [{"tariff_id": 2, "count": 2}]}'

# Перезапуск сервера и проверка
make stop-backend
make run-backend
curl http://localhost:8000/api/v1/bookings
# Данные должны быть на месте

# Запуск тестов
make test-backend
```

### Артефакты

- `backend/database.py` — подключение к БД
- `backend/models/*.py` — ORM-модели
- `backend/repositories/*.py` — слой доступа к данным
- `backend/services/*.py` — обновлённые сервисы
- `backend/api/*.py` — обновлённые роутеры
- `backend/tests/conftest.py` — фикстуры для тестов
- `backend/dependencies.py` — dependency injection

### Документы

- 📋 [План](tasks/task-05-orm-integration/plan.md)
- 📝 [Summary](tasks/task-05-orm-integration/summary.md)

---

## Связь с другими tasklist

| Tasklist | Связь |
|----------|-------|
| [tasklist-backend.md](tasklist-backend.md) | Этот tasklist детализирует Задачу 06 из backend tasklist |
| [tasklist-bot.md](tasklist-bot.md) | После завершения бот работает через API с PostgreSQL |
| [tasklist-web-tenant.md](tasklist-web-tenant.md) | Сценарии арендатора закладывают основу для веб-приложения |
| [tasklist-web-owner.md](tasklist-web-owner.md) | Сценарии арендодателя закладывают основу для панели управления |

---

## Качество и инженерные практики

### Тестирование

- Unit-тесты для репозиториев (pytest + async)
- Интеграционные тесты для API endpoints с тестовой БД
- Фикстуры для изоляции тестов

### Миграции

- Версионирование через Alembic
- Автогенерация миграций из моделей
- Проверка миграций в CI (upgrade/downgrade)

### Наблюдаемость

- Логирование SQL-запросов (echo=True в dev)
- Health check для БД

