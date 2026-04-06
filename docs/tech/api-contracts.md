# API Contracts

Документация REST API контрактов системы бронирования загородного жилья.

## Базовая информация

- **Base URL:** `/api/v1`
- **Формат:** JSON
- **Версионирование:** URL-based (`/api/v1/`)

## Примечание об аутентификации

> **TODO:** До внедрения полноценной аутентификации user ID передаются как query parameters с default=1:
> - `tenant_id=1` — для endpoints бронирований
> - `user_id=1` — для endpoints чатов
> - `owner_id=1` — для endpoints домов
> 
> После внедрения auth эти параметры будут передаваться через заголовки авторизации (JWT token).

## Общие схемы

### ErrorResponse

Стандартный формат ошибки:

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [
    {
      "field": "check_in",
      "msg": "must be in the future",
      "type": "value_error"
    }
  ]
}
```

**Поля:**
- `error` (string) — код ошибки
- `message` (string) — человекочитаемое описание
- `details` (array, optional) — детали валидации

### PaginatedResponse

Generic-обёртка для пагинированных списков:

```json
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

**Поля:**
- `items` (array) — элементы текущей страницы
- `total` (integer) — общее количество
- `limit` (integer) — элементов на страницу
- `offset` (integer) — пропущено элементов

## Коды ошибок

| Код | HTTP Status | Описание |
|-----|-------------|----------|
| `validation_error` | 422 | Ошибка валидации входных данных |
| `not_found` | 404 | Ресурс не найден |
| `conflict` | 409 | Конфликт (например, даты заняты) |
| `internal_error` | 500 | Внутренняя ошибка сервера |

## Endpoints

### Users

#### GET /users

Список пользователей.

**Query Parameters:**
- `limit` (integer, optional) — default: 20, max: 100
- `offset` (integer, optional) — default: 0
- `sort` (string, optional) — сортировка, формат: `field` или `-field` (desc). Пример: `created_at`, `-created_at`
- `role` (string, optional) — фильтр по роли: `tenant`, `owner`, `both`

**Response:** `PaginatedResponse<UserResponse>`

---

#### GET /users/{id}

Получение пользователя по ID.

**Path Parameters:**
- `id` (integer, required)

**Response:** `UserResponse`

**Errors:**
- 404 — пользователь не найден

---

#### POST /users

Создание пользователя (обычно из Telegram).

**Request Body:** `CreateUserRequest`

```json
{
  "telegram_id": "123456789",
  "name": "Иван Петров",
  "role": "tenant"
}
```

**Response:** `UserResponse` (201 Created)

**Errors:**
- 422 — невалидные данные

---

#### PUT /users/{id}

Полная замена профиля пользователя.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `CreateUserRequest` (все поля required)

```json
{
  "telegram_id": "123456789",
  "name": "Иван Иванов",
  "role": "both"
}
```

**Response:** `UserResponse`

**Errors:**
- 404 — пользователь не найден
- 422 — невалидные данные

---

#### PATCH /users/{id}

Частичное обновление профиля пользователя.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `UpdateUserRequest` (все поля optional)

```json
{
  "name": "Иван Иванов",
  "role": "both"
}
```

**Response:** `UserResponse`

**Errors:**
- 404 — пользователь не найден
- 422 — невалидные данные

---

#### DELETE /users/{id}

Удаление пользователя.

**Path Parameters:**
- `id` (integer, required)

**Response:** 204 No Content

**Errors:**
- 404 — пользователь не найден

### Houses

#### GET /houses

Список домов.

**Query Parameters:**
- `limit` (integer, optional) — default: 20, max: 100
- `offset` (integer, optional) — default: 0
- `sort` (string, optional) — сортировка, формат: `field` или `-field` (desc). Пример: `name`, `-created_at`
- `owner_id` (integer, optional) — фильтр по владельцу
- `is_active` (boolean, optional)
- `capacity_min` (integer, optional) — минимальная вместимость
- `capacity_max` (integer, optional) — максимальная вместимость

**Response:** `PaginatedResponse<HouseResponse>`

---

#### GET /houses/{id}

Детали дома.

**Path Parameters:**
- `id` (integer, required)

**Response:** `HouseResponse`

**Errors:**
- 404 — дом не найден

---

