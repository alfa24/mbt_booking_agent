# Исправление несоответствий в spec-документах

## Обнаруженные несоответствия

### 1. КРИТИЧЕСКИЕ: Названия полей в API vs Data Model

**Проблема:** В api-contracts.md и data-model.md разные названия полей для фильтрации бронирований по арендатору.

- **api-contracts.md (строка 294):** `user_id` — фильтр по арендатору
- **screenflow.md (строка 277):** `GET /bookings?tenant_id={current_user_id}`
- **chatflow.md (строка 65):** `GET /bookings?tenant_id={user_id}`
- **data-model.md:** поле называется `tenant_id`

**Исправление:** api-contracts.md строка 294 — заменить `user_id` на `tenant_id`

---

### 2. КРИТИЧЕСКИЕ: Единицы измерения total_amount

**Проблема:** Противоречие в единицах измерения суммы бронирования.

- **api-contracts.md (строка 540):** `total_amount` — "Итоговая сумма в **рублях**"
- **api-contracts.md (строка 596):** `total_revenue` — "общая выручка в **копейках**"
- **data-model.md (строка 80):** `total_amount` — "Итоговая сумма в **копейках**"
- **data-model.md (строка 215):** `total_amount` — `INTEGER`, CHECK >= 0, "Итоговая сумма (копейки)"

**Исправление:** api-contracts.md строка 540 — изменить на "в копейках" для консистентности

---

### 3. КРИТИЧЕСКИЕ: Missing endpoint /chats/user/{user_id}

**Проблема:** Screenflow и chatflow ссылаются на endpoint, которого нет в api-contracts.md.

- **screenflow.md (строка 806):** `GET /chats/user/{user_id}` — создание/получение чата
- **chatflow.md (строка 376):** `GET /chats/user/{user_id}` — "Получить или создать чат пользователя"
- **api-contracts.md:** Отсутствует этот endpoint, есть только `POST /chats` и `GET /chats/{id}/messages`

**Исправление:** Добавить в api-contracts.md новый endpoint `GET /chats/user/{user_id}` с описанием логики авто-создания чата

---

### 4. ВАЖНЫЕ: Tariffs units inconsistency

**Проблема:** Разные единицы измерения в tariff amount.

- **api-contracts.md (строка 442):** `amount: 250` — без указания единиц
- **api-contracts.md (строка 557):** "Стоимость в **рублях** (0 = бесплатно)"
- **api-contracts.md (строка 596):** revenue "в копейках"
- **data-model.md (строка 93):** "Стоимость проживания в **копейках**"
- **data-model.md (строка 232):** `amount` — "Стоимость (копейки)"

**Исправление:** api-contracts.md строка 557 — изменить на "в копейках"

---

### 5. ВАЖНЫЕ: Booking status update method inconsistency

**Проблема:** Разные способы отмены бронирования.

- **api-contracts.md (строка 373-403):** `PATCH /bookings/{id}` с body `{status: "cancelled"}`
- **api-contracts.md (строка 405-427):** Отдельный endpoint `PATCH /bookings/{id}/cancel`
- **screenflow.md (строка 286):** `PATCH /bookings/{id}` с `status: "cancelled"`
- **chatflow.md (строка 86):** `PATCH /bookings/{id}` с `status: cancelled`

**Исправление:** 
- Оставить оба варианта, но документировать разницу: `PATCH /bookings/{id}` для общих обновлений, `/cancel` как специализированный endpoint
- Унифицировать примеры в screenflow.md и chatflow.md — указать оба варианта или推荐 специализированный

---

### 6. ВАЖНЫЕ: Missing endpoint /users/telegram/{username}

**Проблема:** Screenflow ссылается на endpoint для авторизации, которого нет в api-contracts.

- **screenflow.md (строка 91):** `GET /users/telegram/{username}` — запрос к API для входа
- **api-contracts.md:** Отсутствует такой endpoint, есть только `POST /users`, `GET /users`, `GET /users/{id}`

**Исправление:** Добавить в api-contracts.md endpoint `GET /users/telegram/{telegram_username}` для поиска пользователя по username

---

