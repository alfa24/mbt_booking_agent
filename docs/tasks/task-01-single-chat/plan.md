# Task: Упрощение чата до одного диалога

## Цель

Убрать multi-conversation из чата, оставив единственный диалог без боковой панели.

## Текущее состояние

- Страница `/chat` использует `ChatLayout` с sidebar (`ConversationList`) и main area (`ConversationView`)
- `ConversationList` — список диалогов с возможностью переключения (но реально один диалог)
- `useChat` уже работает с одним `chatId` (хранится в Zustand store)
- Backend уже возвращает существующий чат при POST `/chats` для того же пользователя

## План реализации

### 1. Упростить `chat-layout.tsx`

**Было:** Две колонки — sidebar + ConversationView с переключением visible на мобильных.

**Станет:** Одна колонка — ConversationView на всю ширину.

Убрать:
- `useState` для `showConversationView`
- Рендер `ConversationList`
- Логику переключения visible/hidden

### 2. Упростить `chat/page.tsx`

**Было:** Заголовок + ChatLayout.

**Станет:** ConversationView на весь экран без лишних обёрток.

Убрать:
- Заголовок "Чат с ассистентом"
- Лишние обёртки

### 3. Удалить `conversation-list.tsx`

Файл больше не нужен.

### 4. Обновить `ConversationView`

Убрать `onBack` и `showBackButton` props — они были для возврата к списку диалогов на мобильных.

## Сохраняемое

- `MessageInput` (включая voice input и data query mode)
- `MessageList`, `MessageBubble`
- `VoiceInput`, `VoiceOutput`
- `DataQueryMode`, `QueryResultsTable`
- `useChat`, `useDataQuery`, `chat store` — уже упрощены

## Файлы

| Файл | Действие |
|------|----------|
| `web/src/components/chat/chat-layout.tsx` | Упростить |
| `web/src/app/(authenticated)/chat/page.tsx` | Упростить |
| `web/src/components/chat/conversation-view.tsx` | Упростить props |
| `web/src/components/chat/conversation-list.tsx` | Удалить |

## Результат

Страница чата — один полноэкранный диалог с ассистентом.
