# Task 08: Реализация голосового режима чата

## Цель
Добавить голосовой ввод и вывод в чат-виджет и чат-страницу с использованием Web Speech API.

## Состав работ

### 1. Hooks
- `use-speech-recognition.ts` — распознавание речи (ru-RU)
- `use-speech-synthesis.ts` — синтез речи (русский голос)

### 2. Компоненты
- `voice-input.tsx` — кнопка микрофона с индикатором прослушивания
- `voice-output.tsx` — кнопка прослушивания сообщения

### 3. Интеграция
- `message-input.tsx` — добавить кнопку микрофона
- `message-bubble.tsx` — добавить кнопку TTS для сообщений бота
- `chat-window.tsx` — минималистичная версия voice input

### 4. Feature detection
- Проверка `window.SpeechRecognition` / `webkitSpeechRecognition`
- Graceful degradation — скрытие кнопок если API недоступен

## Технические детали

### Web Speech API
- SpeechRecognition для распознавания
- SpeechSynthesis для озвучивания
- Язык: ru-RU
- Обработка промежуточных результатов

### UI
- Использование lucide-react (Mic, MicOff, Volume2, VolumeX)
- Анимация при прослушивании
- Семантические цвета shadcn/ui

## Файлы для создания/изменения

### Новые файлы
- `web/src/hooks/use-speech-recognition.ts`
- `web/src/hooks/use-speech-synthesis.ts`
- `web/src/components/chat/voice-input.tsx`
- `web/src/components/chat/voice-output.tsx`

### Изменяемые файлы
- `web/src/components/chat/message-input.tsx`
- `web/src/components/chat/message-bubble.tsx`
- `web/src/components/chat/chat-window.tsx`