### 7. СРЕДНИЕ: Pagination style inconsistency для Chat Messages

**Проблема:** Разные подходы к пагинации.

- **api-contracts.md (строка 36-53):** Общий `PaginatedResponse` с offset/limit
- **api-contracts.md (строка 812-844):** Chat messages используют `CursorPaginatedResponse` с cursor-based пагинацией
- **Остальные endpoints:** Используют offset-based пагинацию

**Исправление:** Это не ошибка, а feature — задокументировать явно почему chat messages используют cursor-based пагинацию (для real-time обновлений)

---

### 8. СРЕДНИЕ: Missing Houses CRUD endpoints в Chatflow

**Проблема:** Chatflow описывает сценарии управления домами через чат, но нет intent mapping.

- **chatflow.md (строка 331-348):** Intent mapping таблица
- Отсутствуют intents: `create_house`, `update_house`, `delete_house`
- **screenflow.md (строки 472-531):** Описан полный CRUD для домов

**Исправление:** Добавить в chatflow.md intents для управления домами, если это планируется

---

### 9. СРЕДНИЕ: Chat title inconsistency

**Проблема:** Разное описание количества чатов.

- **data-model.md (строка 107):** "Каждый пользователь может иметь **несколько чатов**"
- **screenflow.md (строка 768):** "**Без списка диалогов** — только один чат на пользователя"
- **chatflow.md (строка 15):** "Полноэкранный чат **без списка диалогов** (один чат на пользователя)"

**Исправление:** data-model.md строка 107 — изменить на "один чат на пользователя"

---

### 10. СРЕДНИЕ: Missing DELETE endpoints

**Проблема:** В api-contracts.md отсутствуют endpoint'ы для удаления ресурсов.

- Отсутствует `DELETE /houses/{id}` (screenflow.md строка 522 использует)
- Отсутствует `DELETE /tariffs/{id}` (screenflow.md строка 640 использует)
- Отсутствует `DELETE /bookings/{id}` (screenflow.md строка 286 описывает отмену через PATCH)
- Присутствует `DELETE /consumable-notes/{id}` (строка 762)

**Исправление:** Добавить в api-contracts.md:
- `DELETE /houses/{id}`
- `DELETE /tariffs/{id}`

---

### 11. СРЕДНИЕ: Booking guests field naming

**Проблема:** Разные названия поля для гостей в request vs response.

- **api-contracts.md (строка 351):** Request body использует `"guests": [...]`
- **api-contracts.md (строка 322):** Response использует `"guests_planned": [...]`
- **data-model.md (строка 78):** Поле называется `guests_planned`

**Исправление:** Добавить комментарий в api-contracts.md что `guests` в request маппится на `guests_planned` в response

---

### 12. МЕЛКИЕ: Inconsistent enum values casing

**Проблема:** Разный регистр в enum значениях.

- **api-contracts.md:** `"cancelled"` (lowercase)
- **screenflow.md (строка 266):** "cancelled" (lowercase) — OK
- **data-model.md:** Все lowercase — OK

**Исправление:** Нет ошибки, всё консистентно

---

### 13. МЕЛКИЕ: Missing query parameters в GET /tariffs

**Проблема:** В api-contracts.md GET /tariffs не имеет query parameters, но screenflow не описывает пагинацию для тарифов.

- **api-contracts.md (строка 430-456):** Response `PaginatedResponse<TariffResponse>` — но нет query params
- **screenflow.md:** Не упоминает пагинацию для тарифов

**Исправление:** Добавить query parameters (limit, offset, sort) в api-contracts.md для GET /tariffs

---

### 14. МЕЛКИЕ: House capacity description

**Проблема:** Разные описания capacity.

- **data-model.md (строка 61):** "Максимальная вместимость (гостей)"
- **screenflow.md (строка 131):** "X гостей"
- **api-contracts.md:** Без описания единиц

**Исправление:** Унифицировать описания — добавить "гостей" в api-contracts.md

---

## План исправлений

### Phase 1: Критические исправления (блокирующие разработку)

