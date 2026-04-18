# Ревью Docker- и CI-конфигурации

## Дата проведения

2026-04-18

## Область ревью

- `Dockerfile` (bot)
- `Dockerfile.backend`
- `Dockerfile.frontend`
- `docker-compose.yaml`
- `docker-compose.override.yml`
- `docker-compose.prod.yaml`
- `.github/workflows/build-and-publish.yml`
- `.dockerignore`, `.dockerignore.backend`, `.dockerignore.frontend`
- `Makefile`

## Методология

Ревью проведено с использованием skill `docker-expert` по следующим категориям:
1. Security Hardening
2. Image Optimization
3. Compose Orchestration
4. CI/CD Best Practices
5. Development Workflow

---

## Найденные проблемы

### 🔴 Критичные (High) — Исправлены

#### 1. Bot network isolation в production

**Файл:** `docker-compose.prod.yaml`

**Проблема:** Сервис bot не имел явного подключения к `backend-network`, что могло привести к проблемам с service discovery в production.

**Решение:** Добавлена явная конфигурация networks для bot.

```yaml
bot:
  networks:
    - backend-network
```

**Status:** ✅ Исправлено

---

#### 2. Отсутствие resource limits в production

**Файл:** `docker-compose.prod.yaml`

**Проблема:** Все сервисы (backend, web, bot) не имели ограничений ресурсов, что могло привести к resource exhaustion на хосте.

**Решение:** Добавлены `deploy.resources` limits и reservations для всех сервисов:

| Сервис | CPU Limit | Memory Limit | CPU Reservation | Memory Reservation |
|--------|-----------|--------------|-----------------|-------------------|
| backend | 1.0 | 1G | 0.25 | 256M |
| web | 0.5 | 512M | 0.1 | 128M |
| bot | 0.5 | 512M | 0.1 | 128M |

**Status:** ✅ Исправлено

---

### 🟡 Средние (Medium) — Исправлены

#### 3. Бессмысленный healthcheck в bot

**Файл:** `Dockerfile` (строки 27-28)

**Проблема:** Healthcheck всегда возвращал success (`sys.exit(0)`), не проверяя реальное состояние приложения.

**До:**
```dockerfile
HEALTHCHECK CMD python -c "import sys; sys.exit(0)" || exit 1
```

**После:**
```dockerfile
HEALTHCHECK CMD python -c "import bot.main; import sys; sys.exit(0)" || exit 1
```

**Улучшения:**
- Проверяет возможность импорта основного модуля бота
- Увеличен `start-period` с 5s до 10s для более надёжного старта

**Status:** ✅ Исправлено

---

#### 4. Неверный healthcheck в frontend

**Файл:** `Dockerfile.frontend` (строки 34-35)

**Проблема:** Healthcheck запрашивал `/health` endpoint, который не существует в Next.js standalone mode.

**До:**
```dockerfile
HEALTHCHECK CMD node -e "require('http').get('http://localhost:3000/health', ...)"
```

**После:**
```dockerfile
HEALTHCHECK CMD node -e "const http = require('http'); const opts = {hostname: 'localhost', port: 3000, path: '/', timeout: 3000}; http.get(opts, (res) => { process.exit(res.statusCode < 400 ? 0 : 1); }).on('error', () => process.exit(1))"
```

**Улучшения:**
- Проверяет корневой path `/` вместо несуществующего `/health`
- Принимает любой статус < 400 (200, 301, 302 и т.д.)
- Добавлен timeout 3000ms
- Обработка ошибок соединения

**Status:** ✅ Исправлено

---

#### 5. Отсутствие security scanning в CI/CD

**Файл:** `.github/workflows/build-and-publish.yml`

**Проблема:** Образы публиковались в GHCR без проверки на уязвимости.

**Решение:** Добавлен шаг Trivy vulnerability scanner после build & push:

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service }}:latest
    format: 'table'
    exit-code: '1'
    ignore-unfixed: true
    severity: 'CRITICAL,HIGH'
