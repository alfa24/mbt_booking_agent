# API Contracts

Документация REST API контрактов системы бронирования загородного жилья.

## Базовая информация

- **Base URL:** `/api/v1`
- **Формат:** JSON
- **Версионирование:** URL-based (`/api/v1/`)

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
  ],
  "status": "cancelled"
}
```

**Response:** `BookingResponse`

**Errors:**
- 404 — бронирование не найдено
- 422 — невалидные данные
- 409 — конфликт дат

---

#### PATCH /bookings/{id}/cancel

Отмена бронирования. Статус меняется на `cancelled`.

**Path Parameters:**
- `id` (integer, required)

**Request Body:** None

**Response:** `BookingResponse`

```json
{
  "id": 1,
  "status": "cancelled",
  ...
}
```

**Errors:**
- 404 — бронирование не найдено
- 409 — бронирование уже отменено или завершено

### Tariffs

#### GET /tariffs

Справочник тарифов.

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

Спецификация OpenAPI (JSON):
```
http://localhost:8000/openapi.json
```
