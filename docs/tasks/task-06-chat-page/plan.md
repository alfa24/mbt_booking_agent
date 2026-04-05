# План: Чат в основной области

## Цель
Создать полноэкранную страницу чата с двухколоночным layout (список диалогов + область сообщений), синхронизированную с виджетом через общий store.

## Состав работ

### 1. Новые компоненты

#### `chat-layout.tsx`
- Двухколоночный flex layout с `gap-4`
- Левая колонка: ConversationList (~300px на desktop)
- Правая колонка: ConversationView (flex-1)
- Мобильная адаптация: переключение между списком и чатом через state
- Высота: `h-[calc(100vh-theme(spacing.16))]`

#### `conversation-list.tsx`
- Список диалогов (пока один — "Ассистент")
- Элемент: Avatar + имя + последнее сообщение (truncate) + время
- Подсветка активного (bg-accent)
- Поиск сверху (Input, пока без логики)
- ScrollArea для списка

#### `conversation-view.tsx`
- Шапка: аватар + "Ассистент"
- ScrollArea с сообщениями + группировка по дате (Separator + Badge)
- MessageInput внизу (переиспользуем существующий)
- Автопрокрутка к новым сообщениям

### 2. Модификации существующих компонентов

#### `message-input.tsx`
- Добавить поддержку Ctrl+Enter для отправки
- Сохранить Enter (без Shift) для отправки

#### `message-list.tsx`
- Добавить опциональную группировку по дате через проп `groupByDate`
- Использовать date-fns для форматирования дат

### 3. Страница чата

#### `chat/page.tsx`
- 'use client' страница
- Использует ChatLayout
- При входе: если chatId есть — загрузить сообщения, если нет — создать чат

### 4. Архитектура

```
┌─────────────────────────────────────────────┐
│              chat/page.tsx                   │
│  (инициализация чата, использует ChatLayout) │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              ChatLayout                      │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │Conversation  │  │   ConversationView   │ │
│  │    List      │  │                      │ │
│  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 5. Зависимости

- date-fns (уже установлен)
- Существующие компоненты: MessageList, MessageBubble, MessageInput
- Существующие hooks: useChat
- Существующие stores: useChatStore, useAuthStore

## Файлы для создания/изменения

### Создать:
- `web/src/components/chat/chat-layout.tsx`
- `web/src/components/chat/conversation-list.tsx`
- `web/src/components/chat/conversation-view.tsx`

### Изменить:
- `web/src/components/chat/message-input.tsx` — добавить Ctrl+Enter
- `web/src/components/chat/message-list.tsx` — добавить группировку по дате
- `web/src/app/(authenticated)/chat/page.tsx` — заменить заглушку

## Конвенции
- `gap-*` вместо `space-*`
- Семантические цвета: bg-primary, text-muted-foreground, bg-accent
- `cn()` для условных классов
- Avatar ВСЕГДА с AvatarFallback
- `truncate` для обрезки текста
- `data-icon` на иконках в Button
