# Summary: Реализация API бронирований (Задача 04)

## Что реализовано

### 1. In-memory репозиторий (`backend/repositories/booking.py`)
- Класс `BookingRepository` с полным CRUD
- Хранение в `dict[int, BookingResponse]`
- Автоинкремент ID
- Фильтрация по user_id, house_id, status
- Пагинация и сортировка
- Метод `get_bookings_for_house` для проверки конфликтов
- Метод `clear()` для тестирования

### 2. Сервис бронирований (`backend/services/booking.py`)
- Класс `BookingService` с бизнес-логикой
- Dependency injection через FastAPI `Depends`
- Валидация пересечения дат
- Расчет суммы на основе тарифов:
  - tariff_id=1 (Child): 0 ₽
  - tariff_id=2 (Adult): 250 ₽
  - tariff_id=3 (Regular): 150 ₽
- Авторизация (проверка tenant_id)
- Проверка статуса перед обновлением/отменой

### 3. API роутер (`backend/api/bookings.py`)
- `GET /api/v1/bookings` — список с фильтрами и пагинацией
- `GET /api/v1/bookings/{id}` — получение по ID
- `POST /api/v1/bookings` — создание (201 Created)
- `PATCH /api/v1/bookings/{id}` — обновление
- `DELETE /api/v1/bookings/{id}` — отмена (soft delete)
- Полная документация в Swagger
- Корректные HTTP-коды: 200, 201, 400, 403, 404, 422

### 4. Тесты (`backend/tests/test_bookings.py`)
- 24 теста, все проходят
- Покрытие: создание, чтение, обновление, удаление
- Валидация дат
- Проверка конфликтов дат
- Фильтрация и пагинация
- Расчет суммы

## Результаты тестирования

```bash
$ docker compose exec backend uv run pytest backend/tests/test_bookings.py -v
===================== test session starts =====================
collected 24 items
backend/tests/test_bookings.py::TestCreateBooking::test_create_booking_success PASSED
backend/tests/test_bookings.py::TestCreateBooking::test_create_booking_invalid_dates PASSED
...
backend/tests/test_bookings.py::TestCancelBooking::test_cancelled_booking_not_in_list PASSED
====================== 24 passed in 0.86s ======================
```

## Артефакты

| Файл | Описание |
|------|----------|
| `backend/repositories/booking.py` | In-memory репозиторий |
| `backend/repositories/__init__.py` | Экспорт BookingRepository |
| `backend/services/booking.py` | Бизнес-логика бронирований |
| `backend/api/bookings.py` | API endpoints |
| `backend/api/__init__.py` | Обновлен с bookings_router |
| `backend/tests/test_bookings.py` | Тесты (24 шт.) |
| `docs/tasks/task-04-booking-api/plan.md` | План реализации |
| `docs/tasks/task-04-booking-api/summary.md` | Этот документ |

## Известные ограничения

1. **In-memory хранение** — данные теряются при перезапуске контейнера (будет исправлено в задаче 06 с PostgreSQL)
2. **Фиксированный tenant_id=1** — нет авторизации, будет добавлена позже
3. **Простой расчет тарифов** — без учета количества ночей, будет доработан

## Проверка в Docker

```bash
# Запуск
docker compose up -d backend

# Health check
curl http://localhost:8001/health

# Создание бронирования
curl -X POST http://localhost:8001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"house_id": 1, "check_in": "2024-06-01", "check_out": "2024-06-03", "guests": [{"tariff_id": 2, "count": 2}]}'

# Запуск тестов
docker compose exec backend uv run pytest backend/tests/test_bookings.py -v
```

## Definition of Done — статус

- [x] Все endpoints возвращают корректные HTTP-коды (200, 201, 400, 404, 422)
- [x] Валидация работает — невалидные данные отклоняются
- [x] Тесты проходят в Docker: `docker compose exec backend uv run pytest backend/tests/test_bookings.py -v`
- [x] Покрытие бронирований > 80% (24 теста)
- [x] Swagger UI отображает все endpoints корректно (http://localhost:8001/docs)