1. **api-contracts.md** — Исправить фильтр `user_id` → `tenant_id` для GET /bookings
2. **api-contracts.md** — Исправить единицы измерения `total_amount` с рублей на копейки
3. **api-contracts.md** — Исправить единицы измерения `tariff.amount` с рублей на копейки
4. **api-contracts.md** — Добавить endpoint `GET /chats/user/{user_id}`
5. **api-contracts.md** — Добавить endpoint `GET /users/telegram/{telegram_username}`

### Phase 2: Важные исправления (улучшение консистентности)

6. **api-contracts.md** — Унифицировать описание методов отмены бронирования (PATCH vs /cancel)
7. **api-contracts.md** — Добавить `DELETE /houses/{id}`
8. **api-contracts.md** — Добавить `DELETE /tariffs/{id}`
9. **api-contracts.md** — Добавить комментарий про маппинг `guests` → `guests_planned`
10. **data-model.md** — Исправить описание чата с "несколько" на "один"
11. **api-contracts.md** — Добавить query parameters для GET /tariffs
12. **api-contracts.md** — Добавить единицы измерения для house.capacity

### Phase 3: Средние и мелкие улучшения

13. **chatflow.md** — Добавить intents для CRUD домов (опционально)
14. **api-contracts.md** — Добавить пояснение про cursor-based пагинацию для chat messages
15. **Все файлы** — Проверить консистентность enum значений

### Phase 4: Финальная валидация

16. Прочитать все исправленные файлы и проверить что все cross-reference'ы консистентны
17. Составить summary внесённых изменений

---

## Актуализация документов на основе фактического backend кода

### A. КРИТИЧЕСКИЕ: Несоответствия схем данных

#### A1. total_amount единицы измерения в schemas

**Проблема:** В backend schemas rubles, в data-model.md kopecks.

- **backend/schemas/booking.py (строка 64):** `description="Total amount in rubles"`
- **data-model.md (строка 80, 215):** "в копейках"
- **Реальная реализация:** rubles (backend код - источник правды)

**Исправление:** 
- data-model.md строка 80 — изменить на "в рублях"
- data-model.md строка 215 — изменить на "рубли"
- api-contracts.md строка 540 — оставить "в рублях" (уже правильно)

---

#### A2. tariff.amount единицы измерения в schemas

**Проблема:** Backend schemas rubles, data-model.md kopecks.

- **backend/schemas/tariff.py (строка 21):** `description="Price per night in rubles (0 for free)"`
- **data-model.md (строка 93, 232):** "в копейках"
- **Реальная реализация:** rubles (backend код - источник правды)

**Исправление:**
- data-model.md строка 93 — изменить на "в рублях"
- data-model.md строка 232 — изменить на "рубли"
- api-contracts.md строка 557 — оставить "в рублях" (уже правильно)

---

### B. ВАЖНЫЕ: Missing/Extra endpoints

#### B1. Endpoint GET /chats/user/{user_id} НЕ нужен

**Проблема:** План предлагает добавить endpoint, но он не реализован в backend.

- **План (строка 31-39):** Предлагает добавить `GET /chats/user/{user_id}`
- **backend/api/chat.py:** Отсутствует такой endpoint
- **Реальная логика:** Frontend сам управляет chat_id, нет авто-создания

**Исправление:**
- УДАЛИТЬ из плана добавление `GET /chats/user/{user_id}`
- screenflow.md строка 806 — изменить логику: frontend хранит chat_id в localStorage/state
- chatflow.md строка 376 — удалить ссылку на этот endpoint

---

#### B2. Endpoint GET /users/telegram/{username} — переименовать

**Проблема:** Backend использует telegram_id, не username.

- **screenflow.md (строка 91):** `GET /users/telegram/{username}`
- **backend/schemas/user.py (строка 34, 44):** поле `telegram_id: str`
- **backend/api/users.py:** Отсутствует endpoint поиска по telegram
- **Реальная логика:** Пользователь создается через POST /users с telegram_id

**Исправление:**
- screenflow.md строка 91 — изменить на "POST /users если пользователя нет, иначе GET /users/{id}"
- НЕ добавлять endpoint `GET /users/telegram/{username}` (не нужен)
- Добавить в api-contracts.md примечание что telegram_id используется для авторизации

