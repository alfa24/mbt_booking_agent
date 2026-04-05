"""Tests for natural language query API."""

import pytest
from httpx import AsyncClient


class TestQueryValidation:
    """Tests for SQL validation and security."""

    async def test_drop_table_blocked(self, client: AsyncClient):
        """Test that DROP TABLE is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "DROP TABLE users;"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_delete_blocked(self, client: AsyncClient):
        """Test that DELETE is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "DELETE FROM users WHERE id=1"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_update_blocked(self, client: AsyncClient):
        """Test that UPDATE is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "UPDATE users SET name='hacked'"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_insert_blocked(self, client: AsyncClient):
        """Test that INSERT is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "INSERT INTO users (name) VALUES ('hacker')"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_alter_blocked(self, client: AsyncClient):
        """Test that ALTER is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "ALTER TABLE users ADD COLUMN hacked BOOLEAN"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_create_blocked(self, client: AsyncClient):
        """Test that CREATE is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "CREATE TABLE hacked (id INT)"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_truncate_blocked(self, client: AsyncClient):
        """Test that TRUNCATE is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "TRUNCATE TABLE users"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_pg_catalog_blocked(self, client: AsyncClient):
        """Test that pg_catalog access is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "SELECT * FROM pg_catalog.pg_tables"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()

    async def test_information_schema_blocked(self, client: AsyncClient):
        """Test that information_schema access is blocked."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "SELECT * FROM information_schema.tables"},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "unsafe" in response.json()["detail"].lower()


class TestQueryRequestValidation:
    """Tests for request validation."""

    async def test_empty_question_rejected(self, client: AsyncClient):
        """Test that empty question is rejected."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": ""},
        )
        assert response.status_code == 422

    async def test_question_too_long_rejected(self, client: AsyncClient):
        """Test that very long question is rejected."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={"question": "x" * 1001},
        )
        assert response.status_code == 422

    async def test_missing_question_rejected(self, client: AsyncClient):
        """Test that missing question field is rejected."""
        response = await client.post(
            "/api/v1/query/natural-language",
            json={},
        )
        assert response.status_code == 422


class TestQueryService:
    """Tests for TextToSQLService."""

    def test_validate_sql_allows_select(self):
        """Test that valid SELECT queries are allowed."""
        from backend.services.text_to_sql import TextToSQLService

        service = TextToSQLService()

        # Should not raise
        service._validate_sql("SELECT * FROM users")
        service._validate_sql("SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'")
        service._validate_sql("SELECT u.name, h.name FROM users u JOIN houses h ON u.id = h.owner_id")

    def test_validate_sql_rejects_non_select(self):
        """Test that non-SELECT queries are rejected."""
        from backend.services.text_to_sql import TextToSQLService

        service = TextToSQLService()

        with pytest.raises(ValueError, match="Only SELECT"):
            service._validate_sql("INSERT INTO users (name) VALUES ('test')")

        with pytest.raises(ValueError, match="Only SELECT"):
            service._validate_sql("UPDATE users SET name = 'test'")

    def test_validate_sql_rejects_dangerous_keywords(self):
        """Test that dangerous keywords are rejected."""
        from backend.services.text_to_sql import TextToSQLService

        service = TextToSQLService()

        with pytest.raises(ValueError, match="forbidden"):
            service._validate_sql("SELECT * FROM users; DROP TABLE users")

    def test_add_limit_adds_limit(self):
        """Test that LIMIT is added to queries without it."""
        from backend.services.text_to_sql import TextToSQLService

        service = TextToSQLService()

        sql = service._add_limit("SELECT * FROM users")
        assert "LIMIT 1000" in sql

    def test_add_limit_preserves_existing_limit(self):
        """Test that existing LIMIT is preserved."""
        from backend.services.text_to_sql import TextToSQLService

        service = TextToSQLService()

        sql = service._add_limit("SELECT * FROM users LIMIT 100")
        assert "LIMIT 100" in sql
        assert sql.count("LIMIT") == 1
