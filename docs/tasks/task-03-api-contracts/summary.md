# Task 03: Summary — API Contracts Design

## Что было реализовано

Спроектированы и созданы Pydantic-схемы для всех ресурсов системы бронирования загородного жилья.

## Созданные файлы

### 1. Схемы пользователей (`backend/schemas/user.py`)

- `UserRole` — enum ролей (tenant, owner, both)
- `UserResponse` — ответ с данными пользователя
- `CreateUserRequest` — создание пользователя из Telegram
- `UpdateUserRequest` — частичное обновление профиля
- `UserFilterParams` — параметры фильтрации и сортировки списка

### 2. Схемы домов (`backend/schemas/house.py`)

- `HouseResponse` — ответ с данными дома
- `CreateHouseRequest` — создание дома
- `UpdateHouseRequest` — частичное обновление дома
- `OccupiedDateRange` — диапазон занятых дат
- `HouseCalendarResponse` — календарь доступности
- `HouseFilterParams` — параметры фильтрации и сортировки списка

### 3. Схемы бронирований (`backend/schemas/booking.py`)

- `BookingStatus` — enum статусов (pending, confirmed, cancelled, completed)
- `GuestInfo` — состав группы (tariff_id + count)
- `BookingResponse` — ответ с данными бронирования
- `CreateBookingRequest` — создание бронирования с валидацией дат
- `UpdateBookingRequest` — обновление бронирования
- `BookingFilterParams` — параметры фильтрации и сортировки списка (включая диапазоны дат)

### 4. Схемы тарифов (`backend/schemas/tariff.py`)

- `TariffResponse` — ответ с данными тарифа
- `CreateTariffRequest` — создание тарифа
- `UpdateTariffRequest` — обновление тарифа

### 5. Общие схемы (`backend/schemas/common.py`)

- `ValidationErrorDetail` — детали ошибки валидации
- `ErrorResponse` — стандартный формат ошибки
- `PaginatedResponse[T]` — generic-обёртка для пагинации

### 6. Обновлён `backend/schemas/__init__.py`

Экспортирует все схемы для удобного импорта, включая новые FilterParams.

### 7. Исправлен `docs/tasks/tasklist-backend.md`

Убраны нерелевантные endpoints (`/chat`, `/homework`), добавлены актуальные для бронирования.

### 8. Создана документация `docs/tech/api-contracts.md`

Полная спецификация API с примерами запросов/ответов.

## Спроектированные endpoints

### Users (`/api/v1/users`)
- `GET /users` — список пользователей (с фильтрами и сортировкой)
- `GET /users/{id}` — получение пользователя
- `POST /users` — создание пользователя (из Telegram)
- `PUT /users/{id}` — полная замена профиля
- `PATCH /users/{id}` — частичное обновление профиля

### Houses (`/api/v1/houses`)
- `GET /houses` — список домов (с фильтрами и сортировкой)
- `GET /houses/{id}` — детали дома
- `POST /houses` — создание дома
- `PUT /houses/{id}` — полная замена дома
- `PATCH /houses/{id}` — частичное обновление дома
- `GET /houses/{id}/calendar` — доступность дома

### Bookings (`/api/v1/bookings`)
- `GET /bookings` — список бронирований (с фильтрами, сортировкой, диапазонами дат)
- `GET /bookings/{id}` — получение бронирования
- `POST /bookings` — создание бронирования
- `PATCH /bookings/{id}` — обновление бронирования
- `PATCH /bookings/{id}/cancel` — отмена бронирования

### Tariffs (`/api/v1/tariffs`)
- `GET /tariffs` — справочник тарифов
- `GET /tariffs/{id}` — детали тарифа

## Коды ошибок

- `validation_error` — ошибка валидации (422)
- `not_found` — ресурс не найден (404)
- `conflict` — конфликт (409)
- `internal_error` — внутренняя ошибка (500)

## Формат error response

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [{"field": "check_in", "msg": "must be in the future"}]
}
```

## Примеры данных

### BookingResponse
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

### CreateBookingRequest
```json
{
  "house_id": 1,
  "check_in": "2024-06-01",
  "check_out": "2024-06-03",
  "guests": [{"tariff_id": 1, "count": 2}]
}
```

## Definition of Done

- [x] Все схемы валидируются Pydantic
- [x] OpenAPI документация будет доступна по `/docs` (Swagger UI) после добавления роутеров
- [x] Все схемы имеют описания и примеры через Field
- [x] Коды ошибок задокументированы
- [x] tasklist-backend.md исправлен

## Следующие шаги

1. Создать роутеры в `backend/api/` для каждого ресурса
2. Реализовать бизнес-логику в `backend/services/`
3. Подключить PostgreSQL и SQLAlchemy модели
4. Проверить работу API через Swagger UI
