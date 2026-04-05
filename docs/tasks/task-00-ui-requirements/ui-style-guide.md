# UI Style Guide

## Общие принципы

- **Светлая тема** — единственная тема для MVP
- **Travel-стиль** — природные цвета, воздушность, спокойствие
- **Семантические цвета** — через CSS variables, без raw-цветов
- **Accessibility first** — все интерактивные элементы доступны

---

## Цветовая палитра

### CSS Variables

```css
:root {
  /* Primary — природный зелёный */
  --primary: 142 76% 36%;
  --primary-foreground: 0 0% 100%;
  
  /* Accent — песочный */
  --accent: 45 93% 47%;
  --accent-foreground: 0 0% 9%;
  
  /* Background — чистый белый */
  --background: 0 0% 100%;
  --foreground: 0 0% 9%;
  
  /* Muted — серый для вторичного текста */
  --muted: 0 0% 96%;
  --muted-foreground: 0 0% 45%;
  
  /* Card — карточки поверх фона */
  --card: 0 0% 100%;
  --card-foreground: 0 0% 9%;
  
  /* Border — границы */
  --border: 0 0% 90%;
  --input: 0 0% 90%;
  --ring: 142 76% 36%;
  
  /* Secondary — нейтральный */
  --secondary: 0 0% 96%;
  --secondary-foreground: 0 0% 9%;
  
  /* Destructive — ошибки */
  --destructive: 0 84% 60%;
  --destructive-foreground: 0 0% 100%;
  
  /* Success — успех */
  --success: 142 76% 36%;
  --success-foreground: 0 0% 100%;
  
  /* Warning — предупреждения */
  --warning: 38 92% 50%;
  --warning-foreground: 0 0% 9%;
}
```

### Использование

**Правильно:**
```tsx
<div className="bg-primary text-primary-foreground">
<span className="text-muted-foreground">
<Card className="bg-card">
```

**Неправильно:**
```tsx
<div className="bg-green-500">
<span className="text-gray-500">
<Card className="bg-white">
```

---

## Типографика

### Шрифт
- **Основной:** Inter (Google Fonts)
- **Fallback:** system-ui, -apple-system, sans-serif

### Размеры

| Класс | Размер | Использование |
|-------|--------|---------------|
| `text-xs` | 12px | Подписи, время сообщений |
| `text-sm` | 14px | Вторичный текст, описания |
| `text-base` | 16px | Основной текст |
| `text-lg` | 18px | Подзаголовки |
| `text-xl` | 20px | Заголовки карточек |
| `text-2xl` | 24px | Заголовки секций |
| `text-3xl` | 30px | Страничные заголовки |
| `text-4xl` | 36px | Hero-заголовки |

### Вес
- `font-normal` (400) — основной текст
- `font-medium` (500) — подзаголовки, кнопки
- `font-semibold` (600) — заголовки, активные элементы
- `font-bold` (700) — KPI-значения, акценты

---

## Tailwind CSS v4

### @theme inline

```css
@import "tailwindcss";

@theme inline {
  --color-primary: hsl(var(--primary));
  --color-primary-foreground: hsl(var(--primary-foreground));
  --color-accent: hsl(var(--accent));
  --color-accent-foreground: hsl(var(--accent-foreground));
  --color-background: hsl(var(--background));
  --color-foreground: hsl(var(--foreground));
  --color-muted: hsl(var(--muted));
  --color-muted-foreground: hsl(var(--muted-foreground));
  --color-card: hsl(var(--card));
  --color-card-foreground: hsl(var(--card-foreground));
  --color-border: hsl(var(--border));
  --color-input: hsl(var(--input));
  --color-ring: hsl(var(--ring));
  --color-secondary: hsl(var(--secondary));
  --color-secondary-foreground: hsl(var(--secondary-foreground));
  --color-destructive: hsl(var(--destructive));
  --color-destructive-foreground: hsl(var(--destructive-foreground));
  
  --font-sans: "Inter", system-ui, sans-serif;
  
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
}
```

---

## Spacing

### Gap vs Space

**Используй `gap-*` для flex/grid контейнеров:**
```tsx
<div className="flex flex-col gap-4">
<div className="grid grid-cols-3 gap-6">
```

**Не используй `space-y-*`:**
```tsx
<!-- Неправильно -->
<div className="flex flex-col space-y-4">
```

### Size для квадратных элементов

```tsx
<!-- Иконки, аватары -->
<div className="size-10">
<Icon className="size-4">
```

### Стандартные отступы

