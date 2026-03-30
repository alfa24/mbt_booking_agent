# План: Задача 01 — Выбор backend-стека и ADR

## Цель

Определить технологический стек backend и зафиксировать архитектурное решение в ADR.

## Контекст

Изучены:
- [docs/vision.md](../../vision.md) — архитектура системы, backend-first подход
- [docs/plan.md](../../plan.md) — этап 1: Backend API и база данных
- [docs/data-model.md](../../data-model.md) — сущности: User, House, Booking, Tariff, ConsumableNote, StayRecord
- [docs/adr/adr-001-database.md](../../adr/adr-001-database.md) — выбрана PostgreSQL
- [bot/config.py](../../../bot/config.py) — текущая конфигурация на Pydantic
- [bot/main.py](../../../bot/main.py) — текущая структура бота на aiogram

## Анализ вариантов

### Критерии выбора

| Критерий | Вес | Пояснение |
|----------|-----|-----------|
| Скорость разработки API | Высокий | Нужен быстрый REST API для MVP |
| Async поддержка | Высокий | Интеграция с LLM, Telegram — всё async |
| Pydantic интеграция | Высокий | Уже используется в боте, единый подход |
| Простота обучения | Средний | Команда знакома с Python |
| Экосистема | Средний | Готовые решения для PostgreSQL, миграций |

### Варианты

**1. FastAPI**
- Плюсы: нативный Pydantic, async из коробки, автоматическая OpenAPI документация, SQLAlchemy 2.0 async
- Минусы: меньше "батареек" чем Django, нет встроенной админки

**2. Django + DRF**
- Плюсы: много готового, встроенная админка, mature ecosystem
- Минусы: sync по умолчанию, тяжеловат для API-only, избыточен для MVP

**3. Flask**
- Плюсы: минималистичный, гибкий
- Минусы: требует больше ручной настройки, менее современный

**Рекомендация: FastAPI** — лучше всего подходит для API-first подхода, async интеграций и единого стека с ботом (Pydantic).

## Состав работ

### 1. Сравнение фреймворков (исследование)
- [x] Формализовать критерии выбора
- [x] Задокументировать сравнение FastAPI vs Django vs Flask
- [x] Определить выбор с обоснованием

### 2. Выбор ORM
- [x] SQLAlchemy 2.0 (async) — рекомендуется для FastAPI
- [x] Alembic для миграций

### 3. Создание ADR-002
- [x] Создать файл `docs/adr/adr-002-backend-framework.md`
- [x] Статус: Proposed -> Accepted
- [x] Контекст: требования к backend из vision.md
- [x] Рассмотренные варианты с плюсами/минусами
- [x] Решение: FastAPI + SQLAlchemy 2.0 + Alembic
- [x] Последствия: структура проекта, зависимости

### 4. Обновление conventions.md
- [x] Добавить раздел "Backend" в `.qoder/rules/conventions.md`
- [x] Описать структуру директорий `backend/`
- [x] Определить паттерны: dependency injection, repository pattern
- [x] Naming conventions для routes, schemas, models

### 5. Обновление docs/adr/README.md
- [x] Добавить ссылку на ADR-002

## Артефакты

| Файл | Описание |
|------|----------|
| `docs/adr/adr-002-backend-framework.md` | Архитектурное решение по выбору стека |
| `.qoder/rules/conventions.md` | Обновлённые соглашения с разделом о backend |
| `docs/adr/README.md` | Реестр ADR с ссылкой на ADR-002 |

## Definition of Done

- [x] ADR создан и содержит обоснование выбора
- [x] Все внешние зависимости зафиксированы с версиями (FastAPI 0.110+, SQLAlchemy 2.0+, Alembic)
- [x] Conventions обновлены — структура backend, паттерны, naming

## Self-check

| Пункт DoD | Статус | Проверка |
|-----------|--------|----------|
| ADR создан и содержит обоснование выбора | ✅ | `docs/adr/adr-002-backend-framework.md` — статус Accepted, сравнение FastAPI/Django/Flask, обоснование выбора |
| Все внешние зависимости зафиксированы с версиями | ✅ | FastAPI ^0.110.0, SQLAlchemy ^2.0.0, Alembic ^1.13.0, Pydantic ^2.5.0, asyncpg ^0.29.0 |
| Conventions обновлены — структура backend, паттерны, naming | ✅ | `.qoder/rules/conventions.md` — раздел "## Backend" с деревом директорий, паттернами, naming conventions, API conventions |

**Дополнительно:**
- ADR-002 зарегистрирован в `docs/adr/README.md`
- Структура backend/ описана с модулями: api/, schemas/, models/, services/
- Naming conventions включают паттерны для роутеров, схем, моделей, сервисов

## Документы задачи

Согласно workflow.md, для задачи создаются:

| Документ | Путь | Назначение |
|----------|------|------------|
| План | `docs/tasks/task-01-stack-adr/plan.md` | Как задача будет реализована (этот документ) |
| Summary | `docs/tasks/task-01-stack-adr/summary.md` | Что реализовано по факту (создаётся после выполнения) |

## Проверка

```bash
# Проверка ADR
cat docs/adr/adr-002-backend-framework.md

# Проверка conventions
cat .qoder/rules/conventions.md | grep -A 20 "Backend"

# Проверка реестра ADR
cat docs/adr/README.md
```

## Зависимости

- Блокирует: Задачу 02 (генерация каркаса проекта)
- Зависит от: ADR-001 (выбор PostgreSQL уже принят)

## Оценка времени

~2-3 часа на исследование и документирование.
