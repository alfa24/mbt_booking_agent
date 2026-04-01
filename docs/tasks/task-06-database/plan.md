# План: Задача 06 - Подключение PostgreSQL

## Цель
Заменить in-memory хранение на PostgreSQL с миграциями. Проект, миграции и тесты запускаются только в Docker.

---

## Task 1: Настройка SQLAlchemy 2.0 с asyncpg

**Файлы:**
- `backend/database.py` - подключение к БД

**Действия:**
1. Создать `create_async_engine` с `postgresql+asyncpg`
2. Настроить `AsyncSessionLocal` с `sessionmaker`
3. Создать `Base = declarative_base()`
4. Реализовать `get_db()` dependency для FastAPI
5. Обновить `lifespan` в `main.py` для инициализации/закрытия соединений

**Код для `backend/database.py`:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.config import settings

engine = create_async_engine(settings.database_url, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
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

---

## Task 2: Создание SQLAlchemy моделей

**Файлы:**
- `backend/models/user.py`
- `backend/models/house.py`
- `backend/models/booking.py`
- `backend/models/tariff.py`

**Модель User:**
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

**Модель House:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base

class House(Base):
    __tablename__ = "houses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    capacity = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Модель Tariff:**
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Tariff(Base):
    __tablename__ = "tariffs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Модель Booking:**
```python
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from backend.database import Base
import enum

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    guests_planned = Column(JSON, nullable=False)
    guests_actual = Column(JSON)
    total_amount = Column(Integer)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Task 3: Настройка Alembic для миграций

**Действия (выполняются в Docker):**
1. Инициализировать Alembic: `docker compose exec backend alembic init alembic`
2. Настроить `alembic/env.py` для работы с asyncpg
3. Обновить `alembic.ini` - указать sqlalchemy.url

**Код для `alembic/env.py`:**
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from backend.config import settings
from backend.database import Base
from backend.models import user, house, tariff, booking

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Task 4: Создание начальной миграции

**Действия (в Docker):**
```bash
docker compose exec backend alembic revision --autogenerate -m "Initial migration"
```

---

## Task 5: Реализация SQLAlchemy репозиториев

**Файлы:**
- `backend/repositories/user.py` - обновить для работы с БД
- `backend/repositories/house.py` - обновить для работы с БД
- `backend/repositories/booking.py` - обновить для работы с БД
- `backend/repositories/tariff.py` - обновить для работы с БД

**Паттерн для репозитория (пример UserRepository):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.user import User
from backend.schemas.user import UserResponse, UserRole

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, telegram_id: str, name: str, role: UserRole) -> UserResponse:
        user = User(telegram_id=telegram_id, name=name, role=role)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return UserResponse.model_validate(user)
    
    async def get(self, user_id: int) -> UserResponse | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None
    
    async def get_by_telegram_id(self, telegram_id: str) -> UserResponse | None:
        result = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None
    
    async def get_all(self, role: UserRole | None = None, limit: int = 20, offset: int = 0, sort: str | None = None):
        query = select(User)
        if role:
            query = query.where(User.role == role)
        if sort:
            reverse = sort.startswith("-")
            field = sort[1:] if reverse else sort
            if hasattr(User, field):
                order = getattr(User, field).desc() if reverse else getattr(User, field)
                query = query.order_by(order)
        
        count_result = await self._session.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar()
        
        query = query.offset(offset).limit(limit)
        result = await self._session.execute(query)
        users = result.scalars().all()
        return [UserResponse.model_validate(u) for u in users], total
    
    async def update(self, user_id: int, name: str | None = None, role: UserRole | None = None) -> UserResponse | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if name is not None:
            user.name = name
        if role is not None:
            user.role = role
        await self._session.flush()
        await self._session.refresh(user)
        return UserResponse.model_validate(user)
    
    async def delete(self, user_id: int) -> bool:
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        await self._session.delete(user)
        return True
```

---

## Task 6: Обновление сервисов для работы с async репозиториями

**Файлы:**
- `backend/services/user.py`
- `backend/services/house.py`
- `backend/services/booking.py`
- `backend/services/tariff.py`

**Изменения:**
1. Все методы сервисов становятся `async`
2. `get_*_repository()` возвращает инстанс с сессией БД
3. Обновить dependency injection в API роутерах

**Пример обновленного `get_user_repository`:**
```python
from backend.database import get_db
from backend.repositories.user import UserRepository

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)
```

---

## Task 7: Обновление API роутеров

**Файлы:**
- `backend/api/users.py`
- `backend/api/houses.py`
- `backend/api/bookings.py`
- `backend/api/tariffs.py`

**Изменения:**
1. Добавить `async` ко всем endpoint-функциям
2. Обновить вызовы сервисов с `await`

---

## Task 8: Обновление docker-compose.yaml с PostgreSQL

**Файл:** `docker-compose.yaml`

**Добавить сервис postgres:**
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
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U booking"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    # ... existing config ...
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - BACKEND_DATABASE_URL=postgresql+asyncpg://booking:booking@postgres/booking

volumes:
  postgres_data:
```

---

## Task 9: Обновление .env.example

**Файл:** `.env.example`

**Добавить:**
```
# Database
POSTGRES_USER=booking
POSTGRES_PASSWORD=booking
POSTGRES_DB=booking
```

---

## Task 10: Обновление Makefile

**Файл:** `Makefile`

**Добавить команды:**
```makefile
# Database commands (Docker)
migrate:
	docker compose exec backend uv run alembic upgrade head

migrate-create:
	docker compose exec backend uv run alembic revision --autogenerate -m "$(name)"

migrate-down:
	docker compose exec backend uv run alembic downgrade -1

postgres-up:
	docker compose up postgres -d

postgres-logs:
	docker compose logs postgres -f
```

---

## Task 11: Обновление тестов для работы с БД

**Файлы:**
- `backend/tests/conftest.py` - создать
- `backend/tests/test_*.py` - обновить

**conftest.py:**
```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.database import Base, get_db
from backend.main import app
from httpx import AsyncClient

TEST_DATABASE_URL = "postgresql+asyncpg://booking:booking@postgres/booking_test"

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

**Обновить тесты:**
- Заменить `TestClient` на `AsyncClient`
- Добавить `pytest.mark.asyncio` к тестам
- Использовать `async def` для тестовых функций

---

## Task 12: Ревью измененных файлов

**Действия:**
1. Вызвать `/python-senior-practices` для ревью кода
2. Применить замечания по:
   - Асинхронным паттернам
   - Обработке ошибок
   - Типизации
   - SQLAlchemy best practices

---

## Task 13: Ревью тестов

**Действия:**
1. Вызвать `/python-testing-patterns` для ревью тестов
2. Применить замечания по:
   - Фикстурам
   - Изоляции тестов
   - Async тестированию
   - Покрытию

---

## Task 14: Актуализация summary

**Файл:** `docs/tasks/task-06-database/summary.md`

**Содержание:**
- Что было реализовано
- Архитектурные решения
- Проблемы и их решения
- Инструкции по запуску

---

## Task 15: Актуализация прогресса tasklist-backend.md

**Файл:** `docs/tasks/tasklist-backend.md` (строки 324-341)

**Обновить:**
- [x] Настройка SQLAlchemy 2.0 с asyncpg
- [x] Создание моделей: User, House, Booking, Tariff
- [x] Настройка Alembic для миграций
- [x] Создание начальной миграции
- [x] Реализация репозиториев/DAO
- [x] Обновление `docker-compose.yaml` с PostgreSQL
- [x] Обновление `.env.example`
- [x] Обновление `Makefile`
- [x] Тесты проходят с тестовой БД

---

## Definition of Done

- [ ] БД поднимается: `docker compose up postgres`
- [ ] Миграции применяются: `make migrate`
- [ ] API работает с БД — данные сохраняются между перезапусками
- [ ] Тесты проходят с тестовой БД: `make test-backend`

## Проверка пользователем

```bash
# Запуск инфраструктуры
docker compose up -d postgres

# Применение миграций
make migrate

# Запуск backend
make run-backend

# Проверка: создать бронирование
curl -X POST http://localhost:8001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"house_id": 1, "check_in": "2024-06-01", "check_out": "2024-06-03", "guests": [{"tariff_id": 2, "count": 2}]}'

# Перезапуск сервера и проверка что данные на месте
make stop-backend
make run-backend
curl http://localhost:8001/api/v1/bookings

# Запуск тестов
make test-backend
```
