# План: Каркас frontend-проекта

## Цель
Создать базовый каркас frontend-приложения на Next.js с настроенной архитектурой, аутентификацией и UI компонентами.

## Задачи

### 1. Инициализация проекта
- Создать Next.js проект с TypeScript и Tailwind CSS
- Настроить shadcn/ui компоненты
- Установить необходимые зависимости

### 2. Структура проекта
```
web/src/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Login page
│   ├── loading.tsx         # Root loading
│   ├── error.tsx           # Root error boundary
│   ├── not-found.tsx       # 404 page
│   ├── providers.tsx       # QueryClient + Toaster
│   └── (authenticated)/    # Защищенные маршруты
│       ├── layout.tsx      # Auth layout с проверкой
│       ├── dashboard/
│       ├── leaderboard/
│       └── chat/
├── components/
│   ├── ui/                 # shadcn/ui компоненты
│   ├── layout/             # Layout компоненты
│   └── chat/               # Chat widget
├── lib/
│   ├── api.ts              # API client (ky)
│   └── utils.ts            # Утилиты (cn)
└── store/
    └── auth.ts             # Zustand auth store
```

### 3. Реализация компонентов
- **UI**: Button, Input, Label, Card, Skeleton
- **Layout**: Sidebar, Header, AppShell
- **Chat**: ChatWidget (плавающая кнопка)

### 4. Аутентификация
- Login page с формой Telegram username
- Zustand store с persist middleware
- Проверка auth в (authenticated)/layout
- Редирект при отсутствии авторизации

### 5. Тема
- Travel/nature цветовая палитра
- Зелёный primary (hsl 142)
- Песочный accent (hsl 42)
- Только светлая тема

### 6. Docker и Make
- Dockerfile.frontend (multi-stage)
- docker-compose.yaml: сервис web
- docker-compose.override.yml: dev mode
- Makefile: команды для frontend

## Артефакты
- Работающий login flow
- Навигация между страницами
- Защищенные маршруты
- Docker-контейнеризация
