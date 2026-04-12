# Onboarding нового участника

> **Цель:** Запустить систему и начать разработку за 15 минут  
> **Дата создания:** 12 апреля 2026

---

## 1. Клонирование и первичная настройка

### 1.1 Системные требования

| Зависимость | Версия | Проверка |
|-------------|--------|----------|
| Docker | 24+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Python | 3.12+ | `python3 --version` |
| Node.js | 20+ | `node --version` |
| Make | любая | `make --version` |
| uv | любая | `uv --version` (опционально) |

**Установка отсутствующих зависимостей:**
- Docker: https://docs.docker.com/get-docker/
- Node.js: https://nodejs.org/en/download/ (рекомендуется через nvm)
- uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 1.2 Клонирование репозитория

```bash
git clone <repository-url>
cd project
```

### 1.3 Настройка окружения

```bash
# Копирование шаблона переменных
cp .env.example .env
```

**Обязательные переменные для заполнения:**

| Переменная | Где взять | Описание |
|------------|-----------|----------|
| `TELEGRAM_BOT_TOKEN` | @BotFather в Telegram | Токен бота |
| `ROUTERAI_API_KEY` | https://routerai.ru | API ключ LLM |
| `BOT_USERNAME` | BotFather | Username бота (по умолчанию: mbt_house_booking_bot) |

📖 **Подробный гид по получению токенов:** [docs/how-to-get-tokens.md](how-to-get-tokens.md)

**Пример `.env`:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
BOT_USERNAME=my_test_bot
ROUTERAI_API_KEY=your_routerai_key
ROUTERAI_BASE_URL=https://routerai.ru/api/v1
LLM_MODEL=openrouter/qwen/qwen3-max-thinking

BACKEND_API_URL=http://backend:8000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DATABASE_URL=postgresql+asyncpg://booking:booking@localhost/booking

POSTGRES_USER=booking
POSTGRES_PASSWORD=booking
POSTGRES_DB=booking

# Для разработки с хоста (раскомментируйте и измените при необходимости)
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

⚠️ **Никогда не коммить `.env` в репозиторий!**

---

## 2. Настройка каждого компонента

### 2.1 Запуск базы данных

```bash
make postgres-up
```

**Проверка:**
```bash
docker compose ps postgres
# Должно показать статус "healthy"
```

### 2.2 Применение миграций

```bash
make migrate
```

