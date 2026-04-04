# Getting Started Guide

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [Makefile](file://Makefile)
- [pyproject.toml](file://pyproject.toml)
- [docker-compose.yaml](file://docker-compose.yaml)
- [Dockerfile](file://Dockerfile)
- [Dockerfile.backend](file://Dockerfile.backend)
- [alembic.ini](file://alembic.ini)
- [backend/main.py](file://backend/main.py)
- [backend/config.py](file://backend/config.py)
- [bot/main.py](file://bot/main.py)
- [bot/config.py](file://bot/config.py)
- [backend/api/houses.py](file://backend/api/houses.py)
- [backend/api/bookings.py](file://backend/api/bookings.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Quick Setup and Run](#quick-setup-and-run)
4. [Local Development (Bot Only)](#local-development-bot-only)
5. [Full System Deployment (Docker)](#full-system-deployment-docker)
6. [Environment Configuration (.env)](#environment-configuration-env)
7. [Makefile Commands](#makefile-commands)
8. [API Testing Examples](#api-testing-examples)
9. [Development Workflow](#development-workflow)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Verification Steps](#verification-steps)
12. [Conclusion](#conclusion)

## Introduction
This guide helps you quickly set up and run the fullstack booking system locally and in Docker. The system consists of:
- A Telegram bot that interprets natural language requests and communicates with the backend.
- A FastAPI backend exposing REST endpoints for houses, tariffs, users, and bookings.
- A PostgreSQL database with Alembic migrations.
- Optional web application integration (planned).

You can develop and test the Telegram bot locally without Docker, or deploy the full stack using Docker Compose for realistic end-to-end testing.

## Prerequisites
- Python 3.12 or newer
- uv (Python dependency and packaging tool)
- Docker and Docker Compose
- A text editor or IDE
- curl or a GUI HTTP client (e.g., Insomnia, Postman) for API testing

These requirements are confirmed by the project’s documentation and configuration.

**Section sources**
- [README.md:128-133](file://README.md#L128-L133)
- [pyproject.toml:5](file://pyproject.toml#L5)

## Quick Setup and Run
Choose one of the two primary workflows below depending on whether you want to run just the bot locally or the full system with Docker.

- Local development (bot only): install dependencies, then run the bot.
- Full system (Docker): configure environment, start PostgreSQL, apply migrations, run backend, verify health, then run the bot.

**Section sources**
- [README.md:41-80](file://README.md#L41-L80)

## Local Development (Bot Only)
Follow these steps to run the Telegram bot locally without Docker.

1) Install dependencies
- Use uv to synchronize packages based on the project configuration.
- Command: make install

2) Prepare environment
- Copy the example environment file to .env and fill in required tokens.
- Command: cp .env.example .env (then edit .env)

3) Run the bot
- Command: make run

4) Optional: Lint and format
- Lint: make lint
- Format: make format

Expected outcome:
- The bot starts polling and listens for messages.
- Logs show initialization and polling activity.

Notes:
- The bot reads configuration from .env via bot.config.Settings.
- It initializes BackendClient and LLMService and registers message handlers.

**Section sources**
- [README.md:41-57](file://README.md#L41-L57)
- [Makefile:4-14](file://Makefile#L4-L14)
- [bot/main.py:15-46](file://bot/main.py#L15-L46)
- [bot/config.py:44-67](file://bot/config.py#L44-L67)

## Full System Deployment (Docker)
Deploy the complete system: PostgreSQL, backend, and bot.

1) Configure environment
- Copy the example environment file to .env and add required tokens.
- Command: cp .env.example .env (then edit .env)

2) Start PostgreSQL
- Command: docker compose up -d postgres

3) Apply database migrations
- Command: make migrate

4) Run backend
- Command: make run-backend

5) Verify backend health
- Command: curl http://localhost:8001/health

6) Run the bot (in another terminal)
- Command: make run

Expected outcome:
- PostgreSQL initializes and becomes healthy.
- Backend responds to /health.
- Bot connects to Telegram and polls for updates.
- Swagger UI is available at http://localhost:8001/docs.

Notes:
- Backend binds to port 8000 inside the container; the compose file exposes it on 8001 for external access.
- The backend loads settings from .env via backend.config.Settings.
- The bot uses backend_api_url to communicate with the backend service.

**Section sources**
- [README.md:59-80](file://README.md#L59-L80)
- [docker-compose.yaml:1-43](file://docker-compose.yaml#L1-L43)
- [backend/main.py:62-64](file://backend/main.py#L62-L64)
- [backend/config.py:4-25](file://backend/config.py#L4-L25)
- [bot/config.py:56](file://bot/config.py#L56)
- [README.md:132](file://README.md#L132)

## Environment Configuration (.env)
Create and edit .env with the following keys:
- TELEGRAM_BOT_TOKEN: Your Telegram bot token.
- ROUTERAI_API_KEY: API key for the LLM provider.
- Optional: ROUTERAI_BASE_URL, LLM_MODEL, SYSTEM_PROMPT, LOG_LEVEL, BACKEND_* settings if overriding defaults.

Notes:
- The bot reads .env via bot.config.Settings.
- The backend reads .env via backend.config.Settings with BACKEND_ prefix support.
- The Docker Compose file passes .env into the bot and backend containers.

**Section sources**
- [bot/config.py:44-67](file://bot/config.py#L44-L67)
- [backend/config.py:4-25](file://backend/config.py#L4-L25)
- [docker-compose.yaml:18-31](file://docker-compose.yaml#L18-L31)

## Makefile Commands
The Makefile provides convenient commands for local and Docker-based workflows.

Backend commands (Docker-based):
- run-backend: Start backend service in detached mode.
- run-backend-logs: View backend logs in real-time.
- stop-backend: Stop backend service.
- build-backend: Rebuild backend image.
- test-backend: Run backend tests.
- test-backend-cov: Run tests with coverage reports.
- lint-backend: Lint backend code.
- format-backend: Format backend code.

Database commands:
- migrate: Upgrade database to latest Alembic revision.
- migrate-create: Create a new revision with a given name.
- migrate-down: Downgrade database by one revision.
- postgres-up: Start PostgreSQL service.
- postgres-logs: View PostgreSQL logs.

Local commands:
- install: Synchronize dependencies with uv.
- run: Run the bot locally.
- lint: Lint the project.
- format: Format the project.

Notes:
- Many commands execute inside Docker containers using docker compose exec.
- Backend tests and lint/format operate on the backend/ directory.

**Section sources**
- [Makefile:1-71](file://Makefile#L1-L71)

## API Testing Examples
Use these examples to verify the backend after deploying with Docker.

- Health check
  - curl http://localhost:8001/health

- List houses
  - curl http://localhost:8001/api/v1/houses

- Create a booking
  - curl -X POST http://localhost:8001/api/v1/bookings \
    -H "Content-Type: application/json" \
    -d '{...}'

- Filter bookings
  - curl "http://localhost:8001/api/v1/bookings?house_id=1&status=confirmed"

Swagger UI is available at http://localhost:8001/docs for interactive exploration.

**Section sources**
- [README.md:102-124](file://README.md#L102-L124)
- [backend/main.py:41-64](file://backend/main.py#L41-L64)
- [backend/api/houses.py:21-52](file://backend/api/houses.py#L21-L52)
- [backend/api/bookings.py:20-51](file://backend/api/bookings.py#L20-L51)

## Development Workflow
Recommended iteration loop:
1) Edit code locally.
2) Lint/format with make lint and make format.
3) Run backend tests with make test-backend (or make test-backend-cov for coverage).
4) For end-to-end testing, run the full Docker stack:
   - docker compose up -d postgres
   - make migrate
   - make run-backend
   - make run (in another terminal)
5) Verify with curl or Swagger UI.

Optional:
- Use docker compose logs to inspect backend or PostgreSQL logs.
- Use docker compose down to tear down the stack cleanly.

**Section sources**
- [Makefile:31-71](file://Makefile#L31-L71)
- [docker-compose.yaml:1-43](file://docker-compose.yaml#L1-L43)

## Troubleshooting Guide
Common issues and resolutions:

- Backend does not start or health check fails
  - Ensure PostgreSQL is healthy and reachable.
  - Confirm database URL matches the Docker network and credentials.
  - Check backend logs with make run-backend-logs.

- Database migration errors
  - Verify migrations applied: make migrate.
  - Create a new migration if schema changes: make migrate-create name="<description>".
  - Roll back if needed: make migrate-down.

- Bot not responding
  - Confirm TELEGRAM_BOT_TOKEN is set in .env.
  - Ensure backend is running and accessible at backend_api_url (default http://backend:8000).
  - Check bot logs and verify proxy settings if used.

- Port conflicts
  - Backend is exposed on port 8001 externally; adjust host mapping if conflicting with other services.

- uv sync failures
  - Ensure Python 3.12+ is installed and uv is available.
  - Reinstall dependencies with make install.

**Section sources**
- [Makefile:57-71](file://Makefile#L57-L71)
- [docker-compose.yaml:25-36](file://docker-compose.yaml#L25-L36)
- [backend/config.py:17-18](file://backend/config.py#L17-L18)
- [bot/config.py:56](file://bot/config.py#L56)

## Verification Steps
After completing setup, confirm the system works as expected:

- Local bot only
  - make run produces logs indicating the bot is polling.
  - make lint and make format succeed without errors.

- Full Docker system
  - docker compose ps shows postgres, backend, and bot services running.
  - curl http://localhost:8001/health returns {"status":"ok"}.
  - curl http://localhost:8001/api/v1/houses lists houses.
  - Swagger UI at http://localhost:8001/docs is accessible.
  - make run starts the bot and logs indicate readiness.

**Section sources**
- [README.md:59-80](file://README.md#L59-L80)
- [backend/main.py:62-64](file://backend/main.py#L62-L64)
- [docker-compose.yaml:1-43](file://docker-compose.yaml#L1-L43)
- [README.md:132](file://README.md#L132)

## Conclusion
You now have two pathways to get productive quickly:
- Develop and iterate on the Telegram bot locally with uv.
- Deploy the full stack with Docker Compose for realistic integration testing.

Use the Makefile to streamline tasks, the .env file to configure secrets, and the API examples to validate functionality. Refer to the troubleshooting section if you encounter issues.