---

#### B3. Booking cancel метод — только PATCH

**Проблема:** В backend нет отдельного endpoint /cancel.

- **backend/api/bookings.py (строка 178-220):** Только `DELETE /bookings/{booking_id}` для отмены
- **План (строка 57-68):** Предлагает оба варианта PATCH и /cancel
- **Реальная реализация:** DELETE endpoint с soft delete (status=cancelled)

**Исправление:**
- УДАЛИТЬ из плана упоминание PATCH /bookings/{id}/cancel
- api-contracts.md строка 373-403 — удалить пример PATCH с status: "cancelled"
- screenflow.md строка 286 — изменить на `DELETE /bookings/{id}`
- chatflow.md строка 86 — изменить на `DELETE /bookings/{id}`

---

#### B4. Houses DELETE — hard delete не soft

**Проблема:** Реализация удаляет дом полностью.

- **backend/api/houses.py (строка 200-226):** `DELETE /houses/{house_id}` с status 204
- **screenflow.md (строка 522):** `DELETE /houses/{id}` — правильно
- **data-model.md:** Нет поля is_deleted или deleted_at

**Исправление:** 
- api-contracts.md — добавить `DELETE /houses/{id}` как hard delete
- document в api-contracts.md что удаление необратимо

---

### C. СРЕДНИЕ: Field naming inconsistencies

#### C1. BookingFilterParams использует user_id

**Проблема:** Backend filter параметр называется user_id, не tenant_id.

- **backend/schemas/booking.py (строка 124):** `user_id: Optional[int] = Field(None, description="Filter by tenant ID")`
- **План (строка 7-14):** Предлагает tenant_id
- **data-model.md:** Поле в таблице bookings называется tenant_id
- **Реальная реализация:** user_id (query param name), но description говорит "tenant ID"

**Исправление:**
- ОСТАВИТЬ user_id в api-contracts.md (соответствует backend)
- screenflow.md строка 277 — изменить на `user_id={current_user_id}`
- chatflow.md строка 65 — изменить на `user_id={user_id}`
- Добавить комментарий что user_id фильтрует по tenant_id в БД

---

#### C2. guests → guests_planned mapping

**Проблема:** Request/Response field names разные.

- **backend/schemas/booking.py (строка 76):** Request `guests: List[GuestInfo]`
- **backend/schemas/booking.py (строка 53):** Response `guests_planned: List[GuestInfo]`
- **Реальная реализация:** guests в request → guests_planned в response

**Исправление:**
- api-contracts.md — добавить явное примечание о маппинге
- Это правильное поведение, не ошибка

---

### D. МЕЛКИЕ: Documentation gaps

#### D1. Tariffs pagination query params

**Проблема:** Backend реализует pagination, но не через Depends().

- **backend/api/tariffs.py (строка 29-31):** `limit: int = 20, offset: int = 0, sort: str = "id"`
- **План (строка 158-165):** Правильно предлагает добавить query params
- **Реальная реализация:** query params есть, но не документированы

**Исправление:**
- api-contracts.md — добавить query parameters для GET /tariffs: limit, offset, sort

---

#### D2. Chat messages cursor pagination

**Проблема:** Backend использует cursor pagination для chat messages.

- **backend/api/chat.py (строка 77-78):** `cursor: str | None = None, limit: int = 50`
- **backend/schemas/chat.py (строка 45-50):** `ChatMessagesListResponse` с cursor и has_more
- **Реальная реализация:** cursor-based pagination

**Исправление:**
- api-contracts.md — добавить пояснение почему cursor-based (для real-time чата)
- Это feature, не баг

---

#### D3. Auth placeholder (tenant_id=1, user_id=1, owner_id=1)

**Проблема:** Hardcoded user IDs в endpoint'ах.

- **backend/api/bookings.py (строка 106, 156, 202):** `tenant_id: int = 1`
- **backend/api/houses.py (строка 118):** `owner_id = 1`
- **backend/api/chat.py (строка 76, 129):** `user_id: int = 1`
- **Реальная реализация:** Временные заглушки до внедрения auth

