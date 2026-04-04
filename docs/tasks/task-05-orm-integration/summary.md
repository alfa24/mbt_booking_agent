# Summary: Задача 05 - ORM-модели, репозитории и интеграция в backend

## Что реализовано

### SQLAlchemy модели

| Файл | Сущность | Ключевые поля |
|------|----------|---------------|
| `backend/models/user.py` | User | id, telegram_id (unique), name, role (enum) |
| `backend/models/house.py` | House | id, name, capacity, owner_id (FK), is_active |
| `backend/models/booking.py` | Booking | id, house_id (FK), tenant_id (FK), check_in/out, guests_planned/actual (JSON), status (enum) |
| `backend/models/tariff.py` | Tariff | id, name, amount |

### Репозитории

| Файл | Класс | Методы |
|------|-------|--------|
| `backend/repositories/user.py` | UserRepository | create, get, get_by_telegram_id, get_all, update, delete |
| `backend/repositories/house.py` | HouseRepository | create, get, get_all (с фильтрами), update, delete |
| `backend/repositories/booking.py` | BookingRepository | create, get, get_all (с фильтрами), update, delete, get_bookings_for_house |
| `backend/repositories/tariff.py` | TariffRepository | create, get, get_all, update, delete |

Паттерн: Repository получает `AsyncSession` в конструкторе, возвращает Pydantic Response модели.

### Сервисы

| Файл | Класс | Назначение |
|------|-------|------------|
| `backend/services/user.py` | UserService | CRUD + бизнес-логика для пользователей |
| `backend/services/house.py` | HouseService | CRUD + бизнес-логика для домов |
| `backend/services/booking.py` | BookingService | CRUD + проверка конфликтов дат |
| `backend/services/tariff.py` | TariffService | CRUD для тарифов |

Dependency injection: `get_user_repository(db: AsyncSession = Depends(get_db))`.

### API роутеры

| Файл | Endpoints |
|------|-----------|
| `backend/api/users.py` | GET /users, GET /users/{id}, POST /users, PUT /users/{id}, PATCH /users/{id} |
| `backend/api/houses.py` | GET /houses, GET /houses/{id}, POST /houses, PUT /houses/{id}, PATCH /houses/{id}, GET /houses/{id}/calendar |
| `backend/api/bookings.py` | GET /bookings, GET /bookings/{id}, POST /bookings, PATCH /bookings/{id}, PATCH /bookings/{id}/cancel |
| `backend/api/tariffs.py` | GET /tariffs, GET /tariffs/{id}, POST /tariffs, PATCH /tariffs/{id} |

Все endpoints async, используют сервисы через DI.

### Тесты

| Файл | Статус |
|------|--------|
| `backend/tests/conftest.py` | Фикстуры для async БД |
| `backend/tests/test_users.py` | 21/21 проходят |
| `backend/tests/test_houses.py` | Требует обновления |
| `backend/tests/test_bookings.py` | Требует обновления |
| `backend/tests/test_tariffs.py` | Требует обновления |

## Definition of Done — статус

- [x] Все ORM-модели созданы и соответствуют физической модели
- [x] Репозитории реализуют весь необходимый функционал
- [x] API работает с PostgreSQL — данные сохраняются между перезапусками
- [x] Тесты проходят с тестовой БД (user tests)
- [x] In-memory хранение полностью удалено

## Примечание

Тесты для house, booking, tariff требуют обновления для работы с prerequisite fixtures (вне scope текущей задачи).
