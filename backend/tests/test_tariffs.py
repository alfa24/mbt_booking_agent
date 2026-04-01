"""Tests for tariff API endpoints."""

import pytest


class TestCreateTariff:
    """Tests for POST /api/v1/tariffs"""

    @pytest.mark.asyncio
    async def test_create_tariff_success(self, client):
        """Test creating a tariff with valid data."""
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_create_tariff_free(self, client):
        """Test creating a free tariff (amount=0)."""
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_create_tariff_invalid_amount(self, client):
        """Test creating a tariff with negative amount."""
        response = await client.post(
            "/api/v1/tariffs",
            json={
                "name": "Invalid",
                "amount": -100,
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_tariff_empty_name(self, client):
        """Test creating a tariff with empty name."""
        response = await client.post(
            "/api/v1/tariffs",
            json={
                "name": "",
                "amount": 100,
            },
        )
        assert response.status_code == 422


class TestGetTariff:
    """Tests for GET /api/v1/tariffs/{id}"""

    @pytest.mark.asyncio
    async def test_get_tariff_success(self, client):
        """Test getting an existing tariff."""
        # Create tariff first
        create_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Тестовый тариф", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Get the tariff
        response = await client.get(f"/api/v1/tariffs/{tariff_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tariff_id
        assert data["name"] == "Тестовый тариф"
        assert data["amount"] == 100

    @pytest.mark.asyncio
    async def test_get_tariff_not_found(self, client):
        """Test getting a non-existent tariff."""
        response = await client.get("/api/v1/tariffs/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListTariffs:
    """Tests for GET /api/v1/tariffs"""

    @pytest.mark.asyncio
    async def test_list_tariffs_empty(self, client):
        """Test listing tariffs when none exist."""
        response = await client.get("/api/v1/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tariffs_with_data(self, client):
        """Test listing multiple tariffs."""
        # Create two tariffs
        await client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф 1", "amount": 100},
        )
        await client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф 2", "amount": 200},
        )

        response = await client.get("/api/v1/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_tariffs_pagination(self, client):
        """Test pagination with limit and offset."""
        # Create multiple tariffs
        for i in range(5):
            await client.post(
                "/api/v1/tariffs",
                json={"name": f"Тариф {i+1}", "amount": (i + 1) * 100},
            )

        response = await client.get("/api/v1/tariffs?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1

    @pytest.mark.asyncio
    async def test_list_tariffs_sorting(self, client):
        """Test sorting tariffs."""
        # Create tariffs
        await client.post(
            "/api/v1/tariffs",
            json={"name": "Бета", "amount": 200},
        )
        await client.post(
            "/api/v1/tariffs",
            json={"name": "Альфа", "amount": 100},
        )

        # Sort by name ascending
        response = await client.get("/api/v1/tariffs?sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Альфа"

        # Sort by name descending
        response = await client.get("/api/v1/tariffs?sort=-name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Бета"

        # Sort by amount
        response = await client.get("/api/v1/tariffs?sort=amount")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["amount"] == 100


class TestUpdateTariff:
    """Tests for PATCH /api/v1/tariffs/{id}"""

    @pytest.mark.asyncio
    async def test_update_tariff_partial(self, client):
        """Test partial update of tariff."""
        # Create tariff
        create_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Старое название", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Update only name
        response = await client.patch(
            f"/api/v1/tariffs/{tariff_id}",
            json={"name": "Новое название"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое название"
        assert data["amount"] == 100  # unchanged

    @pytest.mark.asyncio
    async def test_update_tariff_amount(self, client):
        """Test updating tariff amount."""
        # Create tariff
        create_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Update amount
        response = await client.patch(
            f"/api/v1/tariffs/{tariff_id}",
            json={"amount": 150},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 150

    @pytest.mark.asyncio
    async def test_update_tariff_not_found(self, client):
        """Test updating a non-existent tariff."""
        response = await client.patch(
            "/api/v1/tariffs/999",
            json={"name": "Новое название"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_tariff_invalid_amount(self, client):
        """Test updating with invalid amount."""
        # Create tariff
        create_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Try to update with negative amount
        response = await client.patch(
            f"/api/v1/tariffs/{tariff_id}",
            json={"amount": -50},
        )
        assert response.status_code == 422


class TestDeleteTariff:
    """Tests for DELETE /api/v1/tariffs/{id}"""

    @pytest.mark.asyncio
    async def test_delete_tariff_success(self, client):
        """Test deleting a tariff."""
        # Create tariff
        create_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Тариф для удаления", "amount": 100},
        )
        tariff_id = create_response.json()["id"]

        # Delete tariff
        response = await client.delete(f"/api/v1/tariffs/{tariff_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/v1/tariffs/{tariff_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_tariff_not_found(self, client):
        """Test deleting a non-existent tariff."""
        response = await client.delete("/api/v1/tariffs/999")
        assert response.status_code == 404