**Исправление:**
- Добавить TODO комментарий во все spec файлы что auth будет позже
- api-contracts.md — пометить что tenant_id/user_id временно query params с default=1

---

#### D4. House PUT vs PATCH

**Проблема:** Backend поддерживает оба метода.

- **backend/api/houses.py (строка 122-157):** `PUT /{house_id}` — full replace
- **backend/api/houses.py (строка 160-197):** `PATCH /{house_id}` — partial update
- **screenflow.md:** Упоминает только PATCH

**Исправление:**
- api-contracts.md — документировать оба метода (PUT и PATCH)
- screenflow.md — добавить примечание про PUT для полного обновления

---

## ОБНОВЛЕННЫЙ План исправлений

### Phase 1: Критические исправления (блокирующие разработку)

#### 1.1 data-model.md — Исправить total_amount: "копейки" → "рубли"

**Файлы:** `docs/data-model.md` строки 80, 215

**Изменения:**
- Строка 80: изменить описание total_amount с "в копейках" на "в рублях"
- Строка 215: изменить описание total_amount с "Итоговая сумма (копейки)" на "Итоговая сумма (рубли)"

**DoD (self-checked):**
- [ ] Найти все упоминания total_amount в data-model.md
- [ ] Проверить что изменено на "рубли" в обоих местах
- [ ] Убедиться что соответствует backend/schemas/booking.py:64
- [ ] Проверить что нет других противоречий с единицами измерения

---

#### 1.2 data-model.md — Исправить tariff.amount: "копейки" → "рубли"

**Файлы:** `docs/data-model.md` строки 93, 232

**Изменения:**
- Строка 93: изменить описание amount с "в копейках" на "в рублях"
- Строка 232: изменить описание amount с "Стоимость (копейки)" на "Стоимость (рубли)"

**DoD (self-checked):**
- [ ] Найти все упоминания tariff.amount в data-model.md
- [ ] Проверить что изменено на "рубли" в обоих местах
- [ ] Убедиться что соответствует backend/schemas/tariff.py:21
- [ ] Проверить консистентность с api-contracts.md

---

#### 1.3 api-contracts.md — Исправить фильтр bookings: user_id фильтрует tenant_id

**Файлы:** `docs/tech/api-contracts.md` строка 294

**Изменения:**
- Добавить комментарий что параметр `user_id` фильтрует по полю `tenant_id` в БД
- Пример: `- user_id (integer, optional) — фильтр по арендатору (соответствует tenant_id в БД)`

**DoD (self-checked):**
- [ ] Проверить что user_id оставлен как имя параметра API
- [ ] Добавить пояснение про tenant_id в БД
- [ ] Убедиться что соответствует backend/schemas/booking.py:124
- [ ] Проверить что screenflow.md и chatflow.md исправлены на user_id

---

#### 1.4 screenflow.md — Исправить фильтр bookings: tenant_id → user_id

**Файлы:** `docs/specs/screenflow.md` строка 277

**Изменения:**
- Строка 277: изменить `GET /bookings?tenant_id={current_user_id}` на `GET /bookings?user_id={current_user_id}`

**DoD (self-checked):**
- [ ] Найти все упоминания tenant_id в URL query params
- [ ] Заменить на user_id
- [ ] Проверить что соответствует api-contracts.md
- [ ] Проверить что нет других мест с tenant_id в query params

---

#### 1.5 chatflow.md — Исправить фильтр bookings: tenant_id → user_id

**Файлы:** `docs/specs/chatflow.md` строка 65

**Изменения:**
- Строка 65: изменить `GET /bookings?tenant_id={user_id}` на `GET /bookings?user_id={user_id}`

**DoD (self-checked):**
- [ ] Найти все упоминания tenant_id в URL query params
- [ ] Заменить на user_id
- [ ] Проверить что соответствует api-contracts.md
- [ ] Проверить консистентность с screenflow.md

**Артефакты:**
- Создать `docs/tasks/task-10-spec-consistency/plan.md` с описанием всех исправлений
- Создать `docs/tasks/task-10-spec-consistency/summary.md` после выполнения

---