#### POST /houses

Создание дома (только для арендодателей).

**Request Body:** `CreateHouseRequest`

```json
{
  "name": "Старый дом",
  "description": "Уютный дом у озера",
  "capacity": 6,
  "is_active": true
}
```

**Response:** `HouseResponse` (201 Created)

---

#### PUT /houses/{id}

Полная замена информации о доме.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `CreateHouseRequest` (все поля required)

```json
{
  "name": "Старый дом",
  "description": "Уютный дом у озера",
  "capacity": 6,
  "is_active": true
}
```

**Response:** `HouseResponse`

**Errors:**
- 404 — дом не найден
- 422 — невалидные данные

---

#### PATCH /houses/{id}

Частичное обновление информации о доме.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `UpdateHouseRequest` (все поля optional)

**Response:** `HouseResponse`

**Errors:**
- 404 — дом не найден

---

#### DELETE /houses/{id}

Удаление дома (hard delete, необратимо).

**Path Parameters:**
- `id` (integer, required)

**Query Parameters:**
- `owner_id` (integer, required) — ID владельца для проверки прав (временно default=1)

**Response:** 204 No Content

**Errors:**
- 404 — дом не найден
- 403 — нет прав (не владелец дома)

---

#### GET /houses/{id}/calendar

Календарь доступности дома (занятые даты).

**Path Parameters:**
- `id` (integer, required)

**Query Parameters:**
- `from` (date, optional) — начало периода
- `to` (date, optional) — конец периода

**Response:** `HouseCalendarResponse`

```json
{
  "house_id": 1,
  "occupied_dates": [
    {
      "check_in": "2024-06-01",
      "check_out": "2024-06-03",
      "booking_id": 5
    }
  ]
}
```

### Bookings

#### GET /bookings

Список бронирований.

**Query Parameters:**
- `limit` (integer, optional) — default: 20, max: 100
- `offset` (integer, optional) — default: 0
- `sort` (string, optional) — сортировка, формат: `field` или `-field` (desc). Пример: `check_in`, `-created_at`
- `user_id` (integer, optional) — фильтр по арендатору
- `house_id` (integer, optional) — фильтр по дому
- `status` (string, optional) — фильтр по статусу: `pending`, `confirmed`, `cancelled`, `completed`
- `check_in_from` (date, optional) — заезд не раньше
- `check_in_to` (date, optional) — заезд не позже
- `check_out_from` (date, optional) — выезд не раньше
- `check_out_to` (date, optional) — выезд не позже

**Response:** `PaginatedResponse<BookingResponse>`

---

#### GET /bookings/{id}

Получение бронирования.

**Path Parameters:**
- `id` (integer, required)

**Response:** `BookingResponse`

```json
{
  "id": 1,
  "house_id": 1,
  "tenant_id": 2,
  "check_in": "2024-06-01",
  "check_out": "2024-06-03",
  "guests_planned": [
    {
      "tariff_id": 1,
      "count": 2
    }
  ],
  "guests_actual": null,
  "total_amount": 500,
  "status": "confirmed",
  "created_at": "2024-05-01T10:00:00Z"
}
```

**Errors:**
- 404 — бронирование не найдено

---

#### POST /bookings

Создание бронирования.

**Request Body:** `CreateBookingRequest`

```json
{
  "house_id": 1,
  "check_in": "2024-06-01",
  "check_out": "2024-06-03",
  "guests": [
    {
      "tariff_id": 1,
      "count": 2
    }
  ]
}
```

**Валидация:**
- `check_in` < `check_out`
- `guests` — минимум 1 элемент
- `count` >= 1

**Response:** `BookingResponse` (201 Created)

**Примечание:** Поле `guests` в request body маппится на `guests_planned` в response.

**Errors:**
- 422 — невалидные данные
- 409 — выбранные даты заняты

---

#### PATCH /bookings/{id}

Обновление бронирования (до подтверждения).

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `UpdateBookingRequest` (все поля optional)

```json
{
  "check_in": "2024-06-02",
  "check_out": "2024-06-05",
  "guests": [
    {
      "tariff_id": 1,
      "count": 3
    }
  ]
}
```

**Response:** `BookingResponse`

**Errors:**
- 404 — бронирование не найдено
- 422 — невалидные данные
- 409 — конфликт дат

