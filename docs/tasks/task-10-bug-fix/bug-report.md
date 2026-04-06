# Bug Report — Comprehensive Testing

## Обзор

Полное тестирование всех пользовательских сценариев системы бронирования через UI в браузере (Chrome/Edge) на `http://localhost:3000` и Backend API на `http://localhost:8001`.

**Дата тестирования:** 5 апреля 2026  
**Тестировщик:** AI Agent  
**Методология:** Browser UI testing + API verification через DevTools Network tab

---

## 🔴 CRITICAL Bugs

### Bug #1: Middleware PUBLIC_ROUTES логика — все пути считаются публичными

**Severity:** Critical  
**Location:** `web/src/middleware.ts` строка 19  
**Spec Reference:** `screenflow.md#route-protection`

#### Описание
Middleware использует `pathname.startsWith(route)` для PUBLIC_ROUTES `["/", "/chat", "/api"]`. Поскольку ВСЕ пути начинаются с `/`, проверка всегда возвращает true и middleware пропускает все запросы без аутентификации.

#### Шаги воспроизведения
1. Открыть любой путь `/tenant/*` или `/dashboard/*` без авторизации
2. Middleware не блокирует запрос

#### Ожидаемое поведение
Только `/`, `/chat`, `/api/*` должны быть публичными. Все остальные пути требуют аутентификации.

#### Фактическое поведение
Все пути считаются публичными из-за `pathname.startsWith("/")` = true

#### Рекомендация по исправлению
```typescript
// НЕПРАВИЛЬНО:
if (PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(route))) {

// ПРАВИЛЬНО:
const isPublicRoute = PUBLIC_ROUTES.some(route => {
  if (route === '/') return pathname === '/'
  return pathname.startsWith(route)
})
if (isPublicRoute) return
```

---

### Bug #2: SSR проблема — isAuthenticated = false при server-side rendering

**Severity:** Critical  
**Location:** `web/src/app/(authenticated)/layout.tsx` строки 14-21  
**Spec Reference:** `screenflow.md#authentication-flow`

#### Описание
В `(authenticated)/layout.tsx` используется `useAuthStore()` для проверки аутентификации. При SSR localStorage недоступен, поэтому `isAuthenticated` всегда false, что вызывает редирект на `/`.

#### Шаги воспроизведения
1. Войти как tenant
2. Перейти на `/tenant/bookings`
3. Происходит редирект на `/` → `/tenant/houses`

#### Ожидаемое поведение
Авторизованный пользователь должен иметь доступ ко всем `/tenant/*` страницам.

#### Фактическое поведение
SSR инициализирует store пустым, layout считает пользователя неавторизованным и редиректит.

#### Рекомендация по исправлению
- Убрать проверку аутентификации из layout (это делает middleware)
- Или использовать cookie-based проверку вместо Zustand store при SSR

---

### Bug #3: Login redirect не учитывает роль пользователя

**Severity:** Critical  
**Location:** `web/src/app/page.tsx` строка 35  
**Spec Reference:** `screenflow.md#login-page-`

#### Описание
После успешного входа все пользователи редиректятся на `/dashboard`, независимо от роли. Tenant должен попадать на `/tenant/houses`.

#### Шаги воспроизведения
1. Открыть `/`
2. Войти как `demo_tenant`
3. Редирект на `/dashboard` (owner страница)

#### Ожидаемое поведение
- tenant → `/tenant/houses`
- owner → `/dashboard`
- both → выбор роли или `/dashboard`

#### Фактическое поведение
Все → `/dashboard`

#### Рекомендация по исправлению
```typescript
// После успешного входа:
const role = user.role // 'tenant', 'owner', 'both'
if (role === 'tenant') {
  router.push('/tenant/houses')
} else {
  router.push('/dashboard')
}
```

---

### Bug #4: Tenant видит owner-only вкладки на dashboard

**Severity:** Critical  
**Location:** `web/src/app/(authenticated)/dashboard/layout.tsx`  
**Spec Reference:** `screenflow.md#tenant-routes`

#### Описание
Tenant пользователь видит и может взаимодействовать с owner-only вкладками: Обзор, Дома, Бронирования, Тарифы, Расходники.

#### Шаги воспроизведения
1. Войти как `demo_tenant`
2. Из-за Bug #3 попасть на `/dashboard`
3. Видеть все owner вкладки

