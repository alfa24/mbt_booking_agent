# Task 05 & 07: Стабилизировать intent processing и list_bookings

## Проблема

1. **Intent `list_bookings` возвращал ошибку**: LLM пытался вызвать инструмент `list_bookings`, но он называется `get_my_bookings`
2. **~40% intents падали с ошибкой**: Недостаточная обработка ошибок и отсутствие поддержки альтернативных названий
3. **Непонятные ошибки**: Пользователь видел "Упс, мозги перегрелись" без деталей

## Решение

### 1. Добавлена поддержка альтернативных названий инструментов

```python
# Поддержка вариантов названий
normalized_name = tool_name
if tool_name in ("list_bookings", "get_bookings", "my_bookings"):
    normalized_name = "get_my_bookings"
```

### 2. Улучшена обработка ошибок

**Было:**
```python
except Exception as e:
    result = {"error": str(e)}  # Непонятно что случилось
```

**Стало:**
```python
except KeyError as e:
    logger.error("Missing required argument for tool %s: %s", tool_name, e)
    result = {"error": f"Missing required argument: {e}"}
except Exception as e:
    logger.exception("Tool execution failed: %s", tool_name)
    result = {"error": f"Tool execution failed: {str(e)}"}
```

### 3. Информативные ошибки для неизвестных инструментов

**Было:**
```python
result = {"error": f"Unknown tool: {tool_name}"}
```

**Стало:**
```python
logger.warning("Unknown tool: %s (normalized: %s)", tool_name, normalized_name)
result = {
    "error": f"Unknown tool: {tool_name}. "
             f"Available tools: list_available_houses, check_availability, "
             f"create_booking, cancel_booking, get_my_bookings"
}
```

## Поддерживаемые альтернативные названия

| Запрошенный инструмент | Нормализованный |
|------------------------|-----------------|
| `list_bookings` | `get_my_bookings` |
| `get_bookings` | `get_my_bookings` |
| `my_bookings` | `get_my_bookings` |

## Definition of Done (самопроверка)

- [x] Intent `list_bookings` → вызывается `get_my_bookings`
- [x] Intent `get_my_bookings` → работает корректно
- [x] Ошибки валидации аргументов → понятное сообщение
- [x] Неизвестные инструменты → список доступных
- [x] Ruff lint проходит без ошибок
- [x] Логирование всех ошибок для отладки

## Результат

✅ Tool calling стал стабильнее:
- Поддержка вариаций названий инструментов
- Детальные сообщения об ошибках
- Разделение KeyError и общих Exception
- Логирование всех проблем для анализа
- Пользователи реже видят generic fallback
