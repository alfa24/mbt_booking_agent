"""Tests for tariff API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository():
    """Clear repository before each test."""
    from backend.services.tariff import get_tariff_repository

    repo = get_tariff_repository()
    repo.clear()
    yield


class TestCreateTariff:
    """Tests for POST /api/v1/tariffs"""

    def test_create_tariff_success(self):
        """Test creating a tariff with valid data."""
        response = client.post(
            "/api/v1/tariffs",
            json={
                "name": "Взрослый",
                "amount": 250,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Взрослый"
        assert data["amount"] == 250
        assert "created_at" in data

    def test_create_tariff_free(self):
        """Test creating a free tariff (amount=0)."""
        response = client.post(
            "/api/v1/tariffs",
            json={
                "name": "Ребёнок",
                "amount": 0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Ребёнок"
        assert data["amount"] == 0

    def test_create_tariff_invalid_amount(self):
        """Test creating a tariff with negative amount."""
        response = client.post(
            "/api/v1/tariffs",
            json={
                "name": "Invalid",
                "amount": -100,
            },
        )
        assert response.status_code == 422

    def test_create_tariff_empty_name(self):
        """Test creating a tariff with empty name."""
        response = client.post(
            "/api/v1/tariffs",
            json={
                "name": "",
                "amount": 100,
            },
        )
        assert response.status_code == 422


class TestGetTariff:
    """Tests for GET /api/v1/tariffs/{id}"""

    def test_get_tariff_success(self):
        """Test getting an existing tariff."""
        # Create tariff first
        create_response = client.post(
            "/api/v1/tariffs",
            json={"name": "Тестовый тариф", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Get the tariff
        response = client.get(f"/api/v1/tariffs/{tariff_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tariff_id
        assert data["name"] == "Тестовый тариф"
        assert data["amount"] == 100

    def test_get_tariff_not_found(self):
        """Test getting a non-existent tariff."""
        response = client.get("/api/v1/tariffs/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListTariffs:
    """Tests for GET /api/v1/tariffs"""

    def test_list_tariffs_empty(self):
        """Test listing tariffs when none exist."""
        response = client.get("/api/v1/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_tariffs_with_data(self):
        """Test listing multiple tariffs."""
        # Create two tariffs
        client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф 1", "amount": 100},
        )
        client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф 2", "amount": 200},
        )

        response = client.get("/api/v1/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_tariffs_pagination(self):
        """Test pagination with limit and offset."""
        # Create multiple tariffs
        for i in range(5):
            client.post(
                "/api/v1/tariffs",
                json={"name": f"Тариф {i+1}", "amount": (i + 1) * 100},
            )

        response = client.get("/api/v1/tariffs?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1

    def test_list_tariffs_sorting(self):
        """Test sorting tariffs."""
        # Create tariffs
        client.post(
            "/api/v1/tariffs",
            json={"name": "Бета", "amount": 200},
        )
        client.post(
            "/api/v1/tariffs",
            json={"name": "Альфа", "amount": 100},
        )

        # Sort by name ascending
        response = client.get("/api/v1/tariffs?sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Альфа"

        # Sort by name descending
        response = client.get("/api/v1/tariffs?sort=-name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Бета"

        # Sort by amount
        response = client.get("/api/v1/tariffs?sort=amount")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["amount"] == 100


class TestUpdateTariff:
    """Tests for PATCH /api/v1/tariffs/{id}"""

    def test_update_tariff_partial(self):
        """Test partial update of tariff."""
        # Create tariff
        create_response = client.post(
            "/api/v1/tariffs",
            json={"name": "Старое название", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Update only name
        response = client.patch(
            f"/api/v1/tariffs/{tariff_id}",
            json={"name": "Новое название"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое название"
        assert data["amount"] == 100  # unchanged

    def test_update_tariff_amount(self):
        """Test updating tariff amount."""
        # Create tariff
        create_response = client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Update amount
        response = client.patch(
            f"/api/v1/tariffs/{tariff_id}",
            json={"amount": 150},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 150

    def test_update_tariff_not_found(self):
        """Test updating a non-existent tariff."""
        response = client.patch(
            "/api/v1/tariffs/999",
            json={"name": "Новое название"},
        )
        assert response.status_code == 404

    def test_update_tariff_invalid_amount(self):
        """Test updating with invalid amount."""
        # Create tariff
        create_response = client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Try to update with negative amount
        response = client.patch(
            f"/api/v1/tariffs/{tariff_id}",
            json={"amount": -50},
        )
        assert response.status_code == 422


class TestDeleteTariff:
    """Tests for DELETE /api/v1/tariffs/{id}"""

    def test_delete_tariff_success(self):
        """Test deleting a tariff."""
        # Create tariff
        create_response = client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф для удаления", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Delete tariff
        response = client.delete(f"/api/v1/tariffs/{tariff_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/v1/tariffs/{tariff_id}")
        assert get_response.status_code == 404

    def test_delete_tariff_not_found(self):
        """Test deleting a non-existent tariff."""
        response = client.delete("/api/v1/tariffs/999")
        assert response.status_code == 404