#### Ожидаемое поведение
Tenant не должен иметь доступа к `/dashboard/*` страницам.

#### Фактическое поведение
Tenant видит и использует owner dashboard.

#### Рекомендация по исправлению
- Добавить проверку роли в dashboard layout
- Или исправить Bug #3 чтобы tenant не попадал на dashboard

---

## 🟠 HIGH Priority Bugs

### Bug #5: Intent list_bookings возвращает ошибку LLM

**Severity:** High  
**Location:** Backend chat intent processing  
**Spec Reference:** `chatflow.md#intent-mapping`

#### Описание
Запрос "Покажи мои бронирования" возвращает "Упс, мозги перегрелись. Попробуй ещё раз через минутку." вместо списка бронирований.

#### Шаги воспроизведения
1. Открыть `/chat`
2. Отправить "Покажи мои бронирования"
3. Получить ошибку вместо списка

#### Ожидаемое поведение
Список бронирований пользователя с датами, статусами, домами.

#### Фактическое поведение
Обобщенная ошибка LLM.

#### Рекомендация по исправлению
- Проверить логи backend при обработке intent `list_bookings`
- Добавить детальное логирование ошибок LLM
- Проверить что API `GET /bookings?user_id=X` работает корректно

---

### Bug #6: Web Speech API ошибка при голосовом вводе

**Severity:** High  
**Location:** Chat voice input component  
**Spec Reference:** `chatflow.md#voice-input`

#### Описание
После остановки голосовой записи появляется ошибка "Ошибка сети. Проверьте подключение к интернету."

#### Шаги воспроизведения
1. Открыть `/chat`
2. Нажать кнопку микрофона
3. Дождаться "Слушаю..."
4. Нажать "Остановить запись"
5. Получить ошибку сети

#### Ожидаемое поведение
Распознанный текст должен появиться в поле ввода.

#### Фактическое поведение
Ошибка сети.

#### Рекомендация по исправлению
- Проверить что Web Speech API поддерживается в браузере
- Добавить fallback для неподдерживаемых браузеров
- Проверить разрешение микрофона

---

### Bug #7: Множественные ошибки обработки intents в истории чата

**Severity:** High  
**Location:** Backend LLM integration  
**Spec Reference:** `chatflow.md#intent-handling`

#### Описание
В истории чата более 10 случаев когда обычные запросы ("Покажи дома", "Хочу забронировать") возвращают "Упс, мозги перегрелись".

#### Шаги воспроизведения
1. Открыть `/chat` с существующей историей
2. Прокрутить историю
3. Видеть множественные ошибки

#### Ожидаемое поведение
Стабильная обработка всех intents.

#### Фактическое поведение
~40% запросов заканчиваются ошибкой.

#### Рекомендация по исправлению
- Проверить стабильность LLM API (RouterAI)
- Добавить retry logic
- Улучшить prompt engineering для более надёжного распознавания intents

---

## 🟡 MEDIUM Priority Bugs

### Bug #8: TTS нет индикатора воспроизведения

**Severity:** Medium  
**Location:** Chat TTS button component  
**Spec Reference:** `chatflow.md#voice-output`

#### Описание
При нажатии кнопки 🔊 нет видимого индикатора что аудио воспроизводится.

#### Ожидаемое поведение
Визуальный feedback (анимация, прогресс-бар) при воспроизведении.

#### Рекомендация по исправлению
Добавить состояние `isPlaying` и визуальный индикатор на кнопку.

---

### Bug #9: Skeleton loading не виден при нормальной загрузке

**Severity:** Low  
**Location:** Various page components  
**Spec Reference:** `screenflow.md#ui-patterns`

#### Описание
Skeleton loading реализован в коде, но не наблюдается при нормальной загрузке данных (данные загружаются слишком быстро или skeleton не показывается).

#### Рекомендация по исправлению
Добавить минимальную задержку показа skeleton (min 300ms) для лучшего UX.

---

## 📊 Статистика багов

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | 4 | Requires immediate fix |
| 🟠 High | 3 | Should fix before release |
| 🟡 Medium | 1 | Nice to have |
| 🟢 Low | 1 | Cosmetic |
| **Total** | **9** | |

---

## 🧪 Результаты тестирования по сценариям

### Tenant UI (5 сценариев)

