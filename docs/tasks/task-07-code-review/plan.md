# Task 07: Ревью кода фронтенда

## Цели
- Проверить корректность реализации Next.js App Router, клиентских/серверных компонентов и TanStack Query.
- Оценить соответствие UI-компонентов shadcn/ui (семантика, layout, иконки).
- Проверить безопасность фронтенда (XSS, утечки env, LLM-ответы).
- Зафиксировать критические и некритические проблемы.

## Область ревью
- Каталог `web/src` (app, components, hooks, lib, store).
- Интеграция с backend API (особенно `/query/natural-language`).

## Шаги
1. Статический обзор структуры App Router и route-групп `(authenticated)`.
2. Анализ ключевых страниц: login, dashboard, чат, leaderboard.
3. Ревью хуков `use-*` (TanStack Query, работа с API и LLM).
4. Проверка UI-слоя: shadcn/ui компоненты, иконки, классы.
5. Проверка безопасности: env-переменные, отсутствие dangerous HTML, обработка данных LLM.
6. Запуск TypeScript/ESLint (по выводу ошибок) и классификация найденных проблем по severity.
7. Формирование отчёта в `summary.md` с рекомендациями.

## Definition of Done
- [x] План ревью сохранён в `docs/tasks/task-07-code-review/plan.md`.
- [x] Проведён обзор основных route и компонентов.
- [x] Выделены критические / warning / info проблемы.
- [x] Сформирован отчёт `summary.md`.
