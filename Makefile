.PHONY: install run lint format docker-build docker-run docker-down docker-restart
.PHONY: run-backend run-backend-logs stop-backend build-backend lint-backend format-backend test-backend

install:
	uv sync

run:
	uv run python -m bot.main

lint:
	uv run ruff check .

format:
	uv run ruff format .

docker-build:
	docker compose build

docker-run:
	docker compose up

docker-down:
	docker compose down

docker-restart:
	docker compose down && docker compose up --build

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