### Phase 2: Важные исправления (логика endpoint'ов)

#### 2.1 api-contracts.md — Удалить упоминание PATCH /bookings/{id}/cancel

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Удалить секцию с endpoint PATCH /bookings/{id}/cancel
- Оставить только DELETE /bookings/{id} для отмены

**DoD (self-checked):**
- [ ] Найти все упоминания /cancel в api-contracts.md
- [ ] Удалить секцию PATCH /bookings/{id}/cancel
- [ ] Проверить что DELETE /bookings/{id} документирован
- [ ] Убедиться что соответствует backend/api/bookings.py:178-220

---

#### 2.2 api-contracts.md — Добавить DELETE /bookings/{id} для отмены

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить endpoint DELETE /bookings/{booking_id}
- Response: 200 OK с BookingResponse (soft delete: status=cancelled)
- Error responses: 404, 403, 400

**DoD (self-checked):**
- [ ] Добавить полную документацию endpoint
- [ ] Проверить что соответствует backend/api/bookings.py:178-220
- [ ] Проверить что статусы ошибок совпадают
- [ ] Указать что это soft delete (status=cancelled)

---

#### 2.3 screenflow.md — Исправить отмену бронирования: PATCH → DELETE

**Файлы:** `docs/specs/screenflow.md` строка 286

**Изменения:**
- Строка 286: изменить `PATCH /bookings/{id}` с `status: "cancelled"` на `DELETE /bookings/{id}`

**DoD (self-checked):**
- [ ] Найти все упоминания отмены бронирования
- [ ] Заменить PATCH на DELETE
- [ ] Убрать body с status: "cancelled"
- [ ] Проверить что соответствует backend/api/bookings.py

---

#### 2.4 chatflow.md — Исправить отмену бронирования: PATCH → DELETE

**Файлы:** `docs/specs/chatflow.md` строка 86

**Изменения:**
- Строка 86: изменить `PATCH /bookings/{id}` с `status: cancelled` на `DELETE /bookings/{id}`

**DoD (self-checked):**
- [ ] Найти все упоминания отмены бронирования в chatflow.md
- [ ] Заменить PATCH на DELETE
- [ ] Проверить что соответствует api-contracts.md
- [ ] Проверить консистентность с screenflow.md

---

#### 2.5 api-contracts.md — Добавить DELETE /houses/{id}

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить endpoint DELETE /houses/{house_id}
- Response: 204 No Content (hard delete)
- Error responses: 404

**DoD (self-checked):**
- [ ] Добавить полную документацию endpoint
- [ ] Проверить что соответствует backend/api/houses.py:200-226
- [ ] Указать что это hard delete (необратимо)
- [ ] Проверить status code 204

---

#### 2.6 api-contracts.md — Добавить DELETE /tariffs/{id}

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить endpoint DELETE /tariffs/{tariff_id}
- Response: 204 No Content
- Error responses: 404

**DoD (self-checked):**
- [ ] Добавить полную документацию endpoint
- [ ] Проверить что соответствует backend/api/tariffs.py:160-186
- [ ] Проверить status code 204
- [ ] Проверить error responses

---

#### 2.7 api-contracts.md — Добавить PUT /houses/{id} (full replace)

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить endpoint PUT /houses/{house_id}
- Request body: CreateHouseRequest (полная замена)
- Response: 200 OK с HouseResponse

**DoD (self-checked):**
- [ ] Добавить полную документацию endpoint
- [ ] Проверить что соответствует backend/api/houses.py:122-157
- [ ] Указать что это full replace (все поля обязательны)
- [ ] Проверить что отличается от PATCH (partial update)

---

#### 2.8 api-contracts.md — Добавить PUT /users/{id} (full replace)

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить endpoint PUT /users/{user_id}
- Request body: CreateUserRequest (полная замена)
- Response: 200 OK с UserResponse

**DoD (self-checked):**
- [ ] Добавить полную документацию endpoint
- [ ] Проверить что соответствует backend/api/users.py:118-153
- [ ] Указать что это full replace
- [ ] Проверить что отличается от PATCH

---

