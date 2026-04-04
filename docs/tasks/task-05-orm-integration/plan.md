# План: Задача 05 - ORM-модели, репозитории и интеграция в backend

## Цель

Реализовать ORM-модели, слой доступа к данным (репозитории) и интегрировать их в backend для замены in-memory хранения.

## Фактически реализовано

### SQLAlchemy модели

**backend/models/user.py:**
```python
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

**backend/models/house.py:**
```python
class House(Base):
    __tablename__ = "houses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    capacity = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**backend/models/booking.py:**
```python
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

**backend/models/tariff.py:**
```python
class Tariff(Base):
    __tablename__ = "tariffs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Репозитории

- **UserRepository** — CRUD + поиск по telegram_id
- **HouseRepository** — CRUD + фильтры по owner_id, is_active, capacity
- **BookingRepository** — CRUD + проверка пересечения дат
- **TariffRepository** — CRUD

Паттерн: каждый репозиторий принимает `AsyncSession` в конструкторе.

### Сервисы

- **UserService** — бизнес-логика для пользователей
- **HouseService** — бизнес-логика для домов
- **BookingService** — бизнес-логика для бронирований
- **TariffService** — бизнес-логика для тарифов

Dependency injection через `Depends(get_db)`.

### API роутеры

- **users.py** — async endpoints с UserService
- **houses.py** — async endpoints с HouseService
- **bookings.py** — async endpoints с BookingService
- **tariffs.py** — async endpoints с TariffService

### Тесты

- **conftest.py** — фикстуры для async тестовой БД
- **test_users.py** — 21/21 тестов проходят
- Остальные тесты требуют обновления

## Состав работ (документирование)

### 1. Создание plan.md

Описать:
- Структуру ORM-моделей
- Паттерн Repository
- Интеграцию сервисов
- API роутеры
- Тестовую инфраструктуру

### 2. Создание summary.md

Описать что реализовано:
- Модели и их поля
- Репозитории и их методы
- Сервисы и DI
- API endpoints
- Статус тестов

## Definition of Done

- [ ] Все ORM-модели созданы и соответствуют физической модели
- [ ] Репозитории реализуют весь необходимый функционал
- [ ] API работает с PostgreSQL — данные сохраняются между перезапусками
- [ ] Тесты проходят с тестовой БД
- [ ] In-memory хранение полностью удалено

## Проверка пользователем

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

# Перезапуск и проверка
make stop-backend
make run-backend
curl http://localhost:8000/api/v1/bookings

# Тесты
make test-backend
```
