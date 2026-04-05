"""Text-to-SQL service for natural language database queries."""

import json
import logging
import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.llm import LLMClient, RouterAIClient
from backend.config import settings

logger = logging.getLogger(__name__)

# Dangerous SQL keywords to block
DANGEROUS_KEYWORDS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bpg_catalog\b",
    r"\binformation_schema\b",
]

# System tables to block
SYSTEM_SCHEMAS = ["pg_catalog", "information_schema"]

# Database schema description for LLM
DB_SCHEMA = """
You are a SQL expert. Generate PostgreSQL SELECT queries based on user questions.

Database Schema:

1. users table:
   - id (INTEGER, PRIMARY KEY)
   - telegram_id (STRING, UNIQUE)
   - name (STRING)
   - role (ENUM: tenant, owner, both)
   - created_at (TIMESTAMP)

2. houses table:
   - id (INTEGER, PRIMARY KEY)
   - name (STRING)
   - description (STRING)
   - capacity (INTEGER)
   - owner_id (INTEGER, FOREIGN KEY -> users.id)
   - is_active (BOOLEAN)
   - created_at (TIMESTAMP)

3. bookings table:
   - id (INTEGER, PRIMARY KEY)
   - house_id (INTEGER, FOREIGN KEY -> houses.id)
   - tenant_id (INTEGER, FOREIGN KEY -> users.id)
   - check_in (DATE)
   - check_out (DATE)
   - guests_planned (JSON)
   - guests_actual (JSON)
   - total_amount (INTEGER)
   - status (ENUM: pending, confirmed, cancelled, completed)
   - created_at (TIMESTAMP)

4. tariffs table:
   - id (INTEGER, PRIMARY KEY)
   - name (STRING)
   - amount (INTEGER)
   - created_at (TIMESTAMP)

Rules:
1. Generate ONLY SELECT queries
2. Use proper table aliases for clarity
3. Limit results to 1000 rows maximum
4. Use appropriate JOINs when querying multiple tables
5. Format dates properly (YYYY-MM-DD)
6. Always include meaningful column names

Respond in JSON format:
{
    "sql": "SELECT ...",
    "explanation": "Human-readable explanation of what this query does"
}
"""


class TextToSQLService:
    """Service for converting natural language to SQL queries."""

    def __init__(self, client: LLMClient | None = None) -> None:
        """Initialize TextToSQL service.

        Args:
            client: LLM client implementation (defaults to RouterAI)
        """
        self._client = client or RouterAIClient(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.llm_model,
        )

    def _validate_sql(self, sql: str) -> None:
        """Validate SQL query for safety.

        Args:
            sql: SQL query to validate

        Raises:
            ValueError: If query contains dangerous operations
        """
        sql_upper = sql.upper().strip()

        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")

        # Check for dangerous keywords
        for pattern in DANGEROUS_KEYWORDS:
            if re.search(pattern, sql, re.IGNORECASE):
                raise ValueError(f"Query contains forbidden keyword: {pattern}")

        # Check for system schema access
        for schema in SYSTEM_SCHEMAS:
            if schema in sql.lower():
                raise ValueError(f"Access to system schema '{schema}' is forbidden")

    def _add_limit(self, sql: str) -> str:
        """Add LIMIT clause if not present.

        Args:
            sql: SQL query

        Returns:
            SQL query with LIMIT clause
        """
        sql_stripped = sql.strip()
        if not re.search(r"\bLIMIT\s+\d+\b", sql_stripped, re.IGNORECASE):
            sql_stripped = f"{sql_stripped.rstrip(';')} LIMIT 1000"
        return sql_stripped

    async def generate_sql(self, question: str) -> dict[str, str]:
        """Generate SQL from natural language question.

        Args:
            question: Natural language question

        Returns:
            Dict with 'sql' and 'explanation' keys
        """
        messages = [
            {"role": "system", "content": DB_SCHEMA},
            {"role": "user", "content": question},
        ]

        response = await self._client.chat(messages)
        content = response.get("content", "")

        try:
            # Try to parse as JSON
            result = json.loads(content)
            return {
                "sql": result.get("sql", ""),
                "explanation": result.get("explanation", ""),
            }
        except json.JSONDecodeError:
            # Fallback: try to extract SQL from markdown code blocks
            sql_match = re.search(r"```sql\n(.*?)\n```", content, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1).strip()
            else:
                # Try to find SQL starting with SELECT
                sql_match = re.search(r"(SELECT\s+.*?)(?:\n|$)", content, re.DOTALL | re.IGNORECASE)
                sql = sql_match.group(1).strip() if sql_match else ""

            return {
                "sql": sql,
                "explanation": "Query generated from natural language question.",
            }

    async def execute_query(
        self,
        session: AsyncSession,
        question: str,
    ) -> dict[str, Any]:
        """Execute natural language query.

        Args:
            session: Database session
            question: Natural language question

        Returns:
            Query results with metadata

        Raises:
            ValueError: If query is unsafe or fails validation
        """
        # Generate SQL
        generated = await self.generate_sql(question)
        sql = generated["sql"]
        explanation = generated["explanation"]

        if not sql:
            raise ValueError("Failed to generate SQL query")

        # Validate SQL
        self._validate_sql(sql)

        # Add LIMIT if not present
        sql = self._add_limit(sql)

        try:
            # Execute in read-only transaction with timeout
            await session.execute(text("SET TRANSACTION READ ONLY"))
            await session.execute(text("SET LOCAL statement_timeout = '5s'"))

            result = await session.execute(text(sql))
            rows = result.mappings().all()

            # Convert to list of dicts
            results = [dict(row) for row in rows]
            columns = list(results[0].keys()) if results else []

            return {
                "sql": sql,
                "results": results,
                "columns": columns,
                "explanation": explanation,
            }

        except Exception as e:
            logger.error("Query execution failed: %s", e, exc_info=True)
            raise ValueError("Query execution failed") from e
