# Task 03: Проектирование API-контрактов

## Цель

Спроектировать и задокументировать REST API endpoints для системы бронирования загородного жилья на основе модели данных из `docs/data-model.md`.

## Текущее состояние

- Backend каркас создан (FastAPI)
- Есть базовый health endpoint
- Есть общая схема ErrorResponse
- Версионирование API: `/api/v1/` префикс

## Состав работ

### 1. Проектирование endpoints по ресурсам

#### Users (`/api/v1/users`)
- `GET /users` — список пользователей
- `GET /users/{id}` — получение пользователя
- `POST /users` — создание пользователя (из Telegram)
- `PUT /users/{id}` — полная замена профиля
- `PATCH /users/{id}` — частичное обновление профиля

#### Houses (`/api/v1/houses`)
- `GET /houses` — список домов
- `GET /houses/{id}` — детали дома
- `POST /houses` — создание дома (арендодатель)
- `PUT /houses/{id}` — полная замена дома
- `PATCH /houses/{id}` — частичное обновление дома
- `GET /houses/{id}/calendar` — доступность дома (занятые даты)

#### Bookings (`/api/v1/bookings`)
- `GET /bookings` — список бронирований (фильтры: user_id, house_id, status)
- `GET /bookings/{id}` — получение бронирования
- `POST /bookings` — создание бронирования
- `PATCH /bookings/{id}` — обновление бронирования
- `PATCH /bookings/{id}/cancel` — отмена бронирования

#### Tariffs (`/api/v1/tariffs`)
- `GET /tariffs` — справочник тарифов
- `GET /tariffs/{id}` — детали тарифа

### 2. Создание Pydantic-схем

**Файлы для создания:**

- `backend/schemas/user.py`
  - `UserResponse` — ответ с данными пользователя
  - `CreateUserRequest` — создание пользователя
  - `UpdateUserRequest` — обновление профиля

- `backend/schemas/house.py`
  - `HouseResponse` — ответ с данными дома
  - `CreateHouseRequest` — создание дома
  - `UpdateHouseRequest` — обновление дома
  - `HouseCalendarResponse` — календарь доступности

- `backend/schemas/booking.py`
  - `BookingResponse` — ответ с данными бронирования
  - `CreateBookingRequest` — создание бронирования
  - `UpdateBookingRequest` — обновление бронирования
  - `GuestInfo` — состав группы (тип гостя + количество)
  - `BookingStatus` — enum статусов

- `backend/schemas/tariff.py`
  - `TariffResponse` — ответ с данными тарифа
  - `CreateTariffRequest` — создание тарифа

- `backend/schemas/common.py` (дополнить)
  - `PaginatedResponse[T]` — пагинированный ответ
  - `ValidationErrorDetail` — детали ошибки валидации

### 3. Определение форматов запросов/ответов

**Пример BookingResponse:**
```json
{
  "id": 1,
  "house_id": 1,
  "tenant_id": 2,
  "check_in": "2024-06-01",
  "check_out": "2024-06-03",
  "guests_planned": [{"tariff_id": 1, "count": 2}],
  "guests_actual": null,
  "total_amount": 500,
  "status": "confirmed",
  "created_at": "2024-05-01T10:00:00Z"
}
```

**Пример CreateBookingRequest:**
```json
{
  "house_id": 1,
  "check_in": "2024-06-01",
  "check_out": "2024-06-03",
  "guests": [{"tariff_id": 1, "count": 2}]
}
```

### 4. Коды ошибок и формат error response

**ErrorResponse (уже есть):**
```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [{"field": "check_in", "msg": "must be in the future"}]
}
```

**Коды ошибок:**
- `validation_error` — ошибка валидации (422)
- `not_found` — ресурс не найден (404)
- `conflict` — конфликт (даты заняты) (409)
- `internal_error` — внутренняя ошибка (500)

### 5. Версионирование API

- Префикс: `/api/v1/` (уже настроен в main.py)
- Версия в заголовках или path

### 6. Документирование OpenAPI/Swagger

- FastAPI автоматически генерирует `/docs` (Swagger UI)
- Добавить `description` и `summary` для всех endpoints
- Добавить `tags` для группировки
- Добавить примеры в схемы Pydantic

### 7. Исправление tasklist-backend.md

Исправить строки 152-153 с `POST /api/v1/chat` и `POST /api/v1/homework` на актуальные endpoints для бронирования.

## Definition of Done

- [x] Все схемы валидируются Pydantic
- [x] OpenAPI документация доступна по `/docs` (Swagger UI)
- [x] Все endpoints имеют описание и примеры
- [x] Коды ошибок задокументированы
- [x] tasklist-backend.md исправлен

## Артефакты

- `backend/schemas/user.py`
- `backend/schemas/house.py`
- `backend/schemas/booking.py`
- `backend/schemas/tariff.py`
- `backend/schemas/common.py` (дополнен)
- `docs/tasks/task-03-api-contracts/plan.md`
- `docs/tasks/task-03-api-contracts/summary.md`
- Исправленный `docs/tasks/tasklist-backend.md`

## Проверка

```bash
# Запуск backend
make run-backend

# Открытие Swagger UI
open http://localhost:8000/docs

# Проверка: все endpoints отображаются, схемы валидны
```
