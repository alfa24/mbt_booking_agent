# Task 08: TTS индикатор воспроизведения

## Результат проверки

TTS индикатор **уже реализован** в проекте и работает корректно.

## Существующая реализация

### 1. VoiceOutput компонент (`voice-output.tsx`)

Анимация при воспроизведении (строки 53-60):
```typescript
{isSpeaking ? (
  <span className="relative">
    <VolumeX data-icon className={cn('size-4', size === 'sm' && 'size-3')} />
    <span className="absolute -right-1 -top-1 flex size-2">
      <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75" />
      <span className="relative inline-flex size-2 rounded-full bg-primary" />
    </span>
  </span>
) : (
  <Volume2 data-icon className={cn('size-4', size === 'sm' && 'size-3')} />
)}
```

Визуальные индикаторы:
- Иконка меняется с `Volume2` → `VolumeX`
- Пульсирующий кружок (animate-ping) в углу иконки
- Подсветка кнопки: `text-primary`
- Tooltip: "Остановить" / "Прослушать"

### 2. VoiceOutputIndicator компонент (строки 72-86)

Отдельный индикатор для показа в других местах:
```typescript
export function VoiceOutputIndicator({ isSpeaking }: VoiceOutputIndicatorProps) {
  if (!isSpeaking) return null

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <span className="relative flex size-3">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75" />
        <span className="relative inline-flex size-3 rounded-full bg-primary" />
      </span>
      <span>Говорит...</span>
    </div>
  )
}
```

### 3. Использование в MessageBubble

```typescript
const { isSpeaking, isSupported, speak, stop } = useSpeechSynthesis()

<VoiceOutput
  text={message.content}
  isSpeaking={isSpeaking}
  isSupported={isSupported}
  onSpeak={handleSpeak}
  onStop={stop}
  size="sm"
/>
```

## Definition of Done

- [x] Иконка меняется при воспроизведении ✅
- [x] Анимация pulse/ping ✅
- [x] Визуальная подсветка кнопки ✅
- [x] Tooltip "Остановить" ✅
- [x] Отдельный индикатор "Говорит..." ✅

## Результат

✅ TTS индикатор полностью реализован:
- Пользователь видит что сообщение воспроизводится
- Кнопка подсвечивается и анимируется
- Можно остановить воспроизведение
- Никаких изменений не требуется
