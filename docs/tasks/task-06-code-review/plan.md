# План: Задача 06 - Ревью реализованных решений

## Цель

Провести ревью уже реализованных решений с помощью специализированных скиллов и устранить выявленные замечания.

## Состав работ

### 1. Ревью схемы БД через skill `postgresql-table-design`

**Проверено:**
- Типы данных PostgreSQL
- Индексы (PK, FK, частые запросы)
- Constraints
- JSONB поля

**Замечания:**
1. **PK тип**: Используется `INTEGER` вместо `BIGINT GENERATED ALWAYS AS IDENTITY`
2. **FK индексы**: Отсутствуют явные индексы на Foreign Key колонках
3. **JSONB индексы**: Нет GIN индексов на guests_planned/guests_actual
4. **CHECK constraints**: Нет CHECK для capacity > 0, amount >= 0
5. **TIMESTAMPTZ**: Используется `DateTime(timezone=True)` — корректно

### 2. Ревью подключения к БД через skill `fastapi-templates`

**Проверено:**
- Конфигурация async engine
- AsyncSessionLocal
- get_db() dependency
- Lifespan интеграция

**Замечания:**
1. **Lifespan**: Отсутствует lifespan в main.py для управления соединениями
2. **Engine dispose**: Нет явного закрытия engine при shutdown
3. **Connection pooling**: Нет настройки pool_size/max_overflow
4. **Echo**: `echo=True` в production не рекомендуется

### 3. Ревью Python-кода через skill `modern-python`

**Проверено:**
- Type hints
- Async patterns
- Обработка ошибок
- Docstrings
- Импорты

**Замечания:**
1. **Type hints**: Используется `Optional[X]` вместо `X | None`
2. **List hints**: Используется `List[X]` вместо `list[X]`
3. **Union hints**: Используется `Union[X, Y]` вместо `X | Y`
4. **Tuple hints**: Используется `tuple[X, Y]` — корректно

## Файлы для ревью

- `backend/database.py`
- `backend/models/*.py`
- `backend/repositories/*.py`
- `backend/dependencies.py`
- `alembic/versions/2a84cf51810b_initial_migration.py`

## Definition of Done

- [ ] Ревью схемы БД через skill `postgresql-table-design` выполнено
- [ ] Ревью подключения к БД через skill `fastapi-templates` выполнено
- [ ] Ревью Python-кода через skill `modern-python` выполнено
- [ ] Выявленные замечания устранены
- [ ] Тесты проходят после исправлений
