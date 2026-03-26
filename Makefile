.PHONY: install run lint format docker-build docker-run docker-down docker-restart

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