---

#### DELETE /bookings/{id}

Отмена бронирования (soft delete). Статус меняется на `cancelled`.

**Path Parameters:**
- `id` (integer, required)

**Query Parameters:**
- `tenant_id` (integer, required) — ID арендатора для проверки прав (временно default=1)

**Response:** `BookingResponse` (200 OK)

```json
{
  "id": 1,
  "house_id": 1,
  "tenant_id": 123,
  "check_in": "2024-06-01",
  "check_out": "2024-06-05",
  "guests_planned": [{"tariff_id": 1, "count": 2}],
  "total_amount": 12000,
  "status": "cancelled",
  "created_at": "2024-05-20T10:00:00Z"
}
```

**Errors:**
- 404 — бронирование не найдено
- 403 — нет прав (не владелец бронирования)
- 400 — бронирование уже отменено или завершено

### Tariffs

#### GET /tariffs

Справочник тарифов.

**Query Parameters:**
- `limit` (integer, default: 20) — количество записей
- `offset` (integer, default: 0) — смещение
- `sort` (string, default: "id") — сортировка

**Response:** `PaginatedResponse<TariffResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "name": "Взрослый",
      "amount": 250,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Ребёнок",
      "amount": 0,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

---

#### GET /tariffs/{id}

Детали тарифа.

**Path Parameters:**
- `id` (integer, required)

**Response:** `TariffResponse`

**Errors:**
- 404 — тариф не найден

---

#### POST /tariffs

Создание тарифа (только для администраторов/арендодателей).

**Request Body:** `CreateTariffRequest`

```json
{
  "name": "Постоянный гость",
  "amount": 150
}
```

**Response:** `TariffResponse` (201 Created)

---

#### PATCH /tariffs/{id}

Обновление тарифа.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `UpdateTariffRequest` (все поля optional)

**Response:** `TariffResponse`

**Errors:**
- 404 — тариф не найден

---

#### PUT /tariffs/{id}

Полная замена тарифа.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `CreateTariffRequest`

```json
{
  "name": "Взрослый",
  "amount": 3000
}
```

**Response:** `TariffResponse`

**Errors:**
- 404 — тариф не найден

---

#### DELETE /tariffs/{id}

Удаление тарифа.

**Path Parameters:**
- `id` (integer, required)

**Response:** 204 No Content

**Errors:**
- 404 — тариф не найден
- 409 — тариф используется в бронированиях

## Справочник схем

### UserResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `telegram_id` | string | ID в Telegram |
| `name` | string | Имя для отображения |
| `role` | string | `tenant`, `owner`, `both` |
| `created_at` | datetime | Дата регистрации |

### HouseResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `name` | string | Название дома |
| `description` | string | Описание |
| `capacity` | integer | Максимальная вместимость |
| `is_active` | boolean | Доступен для бронирования |
| `owner_id` | integer | ID владельца |
| `created_at` | datetime | Дата создания |

### BookingResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `house_id` | integer | ID дома |
| `tenant_id` | integer | ID арендатора |
| `check_in` | date | Дата заезда |
| `check_out` | date | Дата выезда |
| `guests_planned` | array | Планируемый состав группы |
| `guests_actual` | array | Фактический состав (после проживания) |
| `total_amount` | integer | Итоговая сумма в рублях |
| `status` | string | `pending`, `confirmed`, `cancelled`, `completed` |
| `created_at` | datetime | Дата создания |

### GuestInfo

| Поле | Тип | Описание |
|------|-----|----------|
| `tariff_id` | integer | ID тарифа |
| `count` | integer | Количество гостей данного типа |

### TariffResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `name` | string | Название тарифа |
| `amount` | integer | Стоимость в рублях (0 = бесплатно) |
| `created_at` | datetime | Дата создания |

## OpenAPI / Swagger

Интерактивная документация доступна по адресу:
```
http://localhost:8000/docs
```

### Dashboard

#### GET /dashboard/owner

KPI и метрики для панели арендодателя.

**Query Parameters:**
- `period_from` (date, optional) — начало периода анализа
- `period_to` (date, optional) — конец периода анализа

**Response:** `OwnerDashboardResponse`

```json
{
  "total_bookings": 45,
  "total_revenue": 125000,
  "occupancy_rate": 78.5,
  "active_bookings": 8,
  "monthly_revenue": [
    {"month": "2024-01", "revenue": 25000},
    {"month": "2024-02", "revenue": 30000},
    {"month": "2024-03", "revenue": 35000},
    {"month": "2024-04", "revenue": 35000}
  ]
}
```

**Поля:**
- `total_bookings` (integer) — общее количество бронирований за период
- `total_revenue` (integer) — общая выручка в копейках
- `occupancy_rate` (float) — процент загрузки (0-100)
- `active_bookings` (integer) — количество активных (confirmed) бронирований
- `monthly_revenue` (array) — выручка по месяцам

---

#### GET /dashboard/leaderboard

Данные для страницы аналитики (лидерборд).

**Query Parameters:**
- `period_from` (date, optional) — начало периода
- `period_to` (date, optional) — конец периода

**Response:** `LeaderboardDashboardResponse`

```json
{
  "bookings_by_month": [
    {"month": "2024-01", "count": 10},
    {"month": "2024-02", "count": 12},
    {"month": "2024-03", "count": 15},
    {"month": "2024-04", "count": 8}
  ],
  "revenue_by_house": [
    {"house_id": 1, "house_name": "Старый дом", "revenue": 75000},
    {"house_id": 2, "house_name": "Новый дом", "revenue": 50000}
  ]
}
```

**Поля:**
- `bookings_by_month` (array) — количество бронирований по месяцам
- `revenue_by_house` (array) — выручка по домам

---

### Houses

#### GET /houses/{id}/stats

Статистика по конкретному дому за период.

**Path Parameters:**
- `id` (integer, required) — ID дома

**Query Parameters:**
- `period_from` (date, optional) — начало периода
- `period_to` (date, optional) — конец периода

**Response:** `HouseStatsResponse`

```json
{
  "house_id": 1,
  "house_name": "Старый дом",
  "occupancy_rate": 82.0,
  "total_revenue": 75000,
  "total_bookings": 25,
  "period_from": "2024-01-01",
  "period_to": "2024-04-01"
}
```

**Поля:**
- `house_id` (integer) — ID дома
- `house_name` (string) — название дома
- `occupancy_rate` (float) — процент загрузки
- `total_revenue` (integer) — выручка в копейках
- `total_bookings` (integer) — количество бронирований
- `period_from` (date) — начало периода
- `period_to` (date) — конец периода

**Errors:**
- 404 — дом не найден

---

### Consumable Notes

#### GET /consumable-notes

Список заметок о расходниках.

**Query Parameters:**
- `limit` (integer, optional) — default: 20, max: 100
- `offset` (integer, optional) — default: 0
- `house_id` (integer, optional) — фильтр по дому
- `sort` (string, optional) — сортировка, формат: `field` или `-field`

**Response:** `PaginatedResponse<ConsumableNoteResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "house_id": 1,
      "house_name": "Старый дом",
      "created_by": 2,
      "creator_name": "Иван Петров",
      "name": "Дрова",
      "comment": "Осталось 6 пачек",
      "created_at": "2024-04-01T10:00:00Z"
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

