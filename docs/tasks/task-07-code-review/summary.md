# Task 07: Ревью кода фронтенда

## Общая оценка

В целом фронтенд реализован с учётом современных практик Next.js App Router и shadcn/ui: 
- используются route-группы `(authenticated)` и layout с AppShell;
- для ключевых сегментов есть `loading.tsx` и `error.tsx`;
- чатовый интерфейс и интеграция с Text-to-SQL выглядят концептуально корректно;
- запросы к backend завернуты в отдельные хуки и `ky`-клиент.

Однако статический анализ TypeScript показал несколько **критических ошибок компиляции**, которые необходимо исправить перед деплоем, а также несколько логических и архитектурных моментов уровня warning/info.

---

## Critical (MUST FIX)

### 1. Отсутствует компонент `Switch` из shadcn/ui
`[web/src/components/chat/data-query-mode.tsx#L1-L50](/work/python/fullstack_homework/project/web/src/components/chat/data-query-mode.tsx)`

**Проблема:**
Компонент `DataQueryMode` импортирует `Switch` из `@/components/ui/switch`, но такого файла нет. При сборке получаем ошибку TS2307/модуль не найден, а во время выполнения — падение импорта.

**Фикс (вариант A — добавить switch-компонент):
Создать `web/src/components/ui/switch.tsx` с реализацией на базе `@radix-ui/react-switch` (стандартный shadcn-паттерн), например:

```tsx
"use client"

import * as React from "react"
import * as SwitchPrimitives from "@radix-ui/react-switch"
import { cn } from "@/lib/utils"

const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitives.Root>
>(({ className, ...props }, ref) => (
  <SwitchPrimitives.Root
    ref={ref}
    className={cn(
      "peer inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border border-input bg-input transition-colors data-[state=checked]:bg-primary",
      className,
    )}
    {...props}
  >
    <SwitchPrimitives.Thumb
      className="pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-1"
    />
  </SwitchPrimitives.Root>
))
Switch.displayName = "Switch"

export { Switch }
```

**Фикс (вариант B — удалить импорт):**
Если переключатель режима временно не нужен, можно убрать использование `Switch` и привязать смену режима к кнопке/табу, но это поведенческое изменение.

---

### 2. Неверный импорт и типизация `Avatar` (Radix)
`[web/src/components/ui/avatar.tsx#L1-L60](/work/python/fullstack_homework/project/web/src/components/ui/avatar.tsx)`

**Проблема:**
Файл импортирует `AvatarPrimitive` из пакета `"radix-ui"`:

```tsx
import { Avatar as AvatarPrimitive } from "radix-ui"
```

Такого пакета нет (используются scoped-пакеты `@radix-ui/react-*`), что приводит к ошибке TS2307 и невозможности сборки.

**Фикс:**
Заменить реализацию на стандартный shadcn/ui-паттерн с `@radix-ui/react-avatar`:

```tsx
"use client"

import * as React from "react"
import * as AvatarPrimitive from "@radix-ui/react-avatar"
import { cn } from "@/lib/utils"

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn("relative flex h-8 w-8 shrink-0 overflow-hidden rounded-full", className)}
    {...props}
  />
))
Avatar.displayName = "Avatar"

const AvatarImage = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Image>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image
    ref={ref}
    className={cn("aspect-square h-full w-full", className)}
    {...props}
  />
))
AvatarImage.displayName = "AvatarImage"

const AvatarFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Fallback>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn("flex h-full w-full items-center justify-center rounded-full bg-muted", className)}
    {...props}
  />
))
AvatarFallback.displayName = "AvatarFallback"

export { Avatar, AvatarImage, AvatarFallback }
```

(При необходимости можно поверх вернуть `AvatarBadge`/`AvatarGroup`, но без несуществующего пакета.)

---

### 3. Неверный импорт `useHouses` и неявные any в `BookingsTable`
`[web/src/components/dashboard/bookings-table.tsx#L26-L55](/work/python/fullstack_homework/project/web/src/components/dashboard/bookings-table.tsx)`

**Проблема:**
- Файл импортирует `useHouses` из `"@/hooks/use-bookings"`, хотя этот хук определён в `use-houses.ts`. Это вызывает TS2305: «no exported member useHouses».
- Дополнительно TypeScript ругается на неявные `any` для параметров `house` и `h` при обходе массивов домов.

**Фикс:**
1. Исправить импорт:

```tsx
import { useBookings, type Booking, type BookingStatus } from "@/hooks/use-bookings"
import { useHouses } from "@/hooks/use-houses"
```

2. Явно типизировать элементы массива, чтобы убрать implicit any:

