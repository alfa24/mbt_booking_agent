# Task 09: Text-to-SQL Implementation Summary

## Completed Work

### Backend

#### 1. Schemas (`backend/schemas/query.py`)
- `NaturalLanguageQueryRequest` — Pydantic schema for query request
- `NaturalLanguageQueryResponse` — Pydantic schema for query response with sql, results, columns, explanation

#### 2. Service (`backend/services/text_to_sql.py`)
- `TextToSQLService` class with:
  - Database schema description in system prompt (users, houses, bookings, tariffs tables)
  - SQL generation via LLM with JSON response format
  - Security validation:
    - Whitelist: only SELECT queries allowed
    - Regex filter for dangerous keywords (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, GRANT, REVOKE)
    - Block system schemas (pg_catalog, information_schema)
  - Auto-add LIMIT 1000 if not present
  - Read-only transaction execution with 5s timeout

#### 3. API (`backend/api/query.py`)
- `POST /api/v1/query/natural-language` endpoint
- Dependency injection for TextToSQLService
- Error handling with proper HTTP status codes (400 for validation errors, 500 for execution errors)

#### 4. Router Registration (`backend/api/__init__.py`)
- Registered `query_router` in main API router

#### 5. Tests (`backend/tests/test_query.py`)
- Security tests for dangerous operations (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE)
- System schema access tests (pg_catalog, information_schema)
- Request validation tests (empty, too long, missing question)
- Unit tests for TextToSQLService validation logic

### Frontend

#### 1. Hook (`web/src/hooks/use-data-query.ts`)
- `useDataQuery()` hook using TanStack Query mutation
- Returns queryData function, data, isLoading, error, reset

#### 2. Components

**`web/src/components/chat/query-results-table.tsx`**
- Displays query results in shadcn/ui Table
- Handles empty results, formats cell values (NULL, booleans, objects)
- Shows row count

**`web/src/components/chat/data-query-mode.tsx`**
- `DataQueryMode` component with mode switcher (chat/data)
- Displays SQL code, results table, explanation
- Shows loading state and errors
- `DataQueryInputIndicator` for input field

#### 3. Integration

**`web/src/components/chat/message-input.tsx`**
- Added `mode` and `onModeChange` props
- Database icon button to toggle query mode
- Dynamic placeholder based on mode
- Shows mode indicator

**`web/src/components/chat/conversation-view.tsx`**
- Integrated `useDataQuery` hook
- Added query mode state management
- Displays `DataQueryMode` results panel in data mode
- Routes messages to appropriate handler (chat or data query)

### Security Measures

1. **SQL Validation**:
   - Only SELECT statements allowed
   - Regex blocking of dangerous keywords
   - System schema access blocked

2. **Execution Safety**:
   - Read-only transaction (`SET TRANSACTION READ ONLY`)
   - Statement timeout (5 seconds)
   - LIMIT 1000 rows maximum

3. **Input Validation**:
   - Pydantic schema validation
   - Max question length: 1000 characters

### Linting

- Backend: `ruff check backend/` — All checks passed
- Frontend: `eslint src --ext .ts,.tsx` — No errors

## Files Created/Modified

### New Files
- `backend/schemas/query.py`
- `backend/services/text_to_sql.py`
- `backend/api/query.py`
- `backend/tests/test_query.py`
- `web/src/hooks/use-data-query.ts`
- `web/src/components/chat/query-results-table.tsx`
- `web/src/components/chat/data-query-mode.tsx`

### Modified Files
- `backend/api/__init__.py` — added query_router
- `web/src/components/chat/message-input.tsx` — added mode toggle
- `web/src/components/chat/conversation-view.tsx` — integrated data query mode

## API Endpoint

```
POST /api/v1/query/natural-language
Request: { "question": "Сколько бронирований в этом месяце?" }
Response: {
  "sql": "SELECT COUNT(*) FROM bookings WHERE created_at >= '2024-01-01'",
  "results": [{ "count": 15 }],
  "columns": ["count"],
  "explanation": "В этом месяце было сделано 15 бронирований."
}
```