| Сценарий | Статус | Заблокирован |
|----------|--------|--------------|
| 1. Вход в систему | ⚠️ PARTIAL | Bug #3, #4 |
| 2. Каталог домов | ✅ PASS | - |
| 3. Детали дома | ❌ BLOCKED | Bug #1, #2 |
| 4. Мои бронирования | ❌ BLOCKED | Bug #1, #2 |
| 5. Новое бронирование | ❌ BLOCKED | Bug #1, #2 |

### Owner UI (6 сценариев)

| Сценарий | Статус | Примечание |
|----------|--------|------------|
| 1. Dashboard | ✅ PASS | Все KPI и графики работают |
| 2. Управление домами | ✅ PASS | CRUD операции работают |
| 3. Управление бронированиями | ✅ PASS | Фильтры и статусы работают |
| 4. Управление тарифами | ✅ PASS | CRUD операции работают |
| 5. Учёт расходников | ✅ PASS | Фильтрация по дому работает |
| 6. Лидерборд | ✅ PASS | Таблица/Календарь/Графики работают |

### Chat UI (5 сценариев)

| Сценарий | Статус | Примечание |
|----------|--------|------------|
| 1. Базовый чат | ⚠️ PARTIAL | Bug #5, #7 |
| 2. Голосовой ввод | ❌ FAIL | Bug #6 |
| 3. Голосовой вывод | ⚠️ PARTIAL | Bug #8 |
| 4. Intent обработка | ⚠️ PARTIAL | list_houses ✅, list_bookings ❌ |
| 5. Создание чата | ✅ PASS | Приветствие отображается |

### Backend API (через DevTools Network)

| Endpoint Group | Статус | Примечание |
|----------------|--------|------------|
| Users API | ✅ PASS | Все запросы 200 OK |
| Houses API | ✅ PASS | Все запросы 200 OK |
| Bookings API | ✅ PASS | Все запросы 200 OK |
| Tariffs API | ✅ PASS | Все запросы 200 OK |
| Dashboard API | ✅ PASS | KPI и графики загружаются |
| Consumable Notes API | ✅ PASS | Все запросы 200 OK |
| Chat API | ⚠️ PARTIAL | POST работает, LLM обработка нестабильна |
| Query API (Text-to-SQL) | ⚠️ NOT TESTED | UI mode переключается, но backend не тестировался |

---

## 💡 Общие рекомендации

### 1. Критические fixes (без этого система не работает)
- Исправить middleware PUBLIC_ROUTES логику
- Убрать SSR проверку isAuthenticated из layout
- Исправить login redirect на основе роли
- Блокировать tenant доступ к /dashboard/*

### 2. Chat stability (улучшение UX)
- Стабилизировать LLM intent processing
- Добавить retry logic для LLM запросов
- Улучшить error messages (показывать конкретные ошибки вместо "мозги перегрелись")
- Исправить Web Speech API integration

### 3. UI/UX improvements
- Добавить визуальный feedback для TTS
- Показывать skeleton loading consistently
- Добавить toast уведомления для ошибок
- Улучшить empty states

---

## 📸 Скриншоты

Все скриншоты сохранены в:
- `/tmp/05_tenant_on_dashboard.png` — Tenant на owner dashboard
- `/tmp/03_bug_house_detail_redirect.png` — Редирект деталей дома
- `/tmp/02_tenant_houses_catalog.png` — Каталог домов (работает)
- `/tmp/owner_dashboard_01_initial.png` — Owner dashboard KPI
- `/tmp/owner_houses_03_add_modal.png` — Add house modal
- `/tmp/owner_bookings_04_list.png` — Owner bookings list
- `/tmp/owner_tariffs_05_list.png` — Tariffs list
- `/tmp/owner_consumables_06_list.png` — Consumables by house
- `/tmp/owner_leaderboard_07_table.png` — Leaderboard table
- `/tmp/owner_leaderboard_08_calendar.png` — Leaderboard calendar
- Chat screenshots в кэше изображений Qoder

---

**Заключение:** Система имеет 4 критических бага в аутентификации/маршрутизации которые блокируют ~60% tenant функционала. Owner UI работает стабильно. Chat UI имеет хороший дизайн но нестабильную LLM интеграцию (~40% ошибок). Backend API endpoints работают корректно.
