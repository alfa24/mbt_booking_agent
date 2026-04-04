# План: Задача 04 - Инфраструктура БД, миграции и наполнение данными

## Цель

Настроить инфраструктуру PostgreSQL, создать миграции, подготовить команды для работы с БД и наполнить данными.

## Фактически реализовано

### Docker-инфраструктура

**docker-compose.yaml:**
- Сервис `postgres` с PostgreSQL 16 Alpine
- Healthcheck для проверки готовности
- Volume `postgres_data` для персистентности
- Сервис `backend` с зависимостью от postgres

**.env.example:**
- `BACKEND_DATABASE_URL` — URL для подключения backend
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — для docker-compose

### Alembic

**Конфигурация:**
- `alembic/env.py` — async-конфигурация с `async_engine_from_config`
- `alembic.ini` — основная конфигурация
- `alembic/script.py.mako` — шаблон миграций

**Начальная миграция:**
- `alembic/versions/2a84cf51810b_initial_migration.py`
- Таблицы: users, houses, bookings, tariffs
- Индексы и Foreign Keys

### Команды Makefile

```makefile
migrate              # Применение миграций
migrate-create       # Создание миграции (name=...)
migrate-down         # Откат миграции
postgres-up          # Запуск PostgreSQL
postgres-logs        # Логи PostgreSQL
```

## Состав работ (документирование)

### 1. Создание plan.md

Описать:
- Docker-инфраструктуру
- Настройку Alembic
- Начальную миграцию
- Команды Makefile

### 2. Создание summary.md

Описать что реализовано:
- docker-compose.yaml — сервис postgres
- .env.example — переменные БД
- alembic/ — настроенная директория
- Makefile — команды для работы с БД

### 3. Опционально: seed-скрипты

Для импорта тестовых данных.

## Definition of Done

- [ ] PostgreSQL запускается через `make postgres-up`
- [ ] Миграции создаются и применяются без ошибок
- [ ] Данные из `data/progress-import.v1.json` импортированы
- [ ] Команды `Makefile` работают корректно
- [ ] Данные сохраняются между перезапусками контейнера

## Проверка пользователем

```bash
# Запуск инфраструктуры
make postgres-up

# Применение миграций
make migrate

# Проверка данных
make postgres-logs
# В psql: \dt — должны быть таблицы users, houses, bookings, tariffs
```
