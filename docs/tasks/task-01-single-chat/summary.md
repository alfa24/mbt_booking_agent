# Task: Упрощение чата до одного диалога — Summary

## Выполнено

### 1. Упрощён `chat-layout.tsx`
- Убран sidebar с `ConversationList`
- Убран `useState` для переключения между видами
- Осталась одна колонка с `ConversationView` на всю ширину

### 2. Упрощён `chat/page.tsx`
- Убран заголовок "Чат с ассистентом"
- Убраны лишние обёртки
- Рендерится только `<ChatLayout />`

### 3. Упрощён `conversation-view.tsx`
- Убраны props `onBack` и `showBackButton`
- Убрана кнопка возврата (ArrowLeft)
- Убран неиспользуемый импорт `Button`

### 4. Удалён `conversation-list.tsx`
- Файл больше не нужен

## Сохранено

- `MessageInput` с voice input и data query mode
- `MessageList`, `MessageBubble`
- `VoiceInput`, `VoiceOutput`
- `DataQueryMode`, `QueryResultsTable`
- `useChat`, `useDataQuery`, `chat store` — не менялись

## Результат

Страница `/chat` теперь — один полноэкранный диалог с ассистентом без sidebar и переключения между диалогами.
