# План: Глобальный чат (виджет)

## Цель
Реализовать плавающий виджет чата с LLM-ассистентом, доступный на всех authenticated страницах.

## Архитектура

### State Management
- **Chat Store** (`src/store/chat.ts`): Zustand store с persist middleware
  - `chatId`: ID текущего чата (null если не создан)
  - `isOpen`: состояние открытия Sheet
  - Методы: `setChatId`, `setOpen`, `toggleOpen`

### Data Fetching
- **useChat Hook** (`src/hooks/use-chat.ts`): TanStack Query
  - `createChat`: мутация создания чата (POST /api/v1/chats)
  - `messages`: infinite query для истории (cursor-based)
  - `sendMessage`: мутация отправки с optimistic update

### UI Components

#### chat-widget.tsx
- Плавающая кнопка (fixed bottom-4 right-4)
- При клике: создание чата (если нет) → открытие Sheet
- Рендерит ChatWindow когда isOpen

#### chat-window.tsx
- Sheet side="right"
- Обязательный SheetTitle для accessibility
- Содержит MessageList и MessageInput

#### message-list.tsx
- ScrollArea с сообщениями
- Автопрокрутка к новым сообщениям (useEffect + ref)
- Фильтрация system сообщений

#### message-bubble.tsx
- User: справа, bg-primary
- Assistant: слева, bg-muted
- Время сообщения (date-fns format)

#### message-input.tsx
- Textarea + кнопка Send
- Enter для отправки, Shift+Enter для новой строки
- Disabled при отправке

## API Integration

### Endpoints
- `POST /api/v1/chats` — создание чата
- `GET /api/v1/chats/{id}/messages?cursor=&limit=50` — история
- `POST /api/v1/chats/{id}/messages` — отправка

### Optimistic Updates
- Сообщение пользователя добавляется сразу (temp id = Date.now())
- При успехе — инвалидация кэша для получения ответа LLM
- При ошибке — откат к предыдущему состоянию

## Конвенции
- Все компоненты — 'use client'
- `gap-*` вместо `space-y-*`
- Семантические цвета (bg-primary, bg-muted)
- `cn()` для условных классов
- `data-icon` на иконках в Button
- Sheet ВСЕГДА с SheetTitle

## Файлы для создания
1. `src/store/chat.ts`
2. `src/hooks/use-chat.ts`
3. `src/components/chat/chat-widget.tsx` (заменить)
4. `src/components/chat/chat-window.tsx` (новый)
5. `src/components/chat/message-list.tsx` (новый)
6. `src/components/chat/message-bubble.tsx` (новый)
7. `src/components/chat/message-input.tsx` (новый)
8. Обновить `src/app/(authenticated)/layout.tsx`
