# DevOps Tasklist

## Обзор

Планирование и реализация DevOps-инфраструктуры проекта: контейнеризация, локальная разработка, CI/CD пайплайны. Цель — обеспечить воспроизводимый локальный запуск всего стека и автоматизацию сборки образов.

## Легенда статусов

- 📋 Planned - Запланирован
- 🚧 In Progress - В работе
- ✅ Done - Завершен

## Список задач

| Задача | Описание | Статус | Документы |
|--------|----------|--------|-----------|
| 01 | Структура devops-артефактов и Dockerfile | Создание директорий, Dockerfile, .dockerignore | 📋 Planned | [план](tasks/task-01-docker-structure/plan.md) \| [summary](tasks/task-01-docker-structure/summary.md) |
| 02 | Единый docker-compose для локального запуска | Консолидация compose-файлов, Makefile команды, документация | 📋 Planned | [план](tasks/task-02-compose-consolidation/plan.md) \| [summary](tasks/task-02-compose-consolidation/summary.md) |
| 03 | GitHub Actions workflow для сборки образов | CI/CD пайплайн сборки и публикации в GHCR | 🚧 In Progress | [план](tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/plan.md) \| [summary](tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/summary.md) |
| 04 | Ревью Docker- и CI-конфигураций | Security audit, resource limits, health checks, Trivy scanning | ✅ Done | [summary](tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-04-docker-review/summary.md) |

---

## Итерация 1: Локальный запуск всего проекта ✅

### Цель

Обеспечить полный запуск всех сервисов проекта (backend, frontend, bot, PostgreSQL) одной командой с правильной конфигурацией и документацией.

### Состав работ

#### Задача 01: Структура devops-артефактов и Dockerfile ✅ Done

**Статус**: ✅ Завершено

**Цель**

Спроектировать и создать структуру для хранения всех Docker-артефактов с обоснованием архитектурных решений.

**Состав работ**

- [x] Спроектировать структуру директории `devops/` с обоснованием (вложенность по сервисам, общие конфиги)
- [x] Перенести существующие Dockerfile в `devops/` или оставить в корне с обоснованием
- [x] Создать `.dockerignore` для каждого сервиса (backend, frontend, bot)
- [x] Провести ревью Dockerfile через skill `docker-expert`
- [x] Обновить ссылки в docker-compose на новые пути (если Dockerfile перемещены)

**Артефакты**

- `.dockerignore`, `.dockerignore.backend`, `.dockerignore.frontend`
- `Dockerfile`, `Dockerfile.backend`, `Dockerfile.frontend` (обновлённые)
- `docs/tasks/impl/devops/iteration-1-local-launch/tasks/task-01-docker-artifacts/plan.md`
- `docs/tasks/impl/devops/iteration-1-local-launch/tasks/task-01-docker-artifacts/summary.md`

**Документы**

- 📋 [План](tasks/impl/devops/iteration-1-local-launch/tasks/task-01-docker-artifacts/plan.md)
- 📝 [Summary](tasks/impl/devops/iteration-1-local-launch/tasks/task-01-docker-artifacts/summary.md)

**Definition of Done**

- ✅ Self-check: Все Dockerfile собраны без ошибок, .dockerignore исключают лишние файлы (node_modules, .venv, __pycache__, .git)
- ✅ User-check: Разработчик может выполнить `docker compose build` без предупреждений о лишних файлах в контексте

---

#### Задача 02: Единый docker-compose для локального запуска ✅ Done

**Статус**: ✅ Завершено

**Цель**

Консолидировать docker-compose конфигурацию в единый файл с удобными Makefile-командами для управления полным стеком.

**Состав работ**

- [x] Объединить `docker-compose.yaml` и `docker-compose.override.yml` в единую конфигурацию (или оставить override с явным обоснованием)
- [x] Убедиться, что все сервисы (postgres, backend, frontend, bot) запускаются корректно
- [x] Проверить health checks для всех сервисов (минимум postgres и backend)
- [x] Настроить корректные сети и зависимости между сервисами (`depends_on` с condition)
- [x] Дополнить Makefile командами:
  - `make up` — подъём полного стека
  - `make down` — остановка и удаление контейнеров
  - `make status` — статус сервисов
  - `make logs` — логи всех сервисов
  - `make logs-service=backend` — логи конкретного сервиса
  - `make health` — быстрая проверка health endpoints
- [x] Удалить дублирующиеся команды из Makefile (заменить на новые)
- [x] Создать инструкцию по локальному запуску (`docs/devops/local-setup.md` или обновить README)
- [x] Обновить `architecture.md` и связанные документы с учётом новой структуры

**Артефакты**

- `docker-compose.yaml` (обновлённый, base конфигурация)
- `docker-compose.override.yml` (local dev overrides)
- `Makefile` (с BASE_OVERRIDE паттерном)
- `docs/devops/local-setup.md` (инструкция по запуску, 404 строки)
- `docs/tasks/impl/devops/iteration-1-local-launch/tasks/task-02-unified-compose/plan.md`
- `docs/tasks/impl/devops/iteration-1-local-launch/tasks/task-02-unified-compose/summary.md`

**Документы**

- 📋 [План](tasks/impl/devops/iteration-1-local-launch/tasks/task-02-unified-compose/plan.md)
- 📝 [Summary](tasks/impl/devops/iteration-1-local-launch/tasks/task-02-unified-compose/summary.md)

**Definition of Done**

- ✅ Self-check: `make up` поднимает все 4 сервиса, health checks проходят, сервисы доступны на ожидаемых портах
- ✅ User-check: Новый разработчик следует инструкции и запускает проект за <5 минут без дополнительных вопросов

---

## Итерация 2: Пайплайн сборки образов через GitHub Actions 🚧

### Цель

Автоматизировать сборку Docker-образов всех сервисов и публикацию в GitHub Container Registry (GHCR) при push в main branch.

### Состав работ

#### Задача 03: GitHub Actions workflow для сборки образов 🚧

**Статус**: 🚧 В работе

**Цель**

Создать CI/CD workflow для автоматической сборки, тегирования и публикации Docker-образов в GHCR.

**Состав работ**

- [x] Использовать skill `github-actions-templates` для создания workflow
- [x] Настроить workflow на trigger: push в `main`, manual dispatch
- [x] Реализовать build для linux/amd64 для каждого сервиса
- [x] Настроить публикацию в GHCR с тегами:
  - `latest` (для main)
  - `sha-{short_commit}` (для traceability)
- [x] Добавить кэширование слоёв для ускорения сборок
- [x] Создать compose-файл для запуска из registry (`docker-compose.prod.yaml`)
- [ ] Протестировать локальный запуск на основе образов из GHCR:
  - Pull образов из GHCR
  - Запуск через compose
  - Проверка health checks
- [ ] Обновить документацию по развёртыванию

**Артефакты**

- `.github/workflows/build-and-publish.yml`
- `docker-compose.prod.yaml` (для запуска из registry)
- `docs/tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/plan.md`
- `docs/tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/summary.md`

**Документы**

- 📋 [План](tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/plan.md)
- 📝 [Summary](tasks/impl/devops/iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/summary.md)

**Definition of Done**

- ✅ Self-check: Workflow завершается успешно, образы доступны в GHCR с корректными тегами
- ✅ User-check: Разработчик может выполнить `docker compose -f docker-compose.prod.yaml pull && docker compose up` и получить работающий стек из registry

---

## Связанные документы

- [architecture.md](../architecture.md) — архитектура системы
- [plan.md](../plan.md) — дорожная карта проекта
- [vision.md](../vision.md) — техническое видение
- [integrations.md](../integrations.md) — внешние сервисы