---

#### POST /consumable-notes

Создание заметки о расходниках.

**Request Body:** `CreateConsumableNoteRequest`

```json
{
  "house_id": 1,
  "name": "Дрова",
  "comment": "Осталось 6 пачек"
}
```

**Валидация:**
- `house_id` — существующий дом
- `name` — обязательное, max 100 символов
- `comment` — опциональное, max 1000 символов

**Response:** `ConsumableNoteResponse` (201 Created)

**Errors:**
- 422 — невалидные данные
- 404 — дом не найден

---

#### PATCH /consumable-notes/{id}

Обновление заметки.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** `UpdateConsumableNoteRequest` (все поля optional)

```json
{
  "name": "Дрова берёзовые",
  "comment": "Осталось 4 пачки"
}
```

**Response:** `ConsumableNoteResponse`

**Errors:**
- 404 — заметка не найдена
- 422 — невалидные данные

---

#### DELETE /consumable-notes/{id}

Удаление заметки.

**Path Parameters:**
- `id` (integer, required)

**Response:** 204 No Content

**Errors:**
- 404 — заметка не найдена

---

### Chats

#### POST /chats

Создание нового чата.

**Request Body:** `CreateChatRequest`

```json
{
  "title": "Вопрос о бронировании"
}
```

**Поля:**
- `title` (string, optional) — название чата, если не указано — генерируется автоматически

