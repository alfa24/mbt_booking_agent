# Plan: Iteration 1 — Local Project Launch

## Цель

Настроить Docker-конфигурацию для локальной разработки и обеспечить единый запуск всех сервисов через docker-compose.

## Состав работ

### Task 01: Docker artifacts structure and Dockerfile

- Создать .dockerignore файлы для каждого сервиса
- Оптимизировать Dockerfile (bot, backend, frontend)
- Добавить security hardening (non-root user, HEALTHCHECK, STOPSIGNAL)
- Разделить production и dev stages для backend

### Task 02: Unified docker-compose for local launch

- Разделить базовую конфигурацию (docker-compose.yaml) и локальные настройки (docker-compose.override.yml)
- Добавить health checks и dependency management
- Настроить hot-reload volumes для разработки
- Обновить Makefile с BASE_OVERRIDE паттерном
- Создать документацию по локальному запуску

## Архитектурные решения

### 1. Multi-stage builds

**Backend:**
- `base` — общие зависимости (uv, user)
- `production` — production dependencies only
- `dev` — development dependencies + hot-reload

**Frontend:**
- `deps` — зависимости
- `builder` — сборка Next.js
- `runner` — production runtime

**Bot:**
- Single stage (будет оптимизирован в future iterations)

### 2. Docker Compose разделение

**Base (docker-compose.yaml):**
- Production-ready конфигурация
- Service-to-service URLs (`http://backend:8000`)
- Health checks
- Custom network (`backend-network`)
- Без портов и dev volumes

**Override (docker-compose.override.yml):**
- Local development settings
- Port mappings (8001:8000, 3000:3000)
- Hot-reload volumes
- Bot network_mode: container:adguard-vpn
- Host-accessible URLs (`http://localhost:8001`, `http://172.17.0.1:8001`)

### 3. Makefile BASE_OVERRIDE pattern

```makefile
BASE_OVERRIDE = $(shell test -f docker-compose.override.yml && echo '-f docker-compose.override.yml')
```

Все docker compose команды используют `$(BASE_OVERRIDE)` для условного подключения override файла.

## Файлы

### Созданные
- `.dockerignore` — глобальный ignore для bot
- `.dockerignore.backend` — ignore для backend
- `.dockerignore.frontend` — ignore для frontend
- `docs/devops/local-setup.md` — документация по запуску

### Изменённые
- `Dockerfile` — bot (security hardening)
- `Dockerfile.backend` — multi-stage (production/dev)
- `Dockerfile.frontend` — non-root user, healthcheck
- `docker-compose.yaml` — base configuration
- `docker-compose.override.yml` — local dev settings
- `Makefile` — BASE_OVERRIDE pattern

## Verification

1. `docker compose build` — успешная сборка всех сервисов
2. `docker compose up` — запуск без ошибок
3. Health checks проходят для backend
4. Hot-reload работает для backend и frontend
5. Bot подключается к backend через adguard-vpn network
