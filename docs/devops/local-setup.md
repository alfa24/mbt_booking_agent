# Локальный запуск проекта

> Полное руководство по запуску проекта в локальном окружении с использованием Docker.

## 📋 Предварительные требования

- **Docker** 24+ (с Docker Compose v2)
- **Make** 4.0+
- **Git** 2.0+

## 🏗️ Архитектура контейнеров

Проект состоит из 4 основных сервисов:

```
┌─────────────────────────────────────────┐
│          Backend Network                │
│                                         │
│  ┌──────────┐    ┌──────────────────┐   │
│  │ Postgres │◄──►│    Backend       │   │
│  │  :5432   │    │    :8000         │   │
│  └──────────┘    └────────┬─────────┘   │
│                           │              │
│                    ┌──────▼──────────┐   │
│                    │      Web        │   │
│                    │    :3000        │   │
│                    └─────────────────┘   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         AdGuard VPN Network             │
│                                         │
│  ┌──────────────────┐                   │
│  │       Bot        │                   │
│  │  (Telegram API)  │                   │
│  └──────────────────┘                   │
└─────────────────────────────────────────┘
```

### Сервисы

| Сервис | Порт (host) | Описание |
|--------|-------------|----------|
| **PostgreSQL** | Не проброшен | База данных (внутренняя сеть) |
| **Backend** | 8001 | FastAPI API сервер |
| **Web** | 3000 | Next.js фронтенд |
| **Bot** | Нет | Telegram бот (через adguard-vpn) |

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонировать репозиторий
git clone <repo-url>
cd project

# Создать .env файл из примера
cp .env.example .env

# Отредактировать .env (указать токены, ключи API и т.д.)
nano .env
```

### 2. Запуск инфраструктуры

```bash
# Запустить PostgreSQL
make postgres-up

# Применить миграции базы данных
make migrate
```

### 3. Запуск приложения

```bash
# Собрать и запустить все сервисы
make docker-run

# Или запустить в фоне
make docker-run &
```

### 4. Проверка работоспособности

```bash
# Проверить статус сервисов
make docker-status

# Проверить health сервисов
make docker-health

# Посмотреть логи
make docker-logs
```

## 🛠️ Основные команды

### Управление сервисами

```bash
# Запустить все сервисы
make docker-run

# Остановить все сервисы
make docker-down

# Перезапустить с пересборкой
make docker-restart

# Проверить статус
make docker-status

# Посмотреть логи
make docker-logs
```

### Backend

```bash
# Запустить backend
make run-backend

# Остановить backend
make stop-backend

# Посмотреть логи
make run-backend-logs

# Запустить тесты
make test-backend

# Запустить тесты с покрытием
make test-backend-cov

# Линтинг
make lint-backend

# Форматирование
make format-backend

# Загрузить фикстуры
make backend-fixtures
```

### Frontend

```bash
# Установить зависимости
make install-frontend

# Запустить dev-сервер
make run-frontend

# Собрать production
make build-frontend

# Линтинг
make lint-frontend
```

### Bot

```bash
# Запустить бота
make run-bot

# Остановить бота
make stop-bot

# Посмотреть логи
make logs-bot
```

### База данных

```bash
# Применить миграции
make migrate

# Создать новую миграцию
make migrate-create name="add_users_table"

# Откатить последнюю миграцию
make migrate-down

# Запустить PostgreSQL
make postgres-up

# Посмотреть логи PostgreSQL
make postgres-logs
```

## ⚙️ Конфигурация

### Docker Compose архитектура

Проект использует двухфайловую конфигурацию:

- **docker-compose.yaml** — базовая конфигурация сервисов (production-ready)
- **docker-compose.override.yml** — локальные настройки разработки

Override файл автоматически подключается через Makefile паттерн:

```makefile
BASE_OVERRIDE = $(shell test -f docker-compose.override.yml && echo '-f docker-compose.override.yml')
```

### Отличия base vs override

| Настройка | Base (docker-compose.yaml) | Override (docker-compose.override.yml) |
|-----------|---------------------------|----------------------------------------|
| **Backend target** | `production` | `dev` (с dev зависимостями) |
| **Backend volumes** | Нет | Hot-reload volumes |
| **Backend ports** | Не проброшены | 8001:8000 |
| **Web command** | `node server.js` | `npm run dev` |
| **Web volumes** | Нет | `./web/src:/app/src` |
| **Web ports** | Не проброшены | 3000:3000 |
| **Bot network** | `backend-network` | `container:adguard-vpn` |
| **Bot backend URL** | `http://backend:8000` | `http://172.17.0.1:8001` |