| Значение | Пиксели | Использование |
|----------|---------|---------------|
| `gap-2` | 8px | Мелкие группы |
| `gap-3` | 12px | Формы, списки |
| `gap-4` | 16px | Карточки, секции |
| `gap-6` | 24px | Большие блоки |
| `p-4` | 16px | Внутренние отступы карточек |
| `p-6` | 24px | Модальные окна |
| `px-4` | 16px гориз. | Кнопки, инпуты |
| `py-2` | 8px верт. | Кнопки, бейджи |

---

## shadcn/ui

### Установка компонентов

```bash
npx shadcn add button
npx shadcn add card
npx shadcn add input
npx shadcn add dialog
npx shadcn add sheet
npx shadcn add scroll-area
npx shadcn add avatar
npx shadcn add badge
npx shadcn add separator
npx shadcn add tabs
npx shadcn add sonner
```

### Кастомизация через CSS variables

Все компоненты используют семантические цвета:

```tsx
// Button автоматически использует --primary
<Button variant="default">Primary</Button>

// Secondary использует --secondary
<Button variant="secondary">Secondary</Button>

// Outline использует --border
<Button variant="outline">Outline</Button>

// Ghost для третичных действий
<Button variant="ghost">Ghost</Button>
```

---

## Условные классы

### Функция cn()

```tsx
import { cn } from "@/lib/utils";

// Базовые + условные классы
<div className={cn(
  "flex items-center gap-2",
  isActive && "bg-primary text-primary-foreground",
  isDisabled && "opacity-50 cursor-not-allowed"
)}>

// Объединение с className из props
<Button className={cn("w-full", className)} {...props} />
```

---

## Формы

### Структура FieldGroup

```tsx
<div className="space-y-4">
  <div className="space-y-2">
    <Label htmlFor="email">Email</Label>
    <Input
      id="email"
      type="email"
      aria-invalid={!!error}
      data-invalid={!!error}
    />
    {error && (
      <p className="text-sm text-destructive">{error}</p>
    )}
  </div>
</div>
```

### Валидация

- Используй `data-invalid` + `aria-invalid` для стилизации ошибок
- Сообщения об ошибках — под полем, красным цветом
- Поля с ошибками — красная рамка (через `[data-invalid]`)

---

## Toast-уведомления

### Sonner

```tsx
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

// В layout
<Toaster position="top-right" />

// Использование
toast.success("Бронирование создано");
toast.error("Не удалось сохранить");
toast.info("Новое сообщение в чате");
```

---

## Accessibility

### Dialog / Sheet / Drawer

**Всегда включай Title (даже visually hidden):**

```tsx
<Dialog>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Создать бронирование</DialogTitle>
      <DialogDescription>
        Заполните данные для создания нового бронирования
      </DialogDescription>
    </DialogHeader>
    {/* ... */}
  </DialogContent>
</Dialog>
```

### Кнопки с иконками

**Всегда добавляй `data-icon`:**

```tsx
<Button>
  <Plus className="size-4" data-icon />
  <span>Создать</span>
</Button>
```

### Focus states

- Все интерактивные элементы имеют visible focus ring
- Используй `focus-visible:ring-2 focus-visible:ring-ring`

### ARIA-атрибуты

```tsx
<button aria-label="Закрыть модальное окно">
<nav aria-label="Главная навигация">
<main aria-label="Основной контент">
```

---

## Компоненты

### KPI-карточка

```tsx
<Card>
  <CardHeader className="flex flex-row items-center justify-between pb-2">
    <CardTitle className="text-sm font-medium text-muted-foreground">
      Общая выручка
    </CardTitle>
    <DollarSign className="size-4 text-muted-foreground" data-icon />
  </CardHeader>
  <CardContent>
    <div className="text-2xl font-bold">₽125,000</div>
    <p className="text-xs text-muted-foreground">
      +12% с прошлого месяца
    </p>
  </CardContent>
</Card>
```

### Таблица

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Дом</TableHead>
      <TableHead>Даты</TableHead>
      <TableHead className="text-right">Сумма</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">Старый дом</TableCell>
      <TableCell>01.06 — 03.06</TableCell>
      <TableCell className="text-right">₽5,000</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Сообщение в чате

```tsx
<div className={cn(
  "flex gap-3",
  isUser ? "flex-row-reverse" : "flex-row"
)}>
  <Avatar className="size-8">
    <AvatarFallback>{isUser ? "U" : "B"}</AvatarFallback>
  </Avatar>
  <div className={cn(
    "rounded-lg px-4 py-2 max-w-[80%]",
    isUser 
      ? "bg-primary text-primary-foreground" 
      : "bg-muted"
  )}>
    <p className="text-sm">{message.text}</p>
    <span className="text-xs opacity-70">
      {formatTime(message.createdAt)}
    </span>
  </div>
</div>
```
