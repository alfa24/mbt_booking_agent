# План реализации API бронирований (Задача 04)

## Цель
Реализовать полноценный REST API для управления бронированиями с валидацией дат, проверкой пересечений и расчетом стоимости.

## Архитектура
- **In-memory хранение** — dict с счетчиком ID (для MVP, до подключения PostgreSQL в задаче 06)
- **Service Layer** — бизнес-логика отделена от роутеров
- **Repository Pattern** — абстракция над хранилищем

## Задачи

### 1. Создание in-memory репозитория
**Файл:** `backend/repositories/booking.py`
- Класс `BookingRepository` с методами: create, get, get_all, update, delete
- Хранение в `dict[int, BookingResponse]`
- Автоинкремент ID
- Фильтрация по user_id, house_id, status

### 2. Создание сервиса бронирований
**Файл:** `backend/services/booking.py`
- Класс `BookingService`
- Инжекция репозитория через Depends
- Методы: create_booking, get_booking, list_bookings, update_booking, cancel_booking
- Валидация пересечения дат при создании/обновлении
- Расчет суммы на основе тарифов (заглушка для MVP — фиксированная сумма)

### 3. Создание роутера бронирований
**Файл:** `backend/api/bookings.py`
- Роутер `bookings_router` с префиксом `/bookings`
- Endpoints:
  - `GET /bookings` — список с фильтрами и пагинацией
  - `GET /bookings/{id}` — получение по ID
  - `POST /bookings` — создание
  - `PATCH /bookings/{id}` — обновление
  - `DELETE /bookings/{id}` — отмена (soft delete — статус cancelled)
- Обработка ошибок 404, 422
- Интеграция с Swagger (докстринги, response_model)

### 4. Обновление API роутера
**Файл:** `backend/api/__init__.py`
- Добавить `bookings_router` в `api_router`

### 5. Создание тестов
**Файл:** `backend/tests/test_bookings.py`
- Тесты для всех endpoints (pytest + TestClient)
- Проверка валидации дат (check_in >= check_out)
- Проверка CRUD операций
- Проверка фильтрации
- Проверка 404 ошибки
- Целевое покрытие: >80%

### 6. Создание plan.md и summary.md
**Файлы:**
- `docs/tasks/task-04-booking-api/plan.md` — этот план
- `docs/tasks/task-04-booking-api/summary.md` — результаты реализации

## Формат ошибок
Согласно `backend/schemas/common.py`:
```json
{
  "error": "not_found",
  "message": "Booking with id 123 not found",
  "details": null
}
```

## Проверка (только в Docker)

Все команды запуска и тестирования выполняются ТОЛЬКО через Docker Compose:

```bash
# Запуск backend в Docker
docker compose up -d backend

# Проверка health endpoint
curl http://localhost:8000/health

# Запуск тестов в контейнере
docker compose exec backend pytest backend/tests/test_bookings.py -v

# Проверка через Swagger
# Открыть http://localhost:8000/docs
```

**Важно:** Локальный запуск через `uv run python -m backend.main` или `make run-backend` не используется.

## Definition of Done
- [ ] Все endpoints возвращают корректные HTTP-коды (200, 201, 400, 404, 422)
- [ ] Валидация работает — невалидные данные отклоняются
- [ ] Тесты проходят в Docker: `docker compose exec backend pytest backend/tests/test_bookings.py -v`
- [ ] Покрытие бронирований > 80%
- [ ] Swagger UI отображает все endpoints корректно
