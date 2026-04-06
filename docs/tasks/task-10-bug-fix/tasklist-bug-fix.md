# Bug Fix Tasklist

## Обзор

Комплексное исправление 9 багов, найденных при тестировании всех сценариев specs через UI в браузере. Баги разделены на 4 критических (блокируют tenant functional), 3 high priority (нестабильный chat), 2 medium/low (UI improvements).

## Легенда статусов
- 📋 Planned
- 🚧 In Progress
- ✅ Done

## Список задач

| Задача | Описание | Severity | Статус | Документы |
|--------|----------|----------|--------|-----------|
| 01 | Исправить middleware PUBLIC_ROUTES логику | Critical | 📋 | [план](task-01-fix-middleware/plan.md) |
| 02 | Исправить SSR isAuthenticated проверку в layout | Critical | 📋 | [план](task-02-fix-ssr-auth/plan.md) |
| 03 | Исправить login redirect по роли пользователя | Critical | 📋 | [план](task-03-fix-login-redirect/plan.md) |
| 04 | Заблокировать tenant доступ к /dashboard/* | Critical | 📋 | [план](task-04-block-tenant-dashboard/plan.md) |
| 05 | Стабилизировать intent list_bookings в chat | High | 📋 | [план](task-05-fix-list-bookings-intent/plan.md) |
| 06 | Исправить Web Speech API ошибку | High | 📋 | [план](task-06-fix-voice-input/plan.md) |
| 07 | Улучшить стабильность LLM intent processing | High | 📋 | [план](task-07-stabilize-llm-intents/plan.md) |
| 08 | Добавить TTS индикатор воспроизведения | Medium | 📋 | [план](task-08-add-tts-indicator/plan.md) |
| 09 | Улучшить skeleton loading UX | Low | 📋 | [plan](task-09-improve-skeleton-loading/plan.md) |

---

## Детализация задач

### Задача 01: Исправить middleware PUBLIC_ROUTES логику

**Цель:** Middleware должен корректно определять публичные маршруты и блокировать неавторизованный доступ к защищённым страницам.

**Состав работ:**
- [ ] Исправить логику `startsWith("/")` в `web/src/middleware.ts`
- [ ] Разделить exact match (`/`) и prefix match (`/api`, `/chat`)
- [ ] Протестировать что `/tenant/*` и `/dashboard/*` требуют авторизации
- [ ] Протестировать что `/`, `/chat`, `/api/*` доступны без авторизации
- [ ] Обновить тесты middleware

**Definition of Done:**
- [ ] `/tenant/bookings` без авторизации → редирект на `/`
- [ ] `/dashboard/houses` без авторизации → редирект на `/`
- [ ] `/` → доступен без авторизации
- [ ] `/chat` → доступен без авторизации
- [ ] `/api/v1/health` → доступен без авторизации
- [ ] Все существующие тесты проходят

**Артефакты:**
- Исправленный `web/src/middleware.ts`
- Обновлённые тесты

**Документы:**
- [bug-report.md#bug-1](../task-10-bug-fix/bug-report.md#bug-1)

---

### Задача 02: Исправить SSR isAuthenticated проверку в layout

**Цель:** Убрать редирект на `/` при server-side rendering когда Zustand store ещё не инициализирован.

**Состав работ:**
- [ ] Убрать проверку `isAuthenticated` из `web/src/app/(authenticated)/layout.tsx`
- [ ] Полагаться на middleware для проверки авторизации
- [ ] Добавить loading state для client-side hydration
- [ ] Протестировать что tenant может открывать все `/tenant/*` страницы
- [ ] Протестировать что owner может открывать все `/dashboard/*` страницы

**Definition of Done:**
- [ ] `/tenant/houses` → загружается без редиректа
- [ ] `/tenant/bookings` → загружается без редиректа
- [ ] `/tenant/houses/[id]` → загружается без редиректа
- [ ] Консоль браузера без ошибок
- [ ] Нет flash-of-redirect при загрузке страниц

**Артефакты:**
- Исправленный `web/src/app/(authenticated)/layout.tsx`

**Документы:**
- [bug-report.md#bug-2](../task-10-bug-fix/bug-report.md#bug-2)

---

### Задача 03: Исправить login redirect по роли пользователя

**Цель:** После входа пользователь должен попадать на правильную страницу в зависимости от роли.

**Состав работ:**
- [ ] Изменить `web/src/app/page.tsx` для проверки роли пользователя
- [ ] tenant → `/tenant/houses`
- [ ] owner → `/dashboard`
- [ ] both → выбор роли или `/dashboard`
- [ ] Протестировать вход для каждой роли
- [ ] Проверить что cookie `user_role` устанавливается корректно

**Definition of Done:**
- [ ] Вход как `demo_tenant` → редирект на `/tenant/houses`
- [ ] Вход как `demo_owner` → редирект на `/dashboard`
- [ ] Cookie `user_role=tenant` для tenant
- [ ] Cookie `user_role=owner` для owner
- [ ] Нет ошибок в консоли

**Артефакты:**
- Исправленный `web/src/app/page.tsx`

**Документы:**
- [bug-report.md#bug-3](../task-10-bug-fix/bug-report.md#bug-3)

---

### Задача 04: Заблокировать tenant доступ к /dashboard/*

**Цель:** Tenant пользователи не должны иметь доступа к owner dashboard.

**Состав работ:**
- [ ] Добавить проверку роли в `web/src/app/(authenticated)/dashboard/layout.tsx`
- [ ] Или добавить middleware защиту для `/dashboard/*` routes
- [ ] При попытке tenant открыть `/dashboard` → редирект на `/tenant/houses`
- [ ] Протестировать что tenant не видит owner вкладки
- [ ] Протестировать что owner имеет полный доступ

**Definition of Done:**
- [ ] Tenant → `/dashboard` → редирект на `/tenant/houses`
- [ ] Tenant → `/dashboard/houses` → редирект на `/tenant/houses`
- [ ] Owner → `/dashboard` → доступ разрешён
- [ ] Owner → `/dashboard/*` → доступ разрешён

**Артефакты:**
- Исправленный dashboard layout или middleware

**Документы:**
- [bug-report.md#bug-4](../task-10-bug-fix/bug-report.md#bug-4)

---

### Задача 05: Стабилизировать intent list_bookings в chat

**Цель:** Запрос "Покажи мои бронирования" должен стабильно возвращать список бронирований.

**Состав работ:**
- [ ] Проверить логи backend при обработке intent `list_bookings`
- [ ] Проверить что API `GET /bookings?user_id=X` работает
- [ ] Добавить детальное логирование ошибок LLM
- [ ] Исправить обработку ошибок в chat service
- [ ] Протестировать через UI chat

**Definition of Done:**
- [ ] Отправка "Покажи мои бронирования" → список бронирований
- [ ] Отправка "Какие у меня брони?" → список бронирований
- [ ] Нет ошибок "Упс, мозги перегрелись"
- [ ] В консоли backend нет ошибок

**Артефакты:**
- Исправленный backend chat service
- Логи с деталями обработки

**Документы:**
- [bug-report.md#bug-5](../task-10-bug-fix/bug-report.md#bug-5)

---

### Задача 06: Исправить Web Speech API ошибку

**Цель:** Голосовой ввод должен работать без ошибок "Ошибка сети".

**Состав работ:**
- [ ] Проверить поддержку Web Speech API в браузере
- [ ] Добавить fallback для неподдерживаемых браузеров
- [ ] Проверить разрешение микрофона
- [ ] Добавить обработку ошибок распознавания речи
- [ ] Протестировать голосовой ввод в Chrome

**Definition of Done:**
- [ ] Нажатие микрофона → "Слушаю..."
- [ ] Говорим фразу → текст появляется в поле ввода
- [ ] Нет ошибки "Ошибка сети"
- [ ] Для неподдерживаемых браузеров показывается сообщение

**Артефакты:**
- Исправленный voice input component
- Fallback UI для неподдерживаемых браузеров

**Документы:**
- [bug-report.md#bug-6](../task-10-bug-fix/bug-report.md#bug-6)

---

### Задача 07: Улучшить стабильность LLM intent processing

**Цель:** Снизить процент ошибок обработки intents с ~40% до <5%.

**Состав работ:**
- [ ] Проверить стабильность RouterAI API
- [ ] Добавить retry logic для failed LLM запросов
- [ ] Улучшить prompt engineering для распознавания intents
- [ ] Добавить caching для одинаковых запросов
- [ ] Мониторинг success rate intents

**Definition of Done:**
- [ ] 95%+ intents обрабатываются без ошибок
- [ ] Retry logic работает (макс 2 retry)
- [ ] В логах backend меньше 5% ошибок LLM
- [ ] Тестовые запросы стабильно проходят

**Артефакты:**
- Улучшенный LLM service с retry logic
- Метрики success rate

**Документы:**
- [bug-report.md#bug-7](../task-10-bug-fix/bug-report.md#bug-7)

---

### Задача 08: Добавить TTS индикатор воспроизведения

**Цель:** Пользователь должен видеть когда аудио воспроизводится.

**Состав работ:**
- [ ] Добавить состояние `isPlaying` в TTS компонент
- [ ] Визуальный индикатор на кнопке 🔊 (анимация или прогресс)
- [ ] Блокировка повторного нажатия во время воспроизведения
- [ ] Обработка завершения воспроизведения

**Definition of Done:**
- [ ] Нажатие 🔊 → кнопка меняет цвет/анимацию
- [ ] Во время воспроизведения видно прогресс
- [ ] После завершения → кнопка возвращается в исходное состояние
- [ ] Нельзя запустить второе воспроизведение параллельно

**Артефакты:**
- Улучшенный TTS компонент с индикатором

**Документы:**
- [bug-report.md#bug-8](../task-10-bug-fix/bug-report.md#bug-8)

---

### Задача 09: Улучшить skeleton loading UX

**Цель:** Skeleton loading должен быть виден и создавать ощущение быстрой загрузки.

**Состав работ:**
- [ ] Добавить минимальную задержку показа skeleton (300ms)
- [ ] Проверить что skeleton показывается на всех страницах
- [ ] Добавить smooth transition от skeleton к контенту
- [ ] Протестировать на slow 3G throttling в DevTools

**Definition of Done:**
- [ ] Skeleton виден при загрузке данных
- [ ] Переход skeleton → контент smooth (fade-in)
- [ ] На всех страницах есть skeleton loading
- [ ] Нет flash-of-unstyled-content

**Артефакты:**
- Обновлённые компоненты с улучшенным skeleton loading

**Документы:**
- [bug-report.md#bug-9](../task-10-bug-fix/bug-report.md#bug-9)

---

## Приоритизация

### P0 — Blockers (немедленно)
- Задача 01: Middleware PUBLIC_ROUTES
- Задача 02: SSR isAuthenticated
- Задача 03: Login redirect
- Задача 04: Block tenant dashboard

### P1 — High Priority (до релиза)
- Задача 05: Fix list_bookings intent
- Задача 06: Fix voice input
- Задача 07: Stabilize LLM intents

### P2 — Medium Priority (улучшения)
- Задача 08: TTS indicator
- Задача 09: Skeleton loading

---

## Оценка объёма

- **P0 tasks:** 2-3 часа
- **P1 tasks:** 3-4 часа
- **P2 tasks:** 1-2 часа
- **Total:** 6-9 часов разработки + 2 часа тестирования
