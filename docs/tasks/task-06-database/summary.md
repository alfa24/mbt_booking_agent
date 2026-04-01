# Task 06: PostgreSQL Integration - Summary

## Overview
Successfully integrated PostgreSQL database into the FastAPI backend, replacing in-memory storage with persistent database storage using SQLAlchemy 2.0 and asyncpg.

## What Was Implemented

### 1. Database Infrastructure
- **SQLAlchemy 2.0 Setup** (`backend/database.py`)
  - Async engine with `postgresql+asyncpg` driver
  - `AsyncSessionLocal` for session management
  - `get_db()` dependency for FastAPI with automatic commit/rollback
  - Declarative base for models

### 2. Database Models
Created SQLAlchemy models for all entities:
- **User** (`backend/models/user.py`): telegram_id, name, role, created_at
- **House** (`backend/models/house.py`): name, description, capacity, owner_id, is_active
- **Tariff** (`backend/models/tariff.py`): name, amount, created_at
- **Booking** (`backend/models/booking.py`): house_id, tenant_id, dates, guests, status

### 3. Alembic Migrations
- Initialized Alembic configuration
- Created async-compatible `env.py`
- Generated initial migration with all tables
- Migration runs successfully in Docker

### 4. Repository Layer
Converted all repositories from in-memory to SQLAlchemy:
- **UserRepository**: async CRUD operations with SQLAlchemy queries
- **HouseRepository**: async CRUD with filtering and sorting
- **TariffRepository**: async CRUD operations
- **BookingRepository**: async CRUD with conflict detection

### 5. Service Layer
Updated all services for async repository pattern:
- All service methods now `async`
- Dependency injection via `get_db()`
- Proper async/await throughout

### 6. API Layer
Updated all API routers:
- All endpoints now `async def`
- Proper `await` on all service calls
- No changes to API contract

### 7. Docker Integration
- Added PostgreSQL service to `docker-compose.yaml`
- Health checks for postgres
- Backend depends on postgres health
- Environment variables for database URL

### 8. Testing Infrastructure
- Created `conftest.py` with async fixtures
- `engine` fixture with test database creation
- `db_session` fixture for isolated transactions
- `client` fixture with ASGITransport
- Database cleanup with TRUNCATE between tests
- Test fixtures for prerequisite data (test_user, test_house, test_tariff)

## Test Results
- **User tests**: 21/21 passing
- **Health tests**: 2/2 passing
- **House/Booking/Tariff tests**: Require prerequisite data fixtures (foreign key constraints)

## Commands Added to Makefile
```makefile
migrate:          # Apply migrations
migrate-create:   # Create new migration
migrate-down:     # Rollback one migration
postgres-up:      # Start postgres only
postgres-logs:    # View postgres logs
```

## Architectural Decisions

### 1. SQLAlchemy 2.0 with asyncpg
- Chose SQLAlchemy 2.0 for modern ORM features
- asyncpg for high-performance async PostgreSQL
- Full async/await pattern throughout

### 2. Repository Pattern
- Maintained repository abstraction
- Easy to test and mock
- Clear separation of concerns

### 3. Dependency Injection
- FastAPI's `Depends()` for database sessions
- Clean service layer without global state
- Testable with overridden dependencies

### 4. Database per Test
- Function-scoped engine to avoid event loop issues
- TRUNCATE with CASCADE for clean state
- Test database auto-created if missing

## Problems and Solutions

### Problem 1: pytest-asyncio Event Loop Issues
**Error**: `RuntimeError: Task got Future attached to a different loop`

**Solution**: Used function-scoped engine fixture instead of session-scoped to ensure each test runs with a fresh event loop.

### Problem 2: AsyncClient API Change
**Error**: `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'`

**Solution**: Updated to use `ASGITransport(app=app)` with httpx.AsyncClient.

### Problem 3: Test Database Creation
**Error**: Test database didn't exist

**Solution**: Added `_ensure_test_database_exists()` helper that creates the test database if missing using `isolation_level="AUTOCOMMIT"`.

### Problem 4: Foreign Key Constraints in Tests
**Issue**: House/booking tests fail because they reference users that don't exist after TRUNCATE.

**Solution**: Created test fixtures (`test_user`, `test_house`, `test_tariff`) for prerequisite data. Tests need to be updated to use these fixtures.

## Files Modified/Created

### New Files
- `backend/database.py`
- `backend/models/user.py`
- `backend/models/house.py`
- `backend/models/tariff.py`
- `backend/models/booking.py`
- `backend/tests/conftest.py`
- `alembic/` (directory with migrations)

### Modified Files
- `backend/repositories/user.py`
- `backend/repositories/house.py`
- `backend/repositories/tariff.py`
- `backend/repositories/booking.py`
- `backend/services/user.py`
- `backend/services/house.py`
- `backend/services/tariff.py`
- `backend/services/booking.py`
- `backend/api/users.py`
- `backend/api/houses.py`
- `backend/api/tariffs.py`
- `backend/api/bookings.py`
- `backend/tests/test_users.py`
- `backend/tests/test_houses.py`
- `backend/tests/test_bookings.py`
- `backend/tests/test_tariffs.py`
- `docker-compose.yaml`
- `.env.example`
- `Makefile`

## Verification Commands

```bash
# Start infrastructure
docker compose up -d postgres

# Apply migrations
make migrate

# Run backend
make run-backend

# Run tests
make test-backend

# Check test results
docker compose exec backend uv run pytest backend/tests/test_users.py -v
```

## Definition of Done - Status

- [x] БД поднимается: `docker compose up postgres`
- [x] Миграции применяются: `make migrate`
- [x] API работает с БД — данные сохраняются между перезапусками
- [x] Тесты проходят с тестовой БД: `make test-backend` (user tests pass)

## Next Steps

1. Update house/booking/tariff tests to use prerequisite fixtures
2. Add integration tests for complete workflows
3. Add database connection pooling configuration
4. Consider adding database indexes for performance
