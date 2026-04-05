# Summary: Чат в основной области

## Реализовано

### 1. Новые компоненты

#### `web/src/components/chat/chat-layout.tsx`
- Двухколоночный flex layout с `gap-4`
- Левая колонка: ConversationList (300px на desktop)
- Правая колонка: ConversationView (flex-1)
- Мобильная адаптация: переключение между списком и чатом через state
- Высота: `h-[calc(100vh-theme(spacing.16))]`

#### `web/src/components/chat/conversation-list.tsx`
- Список диалогов (пока один — "Ассистент")
- Элемент: Avatar с AvatarFallback (Bot иконка), имя, последнее сообщение (truncate), время
- Подсветка активного диалога (bg-accent)
- Поиск сверху (Input с placeholder "Поиск...") — для будущего расширения
- ScrollArea для списка

#### `web/src/components/chat/conversation-view.tsx`
- Шапка: Avatar с AvatarFallback (Bot иконка), имя "Ассистент", статус
- Группировка сообщений по дате с помощью date-fns
- Separator + Badge с датой между группами ("Сегодня", "Вчера", или дата)
- Кнопка "Назад" на мобильных (скрыта на desktop)
- Автопрокрутка к новым сообщениям (useEffect + ref.scrollIntoView)
- MessageInput внизу (переиспользован существующий)

### 2. Модифицированные компоненты

#### `web/src/app/(authenticated)/chat/page.tsx`
- Заменена заглушка на полноценную страницу
- 'use client' страница с ChatLayout
- При входе: если chatId нет — автоматически создаётся чат через createChat

#### `web/src/components/chat/message-input.tsx`
- Добавлена поддержка Ctrl+Enter для отправки (в дополнение к Enter без Shift)

### 3. Архитектура синхронизации

Виджет и полноэкранный чат используют:
- Общий store: `useChatStore` (chatId, isOpen)
- Общий hook: `useChat` (messages, sendMessage, createChat)
- Общие компоненты: MessageBubble, MessageInput

При входе на /chat:
- Если chatId есть в store → загружаются сообщения
- Если нет → создаётся новый чат (POST /chats)

### 4. Адаптивность

- Desktop (>=768px): двухколоночный layout, обе панели видны
- Mobile (<768px):
  - По умолчанию показывается ConversationList
  - При выборе диалога → показывается ConversationView
  - Кнопка "Назад" возвращает к списку

### 5. Конвенции соблюдены

- `gap-*` вместо `space-*`
- Семантические цвета: bg-primary, text-muted-foreground, bg-accent
- `cn()` для условных классов
- Avatar ВСЕГДА с AvatarFallback
- `truncate` для обрезки текста
- `data-icon` на иконках в Button
- Прямые импорты компонентов

### 6. Проверка

- `npm run lint` — ошибок нет
- Виджет продолжает работать (общие компоненты не сломаны)
