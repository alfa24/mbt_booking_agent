# Summary: Каркас frontend-проекта

## Реализовано

### Проектная структура
```
web/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout (Server Component)
│   │   ├── page.tsx                # Login page (Client Component)
│   │   ├── loading.tsx             # Root loading skeleton
│   │   ├── error.tsx               # Root error boundary
│   │   ├── not-found.tsx           # 404 page
│   │   ├── providers.tsx           # QueryClientProvider + Toaster
│   │   └── (authenticated)/
│   │       ├── layout.tsx          # Auth check + AppShell
│   │       ├── dashboard/          # Page + loading + error
│   │       ├── leaderboard/        # Page + loading + error
│   │       └── chat/               # Page + loading + error
│   ├── components/
│   │   ├── ui/                     # Button, Input, Label, Card, Skeleton
│   │   ├── layout/                 # Sidebar, Header, AppShell
│   │   └── chat/                   # ChatWidget
│   ├── lib/
│   │   ├── api.ts                  # ky client + getUserByTelegramId
│   │   └── utils.ts                # cn() утилита
│   └── store/
│       └── auth.ts                 # Zustand auth store с persist
├── package.json
├── next.config.ts                  # standalone output
├── tsconfig.json
├── postcss.config.mjs
├── eslint.config.mjs
└── next-env.d.ts
```

### Функциональность
1. **Login flow**: Ввод Telegram username → API запрос → сохранение в store → redirect
2. **Auth guard**: Проверка isAuthenticated в (authenticated)/layout
3. **Навигация**: Sidebar с подсветкой активного пункта
4. **Toast notifications**: sonner для ошибок и успехов
5. **Loading states**: Skeleton для всех страниц
6. **Error boundaries**: Обработка ошибок на уровне страниц

### Тема (globals.css)
- Primary: зелёный (hsl 142 70% 35%)
- Accent: песочный (hsl 42 60% 55%)
- Семантические CSS переменные для shadcn/ui

### Docker
- **Dockerfile.frontend**: multi-stage (deps → builder → runner)
- **docker-compose.yaml**: production сервис web
- **docker-compose.override.yml**: dev mode с hot reload
- **Makefile**: install-frontend, run-frontend, build-frontend, lint-frontend

### Зависимости
- next, react, react-dom, typescript
- tailwindcss, @tailwindcss/postcss
- zustand (с persist middleware)
- @tanstack/react-query
- ky (HTTP client)
- lucide-react (иконки)
- sonner (toast notifications)
- date-fns, recharts (для будущего использования)

## Проверка
```bash
# Установка зависимостей
cd web && npm install

# Линтинг
npm run lint

# Сборка
npm run build

# Запуск в Docker
make run-frontend
```

## Следующие шаги
- Реализация Dashboard страницы
- Интеграция с backend API
- Реализация Chat функциональности