```tsx
// Предполагаемый тип House из use-houses
interface House {
  id: number
  name: string
  // ...остальные поля по необходимости
}

// В компоненте:
{houses?.map((house: House) => (
  <SelectItem key={house.id} value={String(house.id)}>
    {house.name}
  </SelectItem>
))}

{houses?.find((h: House) => h.id === booking.house_id)?.name || `Дом #${booking.house_id}`}
```

Либо импортировать тип `House` из `use-houses.ts`, если он там уже определён.

---

### 4. Некорректные типы для Web Speech API
`[web/src/hooks/use-speech-recognition.ts#L5-L12](/work/python/fullstack_homework/project/web/src/hooks/use-speech-recognition.ts)`

**Проблема:**
Используются типы `SpeechRecognition`, `SpeechRecognitionEvent`, `SpeechRecognitionErrorEvent` без их объявления, из-за чего компилятор выдаёт ошибки TS2304/TS2552.

**Фикс (рекомендуемый):** добавить декларации типов с опорой на DOM-типизацию:

```ts
// В начале файла или в отдельном d.ts в src/types
interface SpeechRecognition extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  maxAlternatives: number
  onaudiostart: ((this: SpeechRecognition, ev: Event) => any) | null
  onaudioend: ((this: SpeechRecognition, ev: Event) => any) | null
  onend: ((this: SpeechRecognition, ev: Event) => any) | null
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null
  // ...минимально необходимые методы
  start(): void
  stop(): void
}

interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number
  readonly results: SpeechRecognitionResultList
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string
}

declare global {
  interface Window {
    SpeechRecognition?: {
      new (): SpeechRecognition
    }
    webkitSpeechRecognition?: {
      new (): SpeechRecognition
    }
  }
}
```

Либо установить и использовать готовые типы, если они есть в отдельном пакете, но в любом случае нужно убрать «неизвестные» символы для TS.

---

## Warnings (SHOULD FIX)

### 1. Дублирование логики создания/инициализации чата
`[web/src/hooks/use-chat.ts#L27-L36](/work/python/fullstack_homework/project/web/src/hooks/use-chat.ts)` и `[web/src/components/chat/chat-widget.tsx#L9-L25](/work/python/fullstack_homework/project/web/src/components/chat/chat-widget.tsx)`

**Проблема:**
Создание чата (`createChat`) вызывается и на странице `/chat` (через `useEffect`), и в виджете `ChatWidget` при клике. Это может приводить к нескольким запросам создания чата и гонкам при обновлении `chatId`.

**Рекомендация:**
Сконцентрировать ответственность либо в `useChat` (добавив, например, ленивое создание при первом `sendMessage`), либо в одном из UI-компонентов. Минимум — добавить проверку `chatId` и флаг инициализации так, чтобы не создавать чат дважды (например, оборачивать создание чата в idempotent-логику в store).

---

### 2. Отсутствие явно настроенных `staleTime/gcTime` в TanStack Query хуках
`[web/src/hooks/use-bookings.ts#L75-L79](/work/python/fullstack_homework/project/web/src/hooks/use-bookings.ts)` и аналогичные хуки `use-houses`, `use-dashboard`, `use-leaderboard`.

**Проблема:**
Хуки используют `useQuery`/`useInfiniteQuery` без указания `staleTime` и `gcTime`. По умолчанию данные быстро становятся «устаревшими» и могут чаще перезапрашиваться, чем нужно.

**Рекомендация:**
Для дашборда/справочных данных (дома, тарифы, лидерборд) задать разумный `staleTime` (например, 30–60 секунд) и увеличить `gcTime`, чтобы уменьшить лишние запросы и мерцание UI.

Пример:

```ts
return useQuery({
  queryKey: ["bookings", filters],
  queryFn: () => fetchBookings(filters),
  staleTime: 30_000,
  gcTime: 5 * 60_000,
})
```

---

### 3. NEXT_PUBLIC_API_URL используется и на сервере, и на клиенте
`[web/src/lib/api.ts#L3-L6](/work/python/fullstack_homework/project/web/src/lib/api.ts)` и `[web/src/app/(authenticated)/dashboard/page.tsx#L8-L13](/work/python/fullstack_homework/project/web/src/app/(authenticated)/dashboard/page.tsx)`

**Проблема:**
Строка базового URL API (`NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`) дублируется в серверном компоненте `dashboard/page.tsx` и в клиентском `ky`-клиенте. Это увеличивает риск рассинхронизации конфигурации.

**Рекомендация:**
Вынести вычисление baseUrl в один модуль (например, `src/lib/config.ts`) и переиспользовать его и в `api.ts`, и в серверных `fetch`-запросах.

---

## Info (CONSIDER)

### 1. Чрезмерное использование `'use client'` в некоторых компонентах
Например, `[web/src/app/(authenticated)/layout.tsx](/work/python/fullstack_homework/project/web/src/app/(authenticated)/layout.tsx)` помечен как client component целиком из‑за проверки авторизации и `useRouter`. Это оправдано, но потенциально увеличивает клиентский бандл.

**Рекомендация:**
В будущем можно вынести auth-guard в отдельный клиентский компонент и оставить layout как серверный, если потребуется оптимизация. Сейчас это не блокер.

### 2. Поведение Text-to-SQL в UI
Компоненты `DataQueryMode` и `ConversationView` аккуратно отображают SQL и результаты, не используют `dangerouslySetInnerHTML`. Это хорошо с точки зрения XSS. При этом можно дополнительно ограничить количество отображаемых строк или размер ячеек, если ожидается очень большой результат, но это уже UX-вопрос.

---

## Безопасность

- XSS: `dangerouslySetInnerHTML` в проекте не используется, вывод контента идёт через JSX/строки.
- Env: на клиенте читается только `NEXT_PUBLIC_API_URL` — это безопасно и соответствует стандартам Next.js.
- LLM-ответы: SQL и текстовые объяснения из Text-to-SQL выводятся как plain-текст и в таблицу; прямой инъекции HTML/JS нет.

---

## Итоговая оценка

- Архитектура App Router, структура route-групп `(authenticated)` и наличие `loading.tsx`/`error.tsx` на основных сегментах — **хорошем уровне**.
- Интеграция с backend (включая `/query/natural-language`) реализована корректно и с базовой защитой от SQL injection на стороне backend.
- Главные блокеры — несколько ошибок TypeScript и отсутствующий UI-компонент `Switch`. После их исправления фронтенд можно считать готовым к дальнейшему тестированию и интеграции.

Рекомендуется сначала устранить все Critical-пункты, затем заняться Warning (особенно настройкой TanStack Query и дублирующей логикой создания чата), а Info-пункты учитывать в следующих итерациях.
