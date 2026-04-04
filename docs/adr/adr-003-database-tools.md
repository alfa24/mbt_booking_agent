# ADR-003: Выбор инструментов миграций и доступа к БД

## Статус

Accepted

## Контекст

После выбора PostgreSQL (ADR-001) и FastAPI (ADR-002) необходимо определить инструменты для:
- Миграций схемы базы данных
- Доступа к данным (ORM/драйвер)

Требования:
- Полная поддержка async/await
- Совместимость с FastAPI и Pydantic
- Простота использования и деплоя
- Возможность автогенерации миграций

## Рассмотренные варианты

### 1. Alembic (SQLAlchemy)

**За:**
- Стандарт де-факто для SQLAlchemy
- Поддержка автогенерации миграций из моделей
- Async-совместимость (через asyncpg)
- Поддержка ветвления и слияния миграций
- Широкая документация и community

**Против:**
- Требует понимания SQLAlchemy
- Миграции требуют ручной проверки

### 2. Migrate (Django-style)

**За:**
- Простота для тех, кто знаком с Django
- Автоматическое создание миграций

**Против:**
- Требует Django ORM
- Не подходит для FastAPI
- Нет нативной async поддержки

### 3. Ручные SQL-скрипты

**За:**
- Полный контроль над SQL
- Нет зависимостей

**Против:**
- Высокий риск ошибок
- Нет автогенерации
- Сложно поддерживать в команде

### 4. SQLAlchemy 2.0 + asyncpg

**За:**
- Нативная поддержка async/await
- Современный API SQLAlchemy 2.0
- Высокая производительность asyncpg
- Полная совместимость с Pydantic v2
- Единый стек с FastAPI

**Против:**
- Кривая обучения SQLAlchemy
- Многослойная абстракция

### 5. psycopg3 (raw/async)

**За:**
- Минимальная абстракция
- Высокая производительность
- Нативная async поддержка

**Против:**
- Нужно писать SQL вручную
- Нет ORM-функциональности
- Больше boilerplate кода

### 6. databases + sqlalchemy-core

**За:**
- Легковесное решение
- Async из коробки

**Против:**
- Требует отдельного управления миграциями
- Меньше функциональности чем SQLAlchemy ORM

## Решение

Использовать **Alembic** для миграций и **SQLAlchemy 2.0 + asyncpg** для доступа к данным.

**Стек:**
- `alembic` — миграции
- `sqlalchemy[asyncio]` — ORM
- `asyncpg` — async PostgreSQL драйвер

**Обоснование:**
- Единый стек SQLAlchemy для ORM и миграций
- Полная поддержка async/await
- Автогенерация миграций из моделей
- Совместимость с Pydantic v2 через `model_validate`
- Стандарт для FastAPI проектов

## Последствия

### Положительные
- Автогенерация миграций при изменении моделей
- Полная типизация с SQLAlchemy 2.0
- Высокая производительность asyncpg
- Dependency injection через FastAPI `Depends()`

### Отрицательные
- Необходимость изучения SQLAlchemy
- Миграции требуют проверки перед применением

## Структура

```
alembic/
├── env.py          # Конфигурация для asyncpg
├── script.py.mako  # Шаблон миграций
└── versions/       # Миграции

backend/
├── database.py     # Engine, session, Base
├── models/         # SQLAlchemy модели
└── repositories/   # Слой доступа к данным
```

## Команды

```bash
# Создание миграции
make migrate-create name="add_user_table"

# Применение миграций
make migrate

# Откат миграции
make migrate-down
```

## Ссылки

- [ADR-001: Выбор СУБД](adr-001-database.md)
- [ADR-002: Выбор backend-фреймворка](adr-002-backend-framework.md)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
