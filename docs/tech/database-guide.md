# Руководство по работе с базой данных

## Обзор

Проект использует PostgreSQL с SQLAlchemy 2.0 и Alembic для миграций.

## Стек

- **PostgreSQL 16** — база данных
- **SQLAlchemy 2.0** — ORM с async поддержкой
- **asyncpg** — async PostgreSQL драйвер
- **Alembic** — миграции

## Структура

```
alembic/
├── env.py              # Конфигурация Alembic для async
├── script.py.mako      # Шаблон миграций
└── versions/           # Файлы миграций
    └── 2a84cf51810b_initial_migration.py

backend/
├── database.py         # Подключение к БД
├── models/             # SQLAlchemy модели
│   ├── user.py
│   ├── house.py
│   ├── booking.py
│   └── tariff.py
└── repositories/       # Слой доступа к данным
```

## Подключение к БД

### backend/database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

engine = create_async_engine(
    "postgresql+asyncpg://booking:booking@postgres/booking",
    echo=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)
```

## Миграции

### Создание миграции

```bash
make migrate-create name="add_user_table"
```

Эквивалент:
```bash
docker compose exec backend uv run alembic revision --autogenerate -m "add_user_table"
```

### Применение миграций

```bash
make migrate
```

Эквивалент:
```bash
docker compose exec backend uv run alembic upgrade head
```

### Откат миграции

```bash
make migrate-down
```

Эквивалент:
```bash
docker compose exec backend uv run alembic downgrade -1
```

## Модели

### Пример модели

```python
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from backend.database import Base
import enum

class UserRole(str, enum.Enum):
    TENANT = "tenant"
    OWNER = "owner"
    BOTH = "both"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.TENANT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

## Репозитории

### Паттерн Repository

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get(self, user_id: int) -> UserResponse | None:
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None
```

## Запуск PostgreSQL

```bash
# Только PostgreSQL
make postgres-up

# Вся инфраструктура
docker compose up -d
```

## Подключение к БД вручную

```bash
docker compose exec postgres psql -U booking -d booking
```

## Полезные команды SQL

```sql
-- Список таблиц
\dt

-- Структура таблицы
\d users

-- Просмотр данных
SELECT * FROM users;
SELECT * FROM houses;
SELECT * FROM bookings;
```
