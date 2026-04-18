.PHONY: install run lint format
.PHONY: docker-build docker-run docker-down docker-restart docker-status docker-logs docker-health
.PHONY: run-backend run-backend-logs stop-backend build-backend lint-backend format-backend test-backend test-backend-cov
.PHONY: migrate migrate-create migrate-down postgres-up postgres-logs
.PHONY: install-frontend run-frontend build-frontend lint-frontend
.PHONY: run-bot stop-bot logs-bot backend-fixtures

# Conditional override file inclusion
BASE_COMPOSE = -f docker-compose.yaml
BASE_OVERRIDE = $(shell test -f docker-compose.override.yml && echo '-f docker-compose.override.yml')
COMPOSE = docker compose $(BASE_COMPOSE) $(BASE_OVERRIDE)

install:
	uv sync

run:
	uv run python -m bot.main

lint:
	uv run ruff check .

format:
	uv run ruff format .

# Docker core commands
docker-build:
	$(COMPOSE) build

docker-run:
	$(COMPOSE) up

docker-down:
	$(COMPOSE) down

docker-restart:
	$(COMPOSE) down && $(COMPOSE) up --build

docker-status:
	$(COMPOSE) ps

docker-logs:
	$(COMPOSE) logs -f

docker-health:
	$(COMPOSE) ps --format json | jq -r '.[] | "\(.Service): \(.State)"'

# Backend commands (Docker)
run-backend:
	$(COMPOSE) up backend -d

run-backend-logs:
	$(COMPOSE) logs backend -f

stop-backend:
	$(COMPOSE) stop backend

build-backend:
	$(COMPOSE) build backend

lint-backend:
	$(COMPOSE) exec backend uv run ruff check backend/

format-backend:
	$(COMPOSE) exec backend uv run ruff format backend/

test-backend:
	$(COMPOSE) exec backend uv run pytest backend/tests/ -v $(ARGS)

test-backend-cov: ARGS=--cov=backend --cov-report=term-missing --cov-report=html:htmlcov
test-backend-cov: test-backend

# Database commands (Docker)
migrate:
	$(COMPOSE) run --rm backend uv run alembic upgrade head

migrate-create:
	$(COMPOSE) run --rm backend uv run alembic revision --autogenerate -m "$(name)"

migrate-down:
	$(COMPOSE) run --rm backend uv run alembic downgrade -1

postgres-up:
	$(COMPOSE) up postgres -d

postgres-logs:
	$(COMPOSE) logs postgres -f

# Frontend commands
install-frontend:
	cd web && npm install

run-frontend:
	$(COMPOSE) up web

build-frontend:
	cd web && npm run build

lint-frontend:
	cd web && npm run lint

# Fixtures commands (Docker)
backend-fixtures:
	$(COMPOSE) exec backend uv run python -m backend.fixtures.load_fixtures

# Bot commands
run-bot:
	$(COMPOSE) up -d bot

stop-bot:
	$(COMPOSE) stop bot

logs-bot:
	$(COMPOSE) logs bot -f
