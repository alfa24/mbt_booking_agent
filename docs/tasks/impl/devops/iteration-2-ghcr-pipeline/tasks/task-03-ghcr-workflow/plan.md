# Plan: GitHub Actions Workflow для сборки и публикации образов в GHCR

## Цель

Создать CI/CD pipeline для автоматической сборки Docker-образов всех сервисов (backend, frontend, bot) и публикации в GitHub Container Registry (GHCR) при push в main branch.

## Подход

### Архитектура workflow

- **Trigger**: push в `main` + ручной запуск (workflow_dispatch)
- **Стратегия**: matrix job для параллельной сборки 3 сервисов
- **Платформа**: linux/amd64 (упрощённо, без multi-arch)
- **Кэширование**: GitHub Actions cache (type: gha) для ускорения сборок
- **Теги**: `latest` + `sha-{short_commit}`

### Структура образов

| Сервис | Dockerfile | Target | Имя образа |
|--------|-----------|--------|------------|
| backend | `Dockerfile.backend` | production | `ghcr.io/alfa24/mbt_booking_agent-backend` |
| frontend | `Dockerfile.frontend` | - | `ghcr.io/alfa24/mbt_booking_agent-frontend` |
| bot | `Dockerfile` | - | `ghcr.io/alfa24/mbt_booking_agent-bot` |

### Файлы

1. **`.github/workflows/build-and-publish.yml`** — основной workflow
2. **`docker-compose.prod.yaml`** — compose файл для запуска из registry (без build, только image)

### Security

- Используется встроенный `GITHUB_TOKEN` (без дополнительных secrets)
- Permissions ограничены: `contents: read`, `packages: write`
- Нет хардкода секретов в файлах

### Production compose

`docker-compose.prod.yaml`:
- Использует образы из GHCR вместо build
- Сохраняет health checks и зависимости
- Не включает dev overrides (hot-reload volumes)
- Bot использует internal network (без adguard-vpn override)

## Шаги реализации

1. Создать `.github/workflows/build-and-publish.yml`
2. Создать `docker-compose.prod.yaml`
3. Обновить tasklist-devops.md
4. Создать summary.md

## Verification

- Workflow валидируется через GitHub Actions lint
- Compose файл проверяется через `docker compose -f docker-compose.prod.yaml config`
- Образы доступны в GHCR после push в main