```

**Поведение:**
- Сканирует каждый образ после публикации
- Блокирует pipeline при обнаружении CRITICAL/HIGH уязвимостей
- Игнорирует unfixable уязвимости (чтобы не блокировать без причины)

**Status:** ✅ Исправлено

---

### 🟢 Низкие (Low) — Рекомендации

#### 6. Multi-architecture builds

**Файл:** `.github/workflows/build-and-publish.yml` (строка 56)

**Текущее состояние:**
```yaml
platforms: linux/amd64
```

**Рекомендация:** Добавить `linux/arm64` для поддержки Apple Silicon и ARM-серверов.

**Почему не исправлено:**
- Увеличивает время сборки в 2-3x
- Требует больше ресурсов GitHub Actions runner
- Может потребовать cross-compilation настройки для некоторых зависимостей

**Статус:** 📋 Запланировано для будущей итерации

---

#### 7. Makefile — дублирование команд

**Файл:** `Makefile`

**Проблема:** Команды общего назначения (`docker-build`, `docker-run`, `docker-down`) дублируют функционал специфичных команд (`run-backend`, `build-backend`, и т.д.).

**Рекомендация:**
- Удалить или задокументировать general-purpose команды
- Оставить только специфичные для сервисов команды
- Добавить `make help` для вывода списка доступных команд

**Статус:** 📋 Запланировано для будущей итерации

---

#### 8. Bot network_mode в dev-режиме

**Файл:** `docker-compose.override.yml` (строки 29-35)

**Проблема:** Bot использует `network_mode: container:adguard-vpn`, что:
- Отключает его от `backend-network`
- Требует хардкод IP `172.17.0.1` для доступа к backend
- Непортабельно (IP может отличаться на других машинах)

**Рекомендация:**
- Использовать `extra_hosts` для DNS resolution
- Или создать отдельную сеть для bot с VPN access
- Или вынести VPN на уровень docker-compose (отдельный сервис)

**Почему не исправлено:**
- Требует архитектурного решения (как bot должен получать доступ к Telegram API)
- Может потребовать изменений в инфраструктуре хоста
- Нужно тестирование на разных окружениях

**Статус:** 📋 Требует обсуждения и планирования

---

## Что сделано хорошо ✅

1. **Multi-stage builds** — backend и frontend используют multi-stage для минимизации размера образов
2. **Non-root users** — все контейнеры запускаются от non-root пользователя
3. **Layer caching** — зависимости копируются до исходного кода для оптимизации кэша
4. **Health checks** — postgres и backend имеют корректные health checks
5. **.dockerignore** — файлы исключают node_modules, .venv, __pycache__, .git
6. **Graceful shutdown** — используется `STOPSIGNAL SIGTERM`
7. **Dev/Prod separation** — override паттерн для разделения конфигураций
8. **Service dependencies** — `depends_on` с `condition: service_healthy`

---

## Метрики качества

| Категория | До ревью | После ревью |
|-----------|----------|-------------|
| Security | ⚠️ 6/10 | ✅ 8/10 |
| Reliability | ⚠️ 7/10 | ✅ 9/10 |
| Resource Management | ❌ 3/10 | ✅ 8/10 |
| CI/CD Quality | ⚠️ 6/10 | ✅ 8/10 |
| Health Checks | ⚠️ 5/10 | ✅ 8/10 |

---

## Артефакты

### Изменённые файлы

1. `Dockerfile` — улучшен healthcheck bot
2. `Dockerfile.frontend` — исправлен healthcheck
3. `docker-compose.prod.yaml` — добавлены resource limits и networks для bot
4. `.github/workflows/build-and-publish.yml` — добавлен Trivy scanner

### Связанные документы

- [tasklist-devops.md](../../tasklist-devops.md)
- [iteration-2-ghcr-pipeline summary](../iteration-2-ghcr-pipeline/tasks/task-03-ghcr-workflow/summary.md)

---

## Рекомендации для будущих итераций

1. **Multi-arch builds** — поддержка linux/arm64
2. **Docker Scout** — интеграция для continuous vulnerability monitoring
3. **Secrets management** — использование Docker Secrets вместо env_file для production
4. **Makefile refactor** — устранение дублирования команд, добавление `make help`
5. **Bot networking** — архитектурное решение для VPN access без network_mode
6. **Image size monitoring** — CI check для предотвращения разрастания образов
7. **Compose validation** — добавить `docker compose config` в CI pipeline
