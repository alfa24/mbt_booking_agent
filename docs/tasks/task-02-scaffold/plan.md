# План: Генерация каркаса проекта backend

## Цель

Создать структуру backend-проекта с FastAPI, настроенными зависимостями и инструментами разработки.

## Задачи

### Task 1: Обновление pyproject.toml

Добавить зависимости backend в существующий `pyproject.toml`:

```toml
[project.dependencies]
# existing: aiogram, openai, pydantic-settings, python-dotenv
fastapi = "^0.110.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.0"}
asyncpg = "^0.29.0"
alembic = "^1.13.0"
pydantic = "^2.5.0"
httpx = "^0.27.0"  # для тестов

[dependency-groups]
dev = [
    "ruff>=0.4",
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
]
```

### Task 2: Создание структуры директорий

Создать директорию `backend/` со следующей структурой:

```
backend/
├── __init__.py
├── main.py              # Точка входа FastAPI
├── config.py            # Pydantic-settings конфигурация
├── dependencies.py      # Dependency injection
├── database.py          # Подключение к БД (заглушка для MVP)
├── api/
│   ├── __init__.py      # Агрегация роутеров
│   └── health.py        # Health check endpoint
├── schemas/
│   ├── __init__.py
│   └── common.py        # ErrorResponse
├── models/
│   └── __init__.py
├── services/
│   └── __init__.py
└── tests/
    ├── __init__.py
    └── test_health.py   # Базовый тест
```

### Task 3: Реализация config.py

Создать конфигурацию на Pydantic-settings:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration."""

    model_config = SettingsConfigDict(env_prefix="BACKEND_", env_file=".env")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (placeholder for MVP)
    database_url: str = "postgresql+asyncpg://user:pass@localhost/booking"

    # Logging
    log_level: str = "INFO"


settings = Settings()
```

### Task 4: Реализация main.py

Создать FastAPI приложение с lifespan events, CORS middleware и обработкой ошибок:

```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting up Booking API...")
    yield
    logger.info("Shutting down Booking API...")


app = FastAPI(
    title="Booking API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred"},
    )
```

### Task 5: Реализация api/health.py

```python
from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

### Task 6: Реализация schemas/common.py

```python
from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[list] = None
```

### Task 7: Обновление Makefile и docker-compose

Добавить команды для backend через Docker:

```makefile
# Backend commands (Docker)
run-backend:
	docker compose up backend -d

run-backend-logs:
	docker compose logs backend -f

stop-backend:
	docker compose stop backend

build-backend:
	docker compose build backend

lint-backend:
	docker compose exec backend uv run ruff check backend/

format-backend:
	docker compose exec backend uv run ruff format backend/

test-backend:
	docker compose exec backend uv run pytest backend/tests/ -v
```

Обновить `docker-compose.yaml` - добавить сервис backend:

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8001:8000"
    environment:
      - BACKEND_HOST=0.0.0.0
      - BACKEND_PORT=8000
      - BACKEND_LOG_LEVEL=INFO
    env_file:
      - .env
    volumes:
      - ./backend:/app/backend
    command: uv run python -m backend.main
```

Создать `Dockerfile.backend`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync

COPY backend/ ./backend/

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "backend.main"]
```

### Task 8: Обновление .env.example

Добавить переменные backend:

```
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/booking
BACKEND_LOG_LEVEL=INFO
```

### Task 9: Тестирование

Создать базовый тест `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.1.0"
```

## Проверка (Definition of Done)

- [ ] `make build-backend` собирает образ без ошибок
- [ ] `make run-backend` запускает контейнер на порту 8001
- [ ] `curl http://localhost:8001/health` возвращает `{"status": "ok"}`
- [ ] `curl http://localhost:8001/docs` открывает Swagger UI
- [ ] `make lint-backend` проходит без ошибок (внутри контейнера)
- [ ] `make test-backend` проходит успешно (внутри контейнера)

## Артефакты

| Файл | Назначение |
|------|------------|
| `backend/main.py` | Точка входа FastAPI |
| `backend/config.py` | Pydantic-settings конфигурация |
| `backend/api/health.py` | Health check endpoint |
| `backend/schemas/common.py` | ErrorResponse схема |
| `backend/tests/test_health.py` | Базовый тест |
| `pyproject.toml` | Обновлённые зависимости |
| `Makefile` | Команды для backend |
| `docker-compose.yaml` | Сервис backend |
| `Dockerfile.backend` | Образ для backend |
| `.env.example` | Переменные окружения |
