# План: Исправление голосового ввода в чате

## Цель
Исправить работу голосового ввода в чате: кнопка записи должна корректно инициировать запись, распознавать речь и вставлять текст в поле ввода.

## Диагностика

### Найденные проблемы

1. **use-speech-recognition.ts**:
   - Отсутствовала типизация ошибок SpeechRecognition
   - Не было состояния `isProcessing` для инициализации
   - Отсутствовала обработка ошибок `not-allowed`, `no-speech`, `network`
   - Не было auto-restart при ошибке `no-speech`
   - Не было человекочитаемых сообщений об ошибках на русском

2. **voice-input.tsx**:
   - При `!isSupported` компонент просто скрывался (return null)
   - Не было визуального отличия состояний idle/recording/error
   - Не передавались новые пропсы `isProcessing`, `error`

3. **message-input.tsx**:
   - Не использовалось поле `error` из хука
   - Не показывались toast-уведомления при ошибках
   - Не передавались новые пропсы в VoiceInput

## Исправления

### 1. use-speech-recognition.ts

**Добавлено:**
- Тип `SpeechRecognitionError` со всеми возможными ошибками
- Состояние `isProcessing` — true при инициализации микрофона
- Поле `errorMessage` — человекочитаемое сообщение на русском
- Словарь `errorMessages` с переводами ошибок
- Auto-restart при ошибке `no-speech` (через 500ms)
- Try-catch вокруг `recognition.start()` для обработки исключений
- Корректная очистка таймаутов и ресурсов

**Улучшено:**
- Обработка `onerror` с типизацией ошибок
- Обработка `onend` сбрасывает `isProcessing`
- Cleanup в useEffect очищает таймауты

### 2. voice-input.tsx

**Добавлено:**
- Новые пропсы: `isProcessing`, `error`
- Состояние disabled при `!isSupported` (вместо скрытия)
- Состояния кнопки:
  - `isProcessing` — спиннер загрузки
  - `isRecording` — красная пульсирующая кнопка
  - `hasError` — destructive стиль
  - idle — outline стиль
- Индикатор `VoiceInputIndicator` показывает:
  - Состояние инициализации
  - Состояние записи с пульсацией
  - Текущий transcript в реальном времени

### 3. message-input.tsx

**Добавлено:**
- Состояние `lastError` для дедупликации toast
- useEffect для показа toast при ошибке
- Toast с кнопкой "Повторить" для retry
- Очистка `lastError` при начале новой записи
- Передача всех новых пропсов в VoiceInput

## Состояния интерфейса

```
┌─────────────────────────────────────────────────────────────┐
│  IDLE          │  PROCESSING    │  RECORDING   │  ERROR     │
├─────────────────────────────────────────────────────────────┤
│  outline btn   │  spinner       │  red pulse   │  red btn   │
│  Mic icon      │  "Инициализация"│  Mic + dot   │  MicOff    │
└─────────────────────────────────────────────────────────────┘
```

## Обработка ошибок

| Ошибка | Сообщение | Действие |
|--------|-----------|----------|
| `not-allowed` | Нет доступа к микрофону... | Toast + кнопка Повторить |
| `no-speech` | Речь не распознана... | Auto-restart через 500ms |
| `network` | Ошибка сети... | Toast + кнопка Повторить |
| `audio-capture` | Микрофон не найден... | Toast |
| `unsupported` | Голосовой ввод не поддерживается... | Disabled кнопка |

## Файлы изменены

- `web/src/hooks/use-speech-recognition.ts`
- `web/src/components/chat/voice-input.tsx`
- `web/src/components/chat/message-input.tsx`
