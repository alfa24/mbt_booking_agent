# Task 10: Spec Consistency Fix Summary

## Completed Work

### Phase 1: Critical Fixes
Исправлены критические несоответствия между spec документами и backend кодом.

**Единицы измерения (kopecks → rubles):**
- data-model.md строка 80: `total_amount` — "в копейках" → "в рублях"
- data-model.md строка 215: `total_amount` — "Итоговая сумма (копейки)" → "Итоговая сумма (рубли)"
- data-model.md строка 93: `amount` (tariff) — "в копейках" → "в рублях"
- data-model.md строка 232: `amount` (tariff) — "Стоимость (копейки)" → "Стоимость (рубли)"

**Filter naming (tenant_id → user_id):**
- screenflow.md строка 277: `GET /bookings?tenant_id=...` → `GET /bookings?user_id=...`
- chatflow.md строка 65: `GET /bookings?tenant_id=...` → `GET /bookings?user_id=...`

**Chat cardinality:**
- data-model.md строка 107: "несколько чатов" → "один чат с ассистентом"

### Phase 2: Endpoint Logic
Удалены несуществующие endpoints, добавлены отсутствующие CRUD методы.

**Удалено:**
- PATCH /bookings/{id}/cancel — не реализован в backend, используется DELETE

**Добавлено в api-contracts.md:**
- `DELETE /bookings/{id}` — отмена бронирования (soft delete, status=cancelled)
- `DELETE /houses/{id}` — удаление дома (hard delete, необратимо)
- `PUT /tariffs/{id}` — полная замена тарифа
- `DELETE /tariffs/{id}` — удаление тарифа
- `DELETE /users/{id}` — удаление пользователя

**Исправлено в screenflow.md:**
- Строка 286: отмена бронирования `PATCH /bookings/{id}` → `DELETE /bookings/{id}`
- Строка 584: отмена бронирования `PATCH /bookings/{id}` → `DELETE /bookings/{id}`
- Строка 91: авторизация — удалён `GET /users/telegram/{username}`, добавлена логика с localStorage

**Исправлено в chatflow.md:**
- Строка 86: отмена бронирования `PATCH /bookings/{id}` → `DELETE /bookings/{id}`
- Строка 375: удалён endpoint `GET /chats/user/{user_id}`

### Phase 3: Consistency Improvements
Улучшена документация для ясности и полноты.

**Field mapping:**
- api-contracts.md POST /bookings: добавлено примечание "guests в request → guests_planned в response"

**Pagination:**
- api-contracts.md GET /tariffs: добавлены query params (limit, offset, sort)
- api-contracts.md GET /chats/{id}/messages: добавлено пояснение про cursor-based pagination

**Authentication placeholder:**
- api-contracts.md: добавлено примечание про временные заглушки (tenant_id=1, user_id=1, owner_id=1)

**PUT vs PATCH:**
- screenflow.md: добавлено примечание про PUT для полного обновления в секции "Управление домами"

### Files Modified
1. **docs/data-model.md** — 5 changes (units: kopecks → rubles, chat cardinality)
2. **docs/tech/api-contracts.md** — 10 changes (endpoints, pagination, auth note, field mapping)
3. **docs/specs/screenflow.md** — 5 changes (booking cancel, auth flow, PUT note)
4. **docs/specs/chatflow.md** — 3 changes (booking cancel, removed endpoint)

**Total:** 4 files, 23 changes

### Validation Results
- ✅ Cross-reference check: **PASSED**
  - Все упоминания "копейки" удалены из data-model.md
  - Все tenant_id в query params заменены на user_id
  - PATCH /bookings/{id}/cancel удалён из api-contracts.md
  
- ✅ Backend code audit: **PASSED**
  - Все documented endpoints существуют в backend/api/
  - DELETE /bookings/{id} соответствует backend/api/bookings.py:178-220 (soft delete)
  - DELETE /houses/{id} соответствует backend/api/houses.py:200-226 (hard delete)
  - Field names соответствуют backend/schemas/ (guests → guests_planned mapping)
  
- ✅ Unit consistency: **PASSED**
  - total_amount: везде "рубли" (data-model.md, api-contracts.md, backend schemas)
  - tariff.amount: везде "рубли" (data-model.md, api-contracts.md, backend schemas)

- **Remaining discrepancies:** None

## Lessons Learned
1. **Backend code is source of truth** — при противоречиях между spec и кодом, код всегда приоритетнее
2. **Unit consistency matters** — несоответствие единиц измерения (рубли vs копейки) может привести к критическим багам
3. **Document auth placeholders** — временные решения должны быть явно задокументированы как TODO
4. **CRUD completeness** — если есть POST/PATCH, должны быть DELETE и PUT endpoints в документации

## Recommendations
1. Добавить автоматическую валидацию spec документов против backend schemas в CI/CD
2. Создать скрипт для проверки единиц измерения во всех документах
3. При изменении backend API обновлять spec документы в том же PR
4. Добавить cross-reference index для быстрого поиска всех упоминаний endpoint'ов
