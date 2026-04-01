"""Tests for user API endpoints."""

import pytest


class TestCreateUser:
    """Tests for POST /api/v1/users"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, client):
        """Test creating a user with valid data."""
        response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123456789",
                "name": "Иван Петров",
                "role": "tenant",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["telegram_id"] == "123456789"
        assert data["name"] == "Иван Петров"
        assert data["role"] == "tenant"
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_user_default_role(self, client):
        """Test creating a user with default role."""
        response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "987654321",
                "name": "Петр Иванов",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "tenant"  # default role

    @pytest.mark.asyncio
    async def test_create_user_all_roles(self, client):
        """Test creating users with all possible roles."""
        roles = ["tenant", "owner", "both"]
        for i, role in enumerate(roles):
            response = await client.post(
                "/api/v1/users",
                json={
                    "telegram_id": f"user{i}",
                    "name": f"User {i}",
                    "role": role,
                },
            )
            assert response.status_code == 201
            assert response.json()["role"] == role

    @pytest.mark.asyncio
    async def test_create_user_invalid_role(self, client):
        """Test creating a user with invalid role."""
        response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "Test",
                "role": "invalid_role",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_empty_name(self, client):
        """Test creating a user with empty name."""
        response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_missing_telegram_id(self, client):
        """Test creating a user without telegram_id."""
        response = await client.post(
            "/api/v1/users",
            json={
                "name": "Test User",
            },
        )
        assert response.status_code == 422


class TestGetUser:
    """Tests for GET /api/v1/users/{id}"""

    @pytest.mark.asyncio
    async def test_get_user_success(self, client):
        """Test getting an existing user."""
        # Create user first
        create_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123456",
                "name": "Тестовый пользователь",
            },
        )
        user_id = create_response.json()["id"]

        # Get the user
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Тестовый пользователь"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client):
        """Test getting a non-existent user."""
        response = await client.get("/api/v1/users/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListUsers:
    """Tests for GET /api/v1/users"""

    @pytest.mark.asyncio
    async def test_list_users_empty(self, client):
        """Test listing users when none exist."""
        response = await client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_users_with_data(self, client):
        """Test listing multiple users."""
        # Create two users
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "user1", "name": "Пользователь 1"},
        )
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "user2", "name": "Пользователь 2"},
        )

        response = await client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_users_filter_by_role(self, client):
        """Test filtering users by role."""
        # Create users with different roles
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "tenant1", "name": "Арендатор", "role": "tenant"},
        )
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "owner1", "name": "Арендодатель", "role": "owner"},
        )
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "both1", "name": "Оба", "role": "both"},
        )

        # Filter by tenant
        response = await client.get("/api/v1/users?role=tenant")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["role"] == "tenant"

        # Filter by owner
        response = await client.get("/api/v1/users?role=owner")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["role"] == "owner"

        # Filter by both
        response = await client.get("/api/v1/users?role=both")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["role"] == "both"

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client):
        """Test pagination with limit and offset."""
        # Create multiple users
        for i in range(5):
            await client.post(
                "/api/v1/users",
                json={"telegram_id": f"user{i}", "name": f"Пользователь {i}"},
            )

        response = await client.get("/api/v1/users?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1

    @pytest.mark.asyncio
    async def test_list_users_sorting(self, client):
        """Test sorting users."""
        # Create users
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "b", "name": "Бета"},
        )
        await client.post(
            "/api/v1/users",
            json={"telegram_id": "a", "name": "Альфа"},
        )

        # Sort by name ascending
        response = await client.get("/api/v1/users?sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Альфа"

        # Sort by name descending
        response = await client.get("/api/v1/users?sort=-name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Бета"


class TestUpdateUser:
    """Tests for PATCH /api/v1/users/{id}"""

    @pytest.mark.asyncio
    async def test_update_user_partial(self, client):
        """Test partial update of user."""
        # Create user
        create_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "Старое имя",
                "role": "tenant",
            },
        )
        user_id = create_response.json()["id"]

        # Update only name
        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json={"name": "Новое имя"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое имя"
        assert data["role"] == "tenant"  # unchanged

    @pytest.mark.asyncio
    async def test_update_user_role(self, client):
        """Test updating user role."""
        # Create user
        create_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "Test",
                "role": "tenant",
            },
        )
        user_id = create_response.json()["id"]

        # Update role
        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json={"role": "owner"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "owner"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client):
        """Test updating a non-existent user."""
        response = await client.patch(
            "/api/v1/users/999",
            json={"name": "Новое имя"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_invalid_role(self, client):
        """Test updating with invalid role."""
        # Create user
        create_response = await client.post(
            "/api/v1/users",
            json={"telegram_id": "123", "name": "Test"},
        )
        user_id = create_response.json()["id"]

        # Try to update with invalid role
        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json={"role": "invalid"},
        )
        assert response.status_code == 422


class TestReplaceUser:
    """Tests for PUT /api/v1/users/{id}"""

    @pytest.mark.asyncio
    async def test_replace_user_success(self, client):
        """Test full replacement of user."""
        # Create user
        create_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "old_id",
                "name": "Старое имя",
                "role": "tenant",
            },
        )
        user_id = create_response.json()["id"]

        # Replace all fields
        response = await client.put(
            f"/api/v1/users/{user_id}",
            json={
                "telegram_id": "new_id",
                "name": "Новое имя",
                "role": "owner",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое имя"
        assert data["role"] == "owner"

    @pytest.mark.asyncio
    async def test_replace_user_not_found(self, client):
        """Test replacing a non-existent user."""
        response = await client.put(
            "/api/v1/users/999",
            json={
                "telegram_id": "123",
                "name": "Test",
            },
        )
        assert response.status_code == 404


class TestDeleteUser:
    """Tests for DELETE /api/v1/users/{id}"""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client):
        """Test deleting a user."""
        # Create user
        create_response = await client.post(
            "/api/v1/users",
            json={"telegram_id": "delete_me", "name": "На удаление"},
        )
        user_id = create_response.json()["id"]

        # Delete user
        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client):
        """Test deleting a non-existent user."""
        response = await client.delete("/api/v1/users/999")
        assert response.status_code == 404