**Response:** `ChatResponse` (201 Created)

```json
{
  "id": 1,
  "title": "Вопрос о бронировании",
  "user_id": 2,
  "created_at": "2024-04-04T10:00:00Z",
  "updated_at": "2024-04-04T10:00:00Z"
}
```

**Автоприветствие:**
При создании чата автоматически отправляется первое сообщение от бота:
> "Привет! Я помощник по бронированию домов. Чем могу помочь?"

---

#### GET /chats/{id}/messages

История сообщений чата (cursor-based пагинация).

**Примечание:** Используется cursor-based пагинация вместо offset-based для поддержки real-time обновлений чата. Cursor позволяет эффективно загружать новые сообщения без пропусков и дубликатов.

**Path Parameters:**
- `id` (integer, required) — ID чата

**Query Parameters:**
- `cursor` (string, optional) — ID последнего полученного сообщения (для загрузки следующей порции)
- `limit` (integer, optional) — default: 50, max: 100

**Response:** `CursorPaginatedResponse<ChatMessageResponse>`

```json
{
  "items": [
    {
      "id": 101,
      "chat_id": 1,
      "role": "assistant",
      "content": "Привет! Я помощник по бронированию домов.",
      "created_at": "2024-04-04T10:00:00Z"
    },
    {
      "id": 102,
      "chat_id": 1,
      "role": "user",
      "content": "Какие дома свободны на выходные?",
      "created_at": "2024-04-04T10:05:00Z"
    }
  ],
  "next_cursor": "102",
  "has_more": false
}
```

**Поля:**
- `items` (array) — сообщения в порядке от старых к новым
- `next_cursor` (string, optional) — курсор для следующей страницы
- `has_more` (boolean) — есть ли ещё сообщения

**Errors:**
- 404 — чат не найден

---

#### POST /chats/{id}/messages

Отправка сообщения и получение ответа от LLM.

**Path Parameters:**
- `id` (integer, required) — ID чата

**Request Body:** `CreateChatMessageRequest`

```json
{
  "content": "Какие дома свободны на выходные?"
}
```

**Response:** `ChatMessageResponse`

```json
{
  "id": 103,
  "chat_id": 1,
  "role": "assistant",
  "content": "На ближайшие выходные (6-7 апреля) свободны:\n\n- Старый дом (до 6 человек)\n- Новый дом (до 4 человек)\n\nХотите забронировать?",
  "created_at": "2024-04-04T10:05:30Z"
}
```

**Логика работы:**
1. Сохраняет сообщение пользователя
2. Отправляет запрос к LLM с контекстом чата
3. Сохраняет ответ ассистента
4. Возвращает ответ ассистента

**Errors:**
- 404 — чат не найден
- 422 — пустое сообщение
- 500 — ошибка LLM-провайдера

---

## Справочник схем

### ConsumableNoteResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `house_id` | integer | ID дома |
| `house_name` | string | Название дома |
| `created_by` | integer | ID создателя |
| `creator_name` | string | Имя создателя |
| `name` | string | Название категории |
| `comment` | string | Описание остатков |
| `created_at` | datetime | Дата создания |

### ChatResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `title` | string | Название чата |
| `user_id` | integer | ID владельца чата |
| `created_at` | datetime | Дата создания |
| `updated_at` | datetime | Дата последнего обновления |

### ChatMessageResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `chat_id` | integer | ID чата |
| `role` | string | `user` или `assistant` |
| `content` | string | Текст сообщения |
| `created_at` | datetime | Дата отправки |

### CursorPaginatedResponse

| Поле | Тип | Описание |
|------|-----|----------|
| `items` | array | Элементы текущей страницы |
| `next_cursor` | string | Курсор для следующей страницы |
| `has_more` | boolean | Есть ли ещё данные |

---

## OpenAPI / Swagger

Интерактивная документация доступна по адресу:
```
http://localhost:8000/docs
```

Спецификация OpenAPI (JSON):
```
http://localhost:8000/openapi.json
```