### Переменные окружения

Ключевые переменные в `.env`:

```bash
# Bot
BOT_TOKEN=your_telegram_bot_token
BOT_BACKEND_URL=http://backend:8000/api/v1  # Override изменит на http://172.17.0.1:8001/api/v1

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DATABASE_URL=postgresql+asyncpg://booking:booking@postgres/booking
BACKEND_LOG_LEVEL=INFO

# Web
NEXT_PUBLIC_API_URL=http://backend:8000/api/v1  # Override изменит на http://localhost:8001/api/v1
```

## 🔧 Разработка

### Hot-reload настройка

Override файл настраивает hot-reload для backend и frontend:

**Backend:**
```yaml
volumes:
  - ./backend:/app/backend:ro
  - ./alembic:/app/alembic:ro
  - ./alembic.ini:/app/alembic.ini:ro
```

**Frontend:**
```yaml
volumes:
  - ./web/src:/app/src
  - ./web/public:/app/public
  - /app/node_modules  # Anonymous volume для node_modules
```

### Запуск без override

Для тестирования production конфигурации локально:

```bash
# Временно переименовать override файл
mv docker-compose.override.yml docker-compose.override.yml.bak

# Запустить
make docker-run

# Вернуть override файл
mv docker-compose.override.yml.bak docker-compose.override.yml
```

## 🐛 Диагностика

### Проверка health сервисов

```bash
# Подробный статус
docker compose ps

# Проверить health конкретного сервиса
docker inspect --format='{{.State.Health.Status}}' project-backend-1
```

### Частые проблемы

#### 1. Bot не может достучаться до backend

**Симптом:** Bot не отвечает на команды

**Решение:**
- Проверить, что backend запущен на порту 8001
- Убедиться, что adguard-vpn контейнер запущен
- Проверить `BOT_BACKEND_URL` в .env

```bash
# Проверить backend
curl http://localhost:8001/api/v1/health

# Проверить adguard-vpn
docker ps | grep adguard-vpn
```

#### 2. Frontend не видит backend

**Симптом:** Ошибки CORS или network errors в браузере

**Решение:**
- Проверить `NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1`
- Убедиться, что backend запущен на порту 8001

#### 3. Миграции не применяются

**Симптом:** Ошибки базы данных при запуске

**Решение:**
```bash
# Остановить всё
make docker-down

# Запустить только PostgreSQL
make postgres-up

# Применить миграции
make migrate

# Запустить всё
make docker-run
```

#### 4. Проблемы с permissions

**Симптом:** Permission denied при записи файлов

**Решение:**
```bash
# Исправить ownership
sudo chown -R $USER:$USER .

# Пересобрать образы
make docker-restart
```

## 🧹 Очистка

### Остановка и удаление контейнеров

```bash
# Остановить сервисы
make docker-down

# Остановить и удалить volumes
docker compose down -v

# Удалить все образы
docker compose down --rmi all
```

### Полная очистка

```bash
# Удалить контейнеры, volumes, образы
docker compose down -v --rmi all --remove-orphans

# Очистить Docker cache
docker system prune -af
```

## 📝 Примечания

### Network режим bot

Bot использует `network_mode: container:adguard-vpn` для доступа к Telegram API через VPN. Это означает:
- Bot работает в сетевом стеке контейнера adguard-vpn
- Bot не может обращаться к другим сервисам по имени (backend, postgres)
- Bot использует IP хоста `172.17.0.1` для доступа к backend

### Production deployment

Для production:
1. Удалить или переименовать `docker-compose.override.yml`
2. Использовать `make docker-run` (запустит только base конфигурацию)
3. Настроить external network для bot или убрать VPN requirement

### Multi-stage builds

Все Dockerfiles используют multi-stage builds:
- **Backend:** `production` и `dev` targets
- **Frontend:** `deps`, `builder`, `runner` stages
- **Bot:** Single stage (будет оптимизирован в будущих итерациях)

## 🔗 Ссылки

- [ADR-002: Backend Framework](../adr/adr-002-backend-framework.md)
- [API Contracts](../tech/api-contracts.md)
- [Onboarding Guide](../onboarding.md)
- [Architecture Overview](../architecture.md)
