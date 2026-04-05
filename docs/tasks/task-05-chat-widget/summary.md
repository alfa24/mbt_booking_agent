# Summary: Глобальный чат (виджет)

## Реализовано

### 1. Chat Store (`src/store/chat.ts`)
- Zustand store с persist middleware
- Хранит `chatId` и `isOpen`
- Методы управления состоянием чата

### 2. Chat Hook (`src/hooks/use-chat.ts`)
- Интеграция с TanStack Query
- Создание чата через мутацию
- Infinite query для истории сообщений (cursor-based)
- Отправка сообщений с optimistic update
- Обработка ошибок с откатом состояния

### 3. Компоненты чата

#### chat-widget.tsx
- Плавающая кнопка с иконкой MessageCircle
- Создание чата при первом клике
- Открытие/закрытие Sheet

#### chat-window.tsx
- Sheet side="right" с заголовком "Ассистент"
- Интеграция MessageList и MessageInput
- Состояние загрузки

#### message-list.tsx
- ScrollArea с автопрокруткой
- Фильтрация system сообщений
- Рендер MessageBubble для каждого сообщения

#### message-bubble.tsx
- User сообщения: справа, bg-primary
- Assistant сообщения: слева, bg-muted
- Отображение времени (date-fns, ru locale)
- System сообщения: центрированные, стилизованные

#### message-input.tsx
- Textarea с автоматическим размером
- Enter для отправки, Shift+Enter для новой строки
- Кнопка Send с иконкой
- Валидация пустого сообщения (toast)

### 4. Интеграция
- ChatWidget добавлен в `src/app/(authenticated)/layout.tsx`
- Виден на всех authenticated страницах
- Рендерится после children

### 5. Зависимости
- Установлен shadcn компонент `avatar`
- `sheet` и `scroll-area` уже были установлены

## API Endpoints
- `POST /api/v1/chats` — создание чата
- `GET /api/v1/chats/{id}/messages` — история
- `POST /api/v1/chats/{id}/messages` — отправка

## Особенности реализации
- Optimistic updates для мгновенной обратной связи
- Автоприветствие от backend при создании чата
- Persist chatId в localStorage
- Полная типизация TypeScript
