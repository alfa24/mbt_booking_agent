# Task 09: Text-to-SQL Implementation Plan

## Goal
Implement natural language to SQL query functionality with safety constraints.

## Architecture
- LLM generates SQL from natural language question
- Backend validates and executes with read-only constraints
- Frontend provides mode switcher in chat interface

## Backend Implementation

### 1. Schemas (`backend/schemas/query.py`)
- `NaturalLanguageQueryRequest`: { question: str }
- `NaturalLanguageQueryResponse`: { sql, results[], explanation, columns[] }

### 2. Service (`backend/services/text_to_sql.py`)
- `TextToSQLService` class
- System prompt with DB schema (users, houses, bookings, tariffs)
- SQL generation via LLM
- Validation: whitelist SELECT only, regex filter for dangerous commands
- Execution: read-only transaction, 5s timeout, LIMIT 1000

### 3. API (`backend/api/query.py`)
- POST /api/v1/query/natural-language
- Dependency injection for LLM service

### 4. Security
- Regex: block DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE
- Read-only transaction
- Statement timeout 5s
- LIMIT 1000 rows
- Block pg_catalog, information_schema access

## Frontend Implementation

### 1. Hook (`src/hooks/use-data-query.ts`)
- `useDataQuery(question)` mutation hook
- Uses ky for API calls

### 2. Components
- `query-results-table.tsx`: Display SQL results in table
- `data-query-mode.tsx`: Mode switcher UI

### 3. Integration
- Add toggle to message-input component
- Show DB icon when data query mode active
- Display results with SQL code block + table + explanation

## Tests
- `backend/tests/test_query.py`
- Test successful query
- Test security: DROP, UPDATE, pg_catalog access attempts

## Files to Create/Modify

### New Files
- `backend/schemas/query.py`
- `backend/services/text_to_sql.py`
- `backend/api/query.py`
- `backend/tests/test_query.py`
- `web/src/hooks/use-data-query.ts`
- `web/src/components/chat/query-results-table.tsx`
- `web/src/components/chat/data-query-mode.tsx`

### Modified Files
- `backend/api/__init__.py` - register router
- `web/src/components/chat/message-input.tsx` - add mode toggle