#### 2.9 api-contracts.md — Добавить DELETE /users/{id}

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить endpoint DELETE /users/{user_id}
- Response: 204 No Content
- Error responses: 404

**DoD (self-checked):**
- [ ] Добавить полную документацию endpoint
- [ ] Проверить что соответствует backend/api/users.py:196-222
- [ ] Проверить status code 204
- [ ] Проверить error responses

---

#### 2.10 screenflow.md — Исправить авторизацию: удалить GET /users/telegram/{username}

**Файлы:** `docs/specs/screenflow.md` строка 91

**Изменения:**
- Строка 91: изменить логику авторизации
- Было: `GET /users/telegram/{username}`
- Стало: "Проверка localStorage → если нет пользователя: POST /users с telegram_id, иначе GET /users/{id}"

**DoD (self-checked):**
- [ ] Найти все упоминания /users/telegram/
- [ ] Удалить или заменить на корректную логику
- [ ] Описать что telegram_id передается в POST /users
- [ ] Проверить что нет такого endpoint в api-contracts.md

**Артефакты:**
- Обновить `docs/tasks/task-10-spec-consistency/plan.md` с Phase 2
- Обновить `docs/tasks/task-10-spec-consistency/summary.md` с результатами

---

### Phase 3: Средние улучшения (консистентность)

#### 3.1 api-contracts.md — Добавить маппинг guests → guests_planned

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить примечание в секцию POST /bookings
- "Поле `guests` в request маппится на `guests_planned` в response"

**DoD (self-checked):**
- [ ] Найти секцию POST /bookings request body
- [ ] Добавить комментарий про маппинг
- [ ] Проверить что соответствует backend/schemas/booking.py:76,53
- [ ] Убедиться что понятно для разработчика

---

#### 3.2 api-contracts.md — Добавить query params для GET /tariffs

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить query parameters:
  - `limit` (integer, default: 20)
  - `offset` (integer, default: 0)
  - `sort` (string, default: "id")

**DoD (self-checked):**
- [ ] Найти GET /tariffs endpoint
- [ ] Добавить секцию Query Parameters
- [ ] Проверить что соответствует backend/api/tariffs.py:29-31
- [ ] Проверить default значения

---

#### 3.3 api-contracts.md — Добавить пояснение про cursor pagination для chat messages

**Файлы:** `docs/tech/api-contracts.md`

**Изменения:**
- Добавить примечание в GET /chats/{id}/messages
- "Используется cursor-based пагинация для поддержки real-time обновлений чата"

**DoD (self-checked):**
- [ ] Найти GET /chats/{id}/messages endpoint
- [ ] Добавить пояснение про cursor pagination
- [ ] Проверить что соответствует backend/api/chat.py:77-78
- [ ] Проверить что ChatMessagesListResponse использует cursor/has_more

---

#### 3.4 data-model.md — Исправить описание чата: "несколько" → "один"

**Файлы:** `docs/data-model.md` строка 107

**Изменения:**
- Строка 107: изменить "Каждый пользователь может иметь несколько чатов" на "Каждый пользователь имеет один чат с ассистентом"

**DoD (self-checked):**
- [ ] Найти описание Chat entity
- [ ] Изменить описание cardinality
- [ ] Проверить что соответствует screenflow.md:768
- [ ] Проверить что соответствует chatflow.md:15

---

#### 3.5 Все spec файлы — Добавить TODO про auth заглушки

**Файлы:** Все spec документы

**Изменения:**
- Добавить примечание что tenant_id=1, user_id=1, owner_id=1 — временные заглушки
- "TODO: До внедрения authentication user ID передаются как query params с default=1"

**DoD (self-checked):**
- [ ] Добавить TODO в api-contracts.md
- [ ] Добавить TODO в screenflow.md
- [ ] Добавить TODO в chatflow.md
- [ ] Перечислить все endpoint'ы с заглушками

---

#### 3.6 screenflow.md — Добавить примечание про PUT endpoints

**Файлы:** `docs/specs/screenflow.md`

**Изменения:**
- Добавить примечание в секции House Management и User Profile
- "Для полного обновления всех полей используется PUT /{id}, для частичного — PATCH /{id}"

