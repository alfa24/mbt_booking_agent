# План: Задача 07 - Устранение замечаний по ревью

## Цель

Устранить замечания, выявленные в ходе ревью (Задача 06).

## Замечания из ревью

### Критичные (влияют на производительность/корректность)

1. **Отсутствуют FK индексы** — без них JOIN и CASCADE операции будут медленными
2. **Нет lifespan** — для корректного закрытия соединений при shutdown
3. **Нет настройки пула** — для production нагрузки

### Желательные (улучшают код)

4. **Обновить type hints** — использовать современный синтаксис Python 3.12
5. **Добавить CHECK constraints** — для целостности данных на уровне БД
6. **Добавить GIN индексы** — если будут запросы по JSONB полям

### Опциональные

7. **Изменить PK на BIGINT** — для будущего масштабирования
8. **Сделать echo настраиваемым** — убрать SQL логирование в production

## Состав работ

### 1. Исправления схемы БД

**Создать миграцию:**
```bash
make migrate-create name="add_indexes_and_constraints"
```

**Добавить в миграцию:**
- FK индексы на bookings.house_id, bookings.tenant_id, houses.owner_id
- CHECK constraints (capacity > 0, amount >= 0, check_out > check_in)
- ON DELETE для Foreign Keys

### 2. Исправления подключения к БД

**backend/database.py:**
- Добавить настройки pool_size, max_overflow
- Сделать echo настраиваемым через settings

**backend/main.py:**
- Добавить lifespan для закрытия engine

**backend/config.py:**
- Добавить debug флаг для echo

### 3. Исправления Python-кода

**Все файлы в backend/repositories/:**
- Добавить `from __future__ import annotations`
- Заменить `Optional[X]` на `X | None`
- Заменить `List[X]` на `list[X]`
- Убрать импорт List, Optional из typing

## Definition of Done

- [ ] Все критичные замечания устранены
- [ ] Миграции созданы и применены
- [ ] Тесты проходят
- [ ] Код проходит линтинг (ruff)

## Проверка пользователем

```bash
# Применение миграций
make migrate

# Запуск тестов
make test-backend

# Линтинг
make lint-backend
```
