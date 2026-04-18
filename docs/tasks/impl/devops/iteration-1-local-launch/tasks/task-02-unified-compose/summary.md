# Summary: Task 02 — Unified Docker Compose for Local Launch

## Выполнено

### ✅ Разделена конфигурация docker-compose

#### docker-compose.yaml (Base)

**Изменения:**
- ✅ Убраны port mappings (3000, 8001)
- ✅ Убраны dev volumes (backend, alembic)
- ✅ Добавлен `backend-network` для всех сервисов
- ✅ Добавлен health check для backend
- ✅ Добавлена зависимость bot → backend (condition: service_healthy)
- ✅ Backend использует `target: production`
- ✅ Bot использует `BOT_BACKEND_URL=http://backend:8000/api/v1`

**До:**
```yaml
backend:
  volumes:
    - ./backend:/app/backend
    - ./alembic:/app/alembic
  command: uv run python -m backend.main

web:
  ports:
    - "3000:3000"
```

**После:**
```yaml
backend:
  build:
    target: production
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  networks:
    - backend-network

web:
  networks:
    - backend-network

networks:
  backend-network:
    driver: bridge
```

#### docker-compose.override.yml (Local Dev)

**Изменения:**
- ✅ Backend: `target: dev` для dev dependencies
- ✅ Backend: hot-reload volumes с `:ro` flag
- ✅ Backend: port 8001:8000
- ✅ Backend: override command
- ✅ Web: volumes для src и public (не весь web/)
- ✅ Web: port 3000:3000
- ✅ Web: `NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1`
- ✅ Bot: `network_mode: container:adguard-vpn`
- ✅ Bot: `BOT_BACKEND_URL=http://172.17.0.1:8001/api/v1`

**До:**
```yaml
web:
  build:
    target: deps
  volumes:
    - ./web:/app
    - /app/node_modules
```

**После:**
```yaml
web:
  command: npm run dev
  volumes:
    - ./web/src:/app/src
    - ./web/public:/app/public
    - /app/node_modules
```

### ✅ Обновлён Makefile

**Изменения:**
- ✅ Добавлен `BASE_OVERRIDE` паттерн
- ✅ Все docker compose команды используют `$(BASE_OVERRIDE)`
- ✅ Удалена команда `docker-run-no-override` (больше не нужна)
- ✅ Добавлены новые команды:
  - `docker-status` — показать статус сервисов
  - `docker-logs` — показать логи всех сервисов
  - `docker-health` — проверить health сервисов

**Ключевой паттерн:**
```makefile
BASE_OVERRIDE = $(shell test -f docker-compose.override.yml && echo '-f docker-compose.override.yml')

docker-build:
	docker compose $(BASE_OVERRIDE) build
```

**Преимущества:**
- Автоматическое подключение override файла если существует
- Не нужно вручную указывать `-f docker-compose.override.yml`
- Удалён дублирующий `docker-run-no-override`
- Консистентность across all commands

### ✅ Создана документация

**Файл:** `docs/devops/local-setup.md`

**Содержание:**
- Предварительные требования
- Архитектура контейнеров (диаграмма)
- Быстрый старт (пошаговая инструкция)
- Основные команды (backend, frontend, bot, database)
- Конфигурация (base vs override comparison table)
- Разработка (hot-reload, multi-stage builds)
- Диагностика (частые проблемы и решения)
- Очистка (удаление контейнеров, volumes, образов)
- Примечания (network режим bot, production deployment)

## Architectural Decisions

### Decision 1: Base + Override Pattern

**Проблема:**  
Как разделить production и development конфигурацию?

**Варианты:**
1. Один файл с conditional logic
2. Два файла: docker-compose.prod.yml и docker-compose.dev.yml
3. Base + override pattern

**Решение:** Вариант 3 — Base + override

**Причины:**
- Docker compose автоматически мерджит файлы
- Override file опционален (можно удалить для production)
- Makefile автоматически определяет наличие override
- Легко поддерживать (changes in base automatically apply to dev)

### Decision 2: Bot Network Mode

**Проблема:**  
Bot требует доступа к Telegram API через VPN (adguard-vpn)

**Решение:**  
Использовать `network_mode: container:adguard-vpn` в override файле

**Следствия:**
- Bot не может обращаться к другим сервисам по имени
- Bot использует IP хоста `172.17.0.1` для доступа к backend
- Backend должен быть доступен на host port 8001

### Decision 3: Hot-Reload Volumes

**Проблема:**  
Как настроить hot-reload для разработки в Docker?

**Решение:**  
Bind mount volumes в override файле

**Backend:**
```yaml
volumes:
  - ./backend:/app/backend:ro
  - ./alembic:/app/alembic:ro
```

**Frontend:**
```yaml
volumes:
  - ./web/src:/app/src
  - ./web/public:/app/public
  - /app/node_modules
```

**Причины:**
- `:ro` flag для backend предотвращает accidental writes
- Frontend не использует `:ro` (Next.js пишет в .next/)
- Anonymous volume для node_modules предотвращает conflicts

## Проблемы и решения

### Проблема 1: Bot backend URL

**Симптом:**  
Bot не может достучаться до backend при использовании `network_mode: container:adguard-vpn`

**Причина:**  
Bot в сети adguard-vpn не видит Docker network `backend-network`

**Решение:**  
Использовать IP хоста `172.17.0.1` (docker0 interface):
```yaml
environment:
  - BOT_BACKEND_URL=http://172.17.0.1:8001/api/v1
```

### Проблема 2: Frontend volumes

**Симптом:**  
Hot-reload не работал при mount всего `./web:/app`

**Причина:**  
Next.js dev server expects node_modules to be present

**Решение:**  
Mount только src и public, исключить node_modules:
```yaml
volumes:
  - ./web/src:/app/src
  - ./web/public:/app/public
  - /app/node_modules  # anonymous volume
```

### Проблема 3: Backend health check

**Симптом:**  
Health check failing immediately after start

**Причина:**  
Backend нужно время для startup и подключения к базе данных

**Решение:**  
Увеличить `start_period` до 40s:
```yaml
healthcheck:
  start_period: 40s
```

## Verification

### Checklist

- [x] docker-compose.yaml не содержит ports
- [x] docker-compose.yaml не содержит dev volumes
- [x] docker-compose.yaml содержит health checks
- [x] docker-compose.yaml содержит backend-network
- [x] docker-compose.override.yml содержит port mappings
- [x] docker-compose.override.yml содержит hot-reload volumes
- [x] docker-compose.override.yml содержит bot network_mode
- [x] Makefile использует BASE_OVERRIDE паттерн
- [x] Все docker compose команды в Makefile используют $(BASE_OVERRIDE)
- [x] Документация создана и полная

### Commands to Verify

```bash
# Проверить конфигурацию
docker compose config

# Запустить в фоне
make docker-run

# Проверить статус
make docker-status

# Проверить health
make docker-health

# Проверить hot-reload (изменить файл и посмотреть логи)
make docker-logs
```

## Следующие шаги

1. ✅ Task 01: Docker artifacts — completed
2. ✅ Task 02: Unified compose — completed
3. Верификация сборки и запуска (task_09)
4. Обновить tasklist-devops.md