**DoD (self-checked):**
- [ ] Найти секцию House Management
- [ ] Добавить примечание про PUT vs PATCH
- [ ] Найти секцию User Profile
- [ ] Добавить аналогичное примечание

**Артефакты:**
- Обновить `docs/tasks/task-10-spec-consistency/plan.md` с Phase 3
- Обновить `docs/tasks/task-10-spec-consistency/summary.md` с результатами
- Добавить checklist всех проверенных cross-reference'ов

---

### Phase 4: Финальная валидация

#### 4.1 Cross-reference validation

**Задача:** Проверить все ссылки между spec документами и backend кодом

**DoD (self-checked):**
- [ ] Прочитать все исправленные spec файлы целиком
- [ ] Проверить что все endpoint'ы в spec существуют в backend/api/
- [ ] Проверить что все request/response schemas соответствуют backend/schemas/
- [ ] Проверить что нет орфанных ссылок на несуществующие endpoint'ы
- [ ] Проверить консистентность field names across all docs
- [ ] Проверить консистентность units (rubles vs kopecks)
- [ ] Проверить что enum values одинаковые везде

---

#### 4.2 Backend code audit

**Задача:** Проверить что backend код соответствует spec'ам

**DoD (self-checked):**
- [ ] Пройтись по всем backend/api/*router.py файлам
- [ ] Сверить каждый endpoint с api-contracts.md
- [ ] Проверить что все documented endpoints реализованы
- [ ] Проверить что status codes совпадают
- [ ] Проверить что request/response models соответствуют schemas
- [ ] Составить список любых remaining discrepancies

---

#### 4.3 Создать финальные артефакты

**Файлы для создания:**
- `docs/tasks/task-10-spec-consistency/summary.md` — полный отчет о всех изменениях
- Обновить `docs/tasks/task-10-spec-consistency/plan.md` — финальная версия с результатами

**Содержание summary.md:**
- Список всех исправленных файлов
- Количество изменений по категориям (Critical/Important/Medium)
- Список оставшихся TODO (auth заглушки)
- Рекомендации для будущих итераций

**DoD (self-checked):**
- [ ] Создать summary.md с полным описанием изменений
- [ ] Приложить примеры before/after для ключевых изменений
- [ ] Указать все файлы которые были изменены
- [ ] Добавить секцию "Lessons Learned"
- [ ] Проверить что plan.md обновлен статусами всех задач

---

## Общие артефакты по задаче

### Структура задачи

Создать по аналогии с task-09-text-to-sql:

```
docs/tasks/task-10-spec-consistency/
├── plan.md          # Детальный план всех исправлений (этот файл)
└── summary.md       # Отчет о выполненных изменениях
```

### summary.md шаблон (создать после выполнения)

```markdown
# Task 10: Spec Consistency Fix Summary

## Completed Work

### Phase 1: Critical Fixes
- Исправлено X файлов
- Изменено Y строк
- Единицы измерения: kopecks → rubles (data-model.md)
- Filter naming: tenant_id → user_id (screenflow.md, chatflow.md)

### Phase 2: Endpoint Logic
- Удалено: PATCH /bookings/{id}/cancel
- Добавлено: DELETE endpoints для bookings, houses, tariffs, users
- Добавлено: PUT endpoints для houses, users
- Исправлена логика авторизации в screenflow.md

### Phase 3: Consistency Improvements
- Добавлен маппинг guests → guests_planned
- Добавлены query params для GET /tariffs
- Добавлено пояснение cursor pagination
- Исправлено описание chat cardinality
- Добавлены TODO про auth заглушки

### Files Modified
1. docs/data-model.md — X changes
2. docs/tech/api-contracts.md — X changes
3. docs/specs/screenflow.md — X changes
4. docs/specs/chatflow.md — X changes

### Validation Results
- Cross-reference check: PASSED/FAILED
- Backend code audit: PASSED/FAILED
- Remaining discrepancies: [список если есть]

## Lessons Learned
- [Описание извлеченных уроков]
## Recommendations
- [Рекомендации для будущих итераций]
```