**Ожидаемый вывод:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 2a84cf51810b, initial migration
INFO  [alembic.runtime.migration] Running upgrade 2a84cf51810b -> 8e3c7a9b2f1d, add indexes and constraints
...
```

### 2.3 Загрузка демо-данных (опционально)

```bash
make backend-fixtures
```

**Что загружается:**
- 3 тестовых дома
- Тарифы для каждого дома
- Тестовые пользователи
- Примеры бронирований

### 2.4 Запуск Backend

```bash
make run-backend
```

**Проверка:**
```bash
curl http://localhost:8001/api/v1/health
```

**Ожидаемый ответ:**
```json
{"status": "ok", "version": "0.1.0"}
```

**Swagger UI:** http://localhost:8001/docs

### 2.5 Запуск Frontend

```bash
make run-frontend
```

**Проверка:**
Откройте http://localhost:3000 в браузере

**Признаки успеха:**
- Загрузилась страница авторизации
- В консоли браузера нет ошибок (F12 → Console)
- Network requests к `localhost:8001/api/v1/*` возвращают 200

### 2.6 Запуск Telegram-бота

```bash
make run
```

> 💡 **Примечание:** `make run` запускает бота локально (не в Docker). 
> Для Docker-окружения используйте: `docker compose up -d bot`

**Проверка:**
1. Откройте Telegram
2. Найдите своего бота по username
3. Отправьте `/start`
4. Бот должен ответить приветственным сообщением

**Логи бота:**
```bash
# В том же терминале, где запущен бот
# Или запустите заново с DEBUG уровнем:
LOG_LEVEL=DEBUG make run
```

---

## 3. Проверка, что всё работает

### 3.1 Чеклист здоровья системы

| Проверка | Команда | Ожидаемый результат |
|----------|---------|---------------------|
| PostgreSQL запущен | `docker compose ps postgres` | Статус: `healthy` |
| Backend запущен | `curl http://localhost:8001/api/v1/health` | `{"status": "ok"}` |
| Frontend доступен | http://localhost:3000 | Загрузилась страница |
| Бот отвечает | Отправить `/start` в Telegram | Приветственное сообщение |
| API документация | http://localhost:8001/docs | Swagger UI открылся |

### 3.2 Интеграционный тест

```bash
# 1. Получить список домов
curl http://localhost:8001/api/v1/houses

# 2. Создать бронирование (если есть демо-данные)
curl -X POST http://localhost:8001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "house_id": 1,
    "tenant_id": 1,
    "check_in": "2024-06-01",
    "check_out": "2024-06-03",
    "guests": [{"tariff_id": 1, "count": 2}]
  }'

# 3. Проверить создание
curl http://localhost:8001/api/v1/bookings?tenant_id=1
```

---

## 4. Куда смотреть в первую очередь

### 4.1 Ключевые файлы и точки входа

| Компонент | Точка входа | Описание |
|-----------|-------------|----------|
| **Backend** | `backend/main.py` | FastAPI app, регистрация роутеров |
| | `backend/api/` | Все API endpoints |
| | `backend/services/` | Бизнес-логика |
| | `backend/models/` | SQLAlchemy модели |
| **Bot** | `bot/main.py` | Инициализация бота, регистрация хендлеров |
| | `bot/handlers/message.py` | Обработка сообщений |
| | `bot/services/backend_client.py` | HTTP клиент к backend |
| **Frontend** | `web/src/app/layout.tsx` | Корневой layout |
| | `web/src/app/page.tsx` | Страница авторизации |
| | `web/src/middleware.ts` | Аутентификация и роутинг по ролям |
| | `web/src/hooks/` | Custom hooks для работы с API |

### 4.2 Архитектурные документы

| Документ | Когда читать |
|----------|--------------|
| [docs/architecture.md](architecture.md) | **Начать отсюда** — общая схема системы |
| [docs/vision.md](vision.md) | Продуктовое видение и эволюция |
| [docs/data-model.md](data-model.md) | Структура базы данных |
| [docs/tech/api-contracts.md](tech/api-contracts.md) | Детали API endpoints |
| [docs/specs/screenflow.md](specs/screenflow.md) | UI экраны и переходы |
| [docs/specs/chatflow.md](specs/chatflow.md) | Сценарии чата с LLM |

### 4.3 Конвенции разработки

| Файл | Содержание |
|------|------------|
| `.qoder/rules/convensions.md` | Naming, API patterns, код-стайл |
| `.qoder/rules/workflow.md` | Процесс работы (итерации, задачи) |
| `.qoder/rules/common.md` | Общие правила (язык, лаконичность) |

---

## 5. Рабочий процесс

### 5.1 Итерационная разработка

Проект следует spec-driven development:

1. **Определить область работ** → tasklist в `docs/tasks/tasklist-*.md`
2. **Создать итерацию** → план в `docs/tasks/impl/<area>/iteration-N/<name>/plan.md`
3. **Декомпозировать на задачи** → `tasks/task-NN-<name>/plan.md`
4. **Реализовать** → код + тесты
5. **Зафиксировать результат** → `tasks/task-NN-<name>/summary.md`
6. **Завершить итерацию** → `iteration-N/<name>/summary.md`

### 5.2 Структура задач

```
docs/tasks/impl/<area>/iteration-N-<name>/
├── plan.md                 # План итерации
├── summary.md              # Результат итерации
└── tasks/
    ├── task-01-<name>/
    │   ├── plan.md         # План задачи
    │   └── summary.md      # Результат задачи
    └── task-02-<name>/
        ├── plan.md
        └── summary.md
```

### 5.3 Tasklist'ы

| Файл | Область |
|------|---------|
| `docs/tasks/tasklist-backend.md` | Backend API |
| `docs/tasks/tasklist-frontend.md` | Frontend web |
| `docs/tasks/tasklist-bot.md` | Telegram-бот |
| `docs/tasks/tasklist-database.md` | База данных |
| `docs/tasks/tasklist-integrations.md` | Интеграции |

### 5.4 Архитектурные решения (ADR)

При изменении архитектуры создавать ADR:

```bash
# Шаблон в docs/adr/README.md
# Пример: docs/adr/adr-004-frontend-framework.md
```

**Существующие ADR:**
- [ADR-001](adr/adr-001-database.md) — PostgreSQL
- [ADR-002](adr/adr-002-backend-framework.md) — FastAPI
- [ADR-003](adr/adr-adr-003-database-tools.md) — Alembic

---

## 6. Как готовить изменения

### 6.1 Проверки качества кода

**Backend:**
```bash
make lint-backend       # Ruff check
make format-backend     # Ruff format
make test-backend       # Pytest
make test-backend-cov   # Pytest с coverage
```

**Frontend:**
```bash
make lint-frontend      # ESLint
# Форматирование через Prettier (автоматически в ESLint)
```

**Bot:**
```bash
make lint               # Ruff check для всего проекта
make format             # Ruff format для всего проекта
```

### 6.2 CI/CD проверки

Перед созданием PR убедитесь:
- ✅ Все тесты проходят (`make test-backend`)
- ✅ Линтинг без ошибок (`make lint-backend`, `make lint-frontend`)
- ✅ Код отформатирован (`make format-backend`)
- ✅ Документация обновлена (если меняли API или архитектуру)

### 6.3 Git workflow

```bash
# 1. Создать ветку
git checkout -b feature/<название-фичи>

# 2. Внести изменения

# 3. Проверить качество
make lint-backend
make format-backend
make test-backend

# 4. Закоммитить
git add .
git commit -m "feat: <описание изменения>"

# 5. Запушить
git push origin feature/<название-фичи>
```

**Conventional Commits:**
- `feat:` — новая функциональность
- `fix:` — исправление бага
- `docs:` — документация
- `refactor:` — рефакторинг
- `test:` — тесты
- `chore:` — рутинные задачи

### 6.4 Работа с миграциями

```bash
# Создать новую миграцию
make migrate-create name="add_users_table"

# Применить все миграции
make migrate

# Откатить последнюю миграцию
make migrate-down
```

⚠️ **Важно:** Миграции запускаются только в Docker-контейнере!

---

## 7. Часто задаваемые вопросы

### Q: Backend не запускается, ошибка подключения к БД

**A:** Убедитесь, что PostgreSQL запущен:
```bash
docker compose ps postgres
```
Если статус не `healthy`, проверьте логи:
```bash
make postgres-logs
```

### Q: Frontend не подключается к backend

**A:** Проверьте `NEXT_PUBLIC_API_URL` в `.env`:
- Для Docker: `http://backend:8000/api/v1`
- Для разработки с хоста: `http://localhost:8001/api/v1`

### Q: Бот не отвечает на сообщения

**A:** Проверьте:
1. `TELEGRAM_BOT_TOKEN` в `.env` корректен
2. Backend запущен и доступен
3. Логи бота на наличие ошибок: `make run` (смотрите вывод)

### Q: Как запустить всё одной командой?

**A:**
```bash
make docker-build && make postgres-up && make migrate && make run-backend && make run-frontend
```

### Q: Где смотреть документацию API?

**A:** http://localhost:8001/docs (Swagger UI)

---

## 8. Полезные команды Makefile

| Команда | Описание |
|---------|----------|
| `make postgres-up` | Запуск PostgreSQL |
| `make migrate` | Применение миграций |
| `make backend-fixtures` | Загрузка демо-данных |
| `make run-backend` | Запуск backend |
| `make run-backend-logs` | Логи backend |
| `make run-frontend` | Запуск frontend |
| `make run` | Запуск бота |
| `make test-backend` | Запуск тестов backend |
| `make lint-backend` | Линтинг backend |
| `make format-backend` | Форматирование backend |
| `make lint-frontend` | Линтинг frontend |
| `make docker-build` | Пересборка всех сервисов |
| `make docker-restart` | Перезапуск всех сервисов |

Полный список: `Makefile` в корне проекта.

---

## 9. Следующие шаги

1. ✅ Прочитать [docs/architecture.md](architecture.md) — общая архитектура
2. ✅ Изучить [docs/vision.md](vision.md) — продуктовое видение
3. ✅ Посмотреть `backend/api/` — API endpoints
4. ✅ Запустить систему по этому гайду
5. ✅ Выбрать tasklist из `docs/tasks/` и начать работу

---

> **Есть вопросы?** Обращайтесь к команде или создавайте issue в репозитории.
