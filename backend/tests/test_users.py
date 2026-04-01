"""Tests for user API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository():
    """Clear repository before each test."""
    from backend.services.user import get_user_repository

    repo = get_user_repository()
    repo.clear()
    yield


class TestCreateUser:
    """Tests for POST /api/v1/users"""

    def test_create_user_success(self):
        """Test creating a user with valid data."""
        response = client.post(
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

    def test_create_user_default_role(self):
        """Test creating a user with default role."""
        response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "987654321",
                "name": "Петр Иванов",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "tenant"  # default role

    def test_create_user_all_roles(self):
        """Test creating users with all possible roles."""
        roles = ["tenant", "owner", "both"]
        for i, role in enumerate(roles):
            response = client.post(
                "/api/v1/users",
                json={
                    "telegram_id": f"user{i}",
                    "name": f"User {i}",
                    "role": role,
                },
            )
            assert response.status_code == 201
            assert response.json()["role"] == role

    def test_create_user_invalid_role(self):
        """Test creating a user with invalid role."""
        response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "Test",
                "role": "invalid_role",
            },
        )
        assert response.status_code == 422

    def test_create_user_empty_name(self):
        """Test creating a user with empty name."""
        response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "",
            },
        )
        assert response.status_code == 422

    def test_create_user_missing_telegram_id(self):
        """Test creating a user without telegram_id."""
        response = client.post(
            "/api/v1/users",
            json={
                "name": "Test User",
            },
        )
        assert response.status_code == 422


class TestGetUser:
    """Tests for GET /api/v1/users/{id}"""

    def test_get_user_success(self):
        """Test getting an existing user."""
        # Create user first
        create_response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123456",
                "name": "Тестовый пользователь",
            },
        )
        user_id = create_response.json()["id"]

        # Get the user
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Тестовый пользователь"

    def test_get_user_not_found(self):
        """Test getting a non-existent user."""
        response = client.get("/api/v1/users/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListUsers:
    """Tests for GET /api/v1/users"""

    def test_list_users_empty(self):
        """Test listing users when none exist."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_users_with_data(self):
        """Test listing multiple users."""
        # Create two users
        client.post(
            "/api/v1/users",
            json={"telegram_id": "user1", "name": "Пользователь 1"},
        )
        client.post(
            "/api/v1/users",
            json={"telegram_id": "user2", "name": "Пользователь 2"},
        )

        response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_users_filter_by_role(self):
        """Test filtering users by role."""
        # Create users with different roles
        client.post(
            "/api/v1/users",
            json={"telegram_id": "tenant1", "name": "Арендатор", "role": "tenant"},
        )
        client.post(
            "/api/v1/users",
            json={"telegram_id": "owner1", "name": "Арендодатель", "role": "owner"},
        )
        client.post(
            "/api/v1/users",
            json={"telegram_id": "both1", "name": "Оба", "role": "both"},
        )

        # Filter by tenant
        response = client.get("/api/v1/users?role=tenant")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["role"] == "tenant"

        # Filter by owner
        response = client.get("/api/v1/users?role=owner")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["role"] == "owner"

        # Filter by both
        response = client.get("/api/v1/users?role=both")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["role"] == "both"

    def test_list_users_pagination(self):
        """Test pagination with limit and offset."""
        # Create multiple users
        for i in range(5):
            client.post(
                "/api/v1/users",
                json={"telegram_id": f"user{i}", "name": f"Пользователь {i}"},
            )

        response = client.get("/api/v1/users?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1

    def test_list_users_sorting(self):
        """Test sorting users."""
        # Create users
        client.post(
            "/api/v1/users",
            json={"telegram_id": "b", "name": "Бета"},
        )
        client.post(
            "/api/v1/users",
            json={"telegram_id": "a", "name": "Альфа"},
        )

        # Sort by name ascending
        response = client.get("/api/v1/users?sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Альфа"

        # Sort by name descending
        response = client.get("/api/v1/users?sort=-name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Бета"


class TestUpdateUser:
    """Tests for PATCH /api/v1/users/{id}"""

    def test_update_user_partial(self):
        """Test partial update of user."""
        # Create user
        create_response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "Старое имя",
                "role": "tenant",
            },
        )
        user_id = create_response.json()["id"]

        # Update only name
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"name": "Новое имя"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое имя"
        assert data["role"] == "tenant"  # unchanged

    def test_update_user_role(self):
        """Test updating user role."""
        # Create user
        create_response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "123",
                "name": "Test",
                "role": "tenant",
            },
        )
        user_id = create_response.json()["id"]

        # Update role
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"role": "owner"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "owner"

    def test_update_user_not_found(self):
        """Test updating a non-existent user."""
        response = client.patch(
            "/api/v1/users/999",
            json={"name": "Новое имя"},
        )
        assert response.status_code == 404

    def test_update_user_invalid_role(self):
        """Test updating with invalid role."""
        # Create user
        create_response = client.post(
            "/api/v1/users",
            json={"telegram_id": "123", "name": "Test"},
        )
        user_id = create_response.json()["id"]

        # Try to update with invalid role
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"role": "invalid"},
        )
        assert response.status_code == 422


class TestReplaceUser:
    """Tests for PUT /api/v1/users/{id}"""

    def test_replace_user_success(self):
        """Test full replacement of user."""
        # Create user
        create_response = client.post(
            "/api/v1/users",
            json={
                "telegram_id": "old_id",
                "name": "Старое имя",
                "role": "tenant",
            },
        )
        user_id = create_response.json()["id"]

        # Replace all fields
        response = client.put(
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

    def test_replace_user_not_found(self):
        """Test replacing a non-existent user."""
        response = client.put(
            "/api/v1/users/999",
            json={
                "telegram_id": "123",
                "name": "Test",
            },
        )
        assert response.status_code == 404


class TestDeleteUser:
    """Tests for DELETE /api/v1/users/{id}"""

    def test_delete_user_success(self):
        """Test deleting a user."""
        # Create user
        create_response = client.post(
            "/api/v1/users",
            json={"telegram_id": "delete_me", "name": "На удаление"},
        )
        user_id = create_response.json()["id"]

        # Delete user
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self):
        """Test deleting a non-existent user."""
        response = client.delete("/api/v1/users/999")
        assert response.status_code == 404
