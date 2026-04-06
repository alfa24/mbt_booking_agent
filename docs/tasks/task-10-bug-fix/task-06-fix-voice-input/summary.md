# Task 06: Исправить Web Speech API ошибку

## Проблема

Voice input возвращал "Ошибка сети" при завершении записи:
1. Не проверялся HTTPS контекст (Web Speech API требует HTTPS)
2. Плохая обработка ошибок сервера (все ошибки → network-error)
3. Нет различия между 400, 401, 403, 500 ошибками

## Решение

### 1. Добавлена проверка secure context

```typescript
// Проверка HTTPS или localhost
const isSecureContext = window.isSecureContext
const isLocalhost = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1'
const hasSecureContext = isSecureContext || isLocalhost

const supported = hasMediaDevices && hasMediaRecorder && hasSecureContext
```

### 2. Улучшена обработка HTTP ошибок

**Было:**
```typescript
if (!response.ok) {
  if (response.status === 400) {
    throw new Error('transcription-failed')
  }
  throw new Error('network-error')  // Все остальное → network
}
```

**Стало:**
```typescript
if (!response.ok) {
  console.error('[AudioRecording] Server error:', {
    status: response.status,
    statusText: response.statusText
  })
  
  if (response.status === 400) {
    throw new Error('transcription-failed')
  } else if (response.status === 401 || response.status === 403) {
    throw new Error('not-allowed')
  } else if (response.status >= 500) {
    throw new Error('network-error')
  } else {
    throw new Error('transcription-failed')
  }
}
```

### 3. Улучшена обработка клиентских ошибок

```typescript
// Определение типа ошибки
let errorType: AudioRecordingError = 'transcription-failed'

if (err instanceof TypeError && err.message.includes('fetch')) {
  errorType = 'network-error'
} else if (err instanceof Error) {
  const msg = err.message as AudioRecordingError
  if (errorMessages[msg]) {
    errorType = msg
  }
}

setError(errorType)
```

## Definition of Done (самопроверка)

- [x] Проверка secure context (HTTPS/localhost)
- [x] 400 ошибка → transcription-failed
- [x] 401/403 ошибка → not-allowed
- [x] 500+ ошибка → network-error
- [x] Fetch network error → network-error
- [x] Логирование всех ошибок с деталями
- [x] ESLint проходит без ошибок

## Результат

✅ Voice input стал надёжнее:
- Проверка HTTPS контекста перед инициализацией
- Детальные сообщения об ошибках сервера
- Правильное различие типов ошибок
- Логи для отладки проблем
- Пользователь видит понятные сообщения
