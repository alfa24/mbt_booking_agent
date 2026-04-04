# Summary: Задача 04 - Инфраструктура БД, миграции и наполнение данными

## Что реализовано

### Docker-инфраструктура

**docker-compose.yaml:**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: booking
      POSTGRES_PASSWORD: booking
      POSTGRES_DB: booking
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U booking"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - BACKEND_DATABASE_URL=postgresql+asyncpg://booking:booking@postgres/booking
```

**.env.example:**
```
BACKEND_DATABASE_URL=postgresql+asyncpg://booking:booking@localhost/booking
POSTGRES_USER=booking
POSTGRES_PASSWORD=booking
POSTGRES_DB=booking
```

### Alembic

**Структура:**
```
alembic/
├── env.py              # Async-конфигурация
├── script.py.mako      # Шаблон миграций
└── versions/
    └── 2a84cf51810b_initial_migration.py
```

**Начальная миграция создаёт таблицы:**
- users — с индексом на telegram_id
- houses — с FK на users.id
- bookings — с FK на houses.id и users.id
- tariffs — справочник тарифов

### Команды Makefile

```makefile
# Database commands (Docker)
migrate:              # Применение миграций
migrate-create:       # Создание миграции (name=...)
migrate-down:         # Откат миграции
postgres-up:          # Запуск PostgreSQL
postgres-logs:        # Логи PostgreSQL
```

## Definition of Done — статус

- [x] PostgreSQL запускается через `make postgres-up`
- [x] Миграции создаются и применяются без ошибок
- [ ] Данные из `data/progress-import.v1.json` импортированы (опционально)
- [x] Команды `Makefile` работают корректно
- [x] Данные сохраняются между перезапусками контейнера

## Примечание

Seed-скрипты для импорта данных из `data/progress-import.v1.json` не реализованы — помечено как опциональное.
