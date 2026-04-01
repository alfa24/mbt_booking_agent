"""Tests for booking API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories.booking import BookingRepository
from backend.schemas.booking import BookingStatus

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository():
    """Clear repository before each test."""
    # Get repository instance and clear it
    from backend.services.booking import get_booking_repository

    repo = get_booking_repository()
    repo.clear()
    yield


class TestCreateBooking:
    """Tests for POST /api/v1/bookings"""

    def test_create_booking_success(self):
        """Test creating a booking with valid data."""
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["house_id"] == 1
        assert data["tenant_id"] == 1
        assert data["check_in"] == "2024-06-01"
        assert data["check_out"] == "2024-06-03"
        assert data["status"] == "pending"
        assert data["total_amount"] == 500  # 2 adults * 250
        assert len(data["guests_planned"]) == 1

    def test_create_booking_invalid_dates(self):
        """Test creating a booking with check_in >= check_out."""
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-03",
                "check_out": "2024-06-01",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        assert response.status_code == 422

    def test_create_booking_same_date(self):
        """Test creating a booking with check_in == check_out."""
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-01",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        assert response.status_code == 422

    def test_create_booking_missing_guests(self):
        """Test creating a booking without guests."""
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
            },
        )
        assert response.status_code == 422

    def test_create_booking_empty_guests(self):
        """Test creating a booking with empty guests list."""
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [],
            },
        )
        assert response.status_code == 422

    def test_create_booking_date_conflict(self):
        """Test creating a booking with conflicting dates."""
        # Create first booking
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Try to create overlapping booking
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-12",
                "check_out": "2024-06-17",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )
        assert response.status_code == 400
        assert "conflict" in response.json()["error"]

    def test_create_booking_different_house_no_conflict(self):
        """Test that bookings for different houses don't conflict."""
        # Create booking for house 1
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Create booking for house 2 with overlapping dates
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 2,
                "check_in": "2024-06-12",
                "check_out": "2024-06-17",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )
        assert response.status_code == 201

    def test_create_booking_amount_calculation(self):
        """Test amount calculation for different guest types."""
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [
                    {"tariff_id": 1, "count": 2},  # Children: free
                    {"tariff_id": 2, "count": 2},  # Adults: 250 each
                    {"tariff_id": 3, "count": 1},  # Regular: 150
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["total_amount"] == 650  # 0*2 + 250*2 + 150*1


class TestGetBooking:
    """Tests for GET /api/v1/bookings/{id}"""

    def test_get_booking_success(self):
        """Test getting an existing booking."""
        # Create booking first
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Get the booking
        response = client.get(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking_id
        assert data["house_id"] == 1

    def test_get_booking_not_found(self):
        """Test getting a non-existent booking."""
        response = client.get("/api/v1/bookings/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListBookings:
    """Tests for GET /api/v1/bookings"""

    def test_list_bookings_empty(self):
        """Test listing bookings when none exist."""
        response = client.get("/api/v1/bookings")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_bookings_with_data(self):
        """Test listing multiple bookings."""
        # Create two bookings
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 2,
                "check_in": "2024-07-01",
                "check_out": "2024-07-03",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )

        response = client.get("/api/v1/bookings")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_bookings_filter_by_house(self):
        """Test filtering bookings by house_id."""
        # Create bookings for different houses
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 2,
                "check_in": "2024-07-01",
                "check_out": "2024-07-03",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )

        response = client.get("/api/v1/bookings?house_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["house_id"] == 1

    def test_list_bookings_filter_by_status(self):
        """Test filtering bookings by status."""
        # Create and cancel a booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]
        client.delete(f"/api/v1/bookings/{booking_id}")

        # Create another booking (pending)
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 2,
                "check_in": "2024-07-01",
                "check_out": "2024-07-03",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )

        response = client.get("/api/v1/bookings?status=cancelled")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "cancelled"

    def test_list_bookings_pagination(self):
        """Test pagination with limit and offset."""
        # Create multiple bookings
        for i in range(5):
            client.post(
                "/api/v1/bookings",
                json={
                    "house_id": i + 1,
                    "check_in": f"2024-06-{i+1:02d}",
                    "check_out": f"2024-06-{i+3:02d}",
                    "guests": [{"tariff_id": 2, "count": 1}],
                },
            )

        response = client.get("/api/v1/bookings?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1


class TestUpdateBooking:
    """Tests for PATCH /api/v1/bookings/{id}"""

    def test_update_booking_dates(self):
        """Test updating booking dates."""
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Update dates
        response = client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "check_in": "2024-06-05",
                "check_out": "2024-06-07",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["check_in"] == "2024-06-05"
        assert data["check_out"] == "2024-06-07"

    def test_update_booking_guests(self):
        """Test updating guest composition."""
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Update guests (changes amount from 500 to 750)
        response = client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "guests": [{"tariff_id": 2, "count": 3}],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] == 750
        assert len(data["guests_planned"]) == 1
        assert data["guests_planned"][0]["count"] == 3

    def test_update_booking_not_found(self):
        """Test updating a non-existent booking."""
        response = client.patch(
            "/api/v1/bookings/999",
            json={"check_in": "2024-06-05"},
        )
        assert response.status_code == 404

    def test_update_booking_invalid_dates(self):
        """Test updating with invalid dates."""
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Try to update with invalid dates
        response = client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "check_in": "2024-06-05",
                "check_out": "2024-06-04",
            },
        )
        assert response.status_code == 422

    def test_update_booking_date_conflict(self):
        """Test updating with conflicting dates."""
        # Create first booking
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Create second booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-20",
                "check_out": "2024-06-25",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )
        booking_id = create_response.json()["id"]

        # Try to update second booking to overlap with first
        response = client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "check_in": "2024-06-12",
                "check_out": "2024-06-17",
            },
        )
        assert response.status_code == 400


class TestCancelBooking:
    """Tests for DELETE /api/v1/bookings/{id}"""

    def test_cancel_booking_success(self):
        """Test cancelling a booking."""
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Cancel booking
        response = client.delete(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_booking_not_found(self):
        """Test cancelling a non-existent booking."""
        response = client.delete("/api/v1/bookings/999")
        assert response.status_code == 404

    def test_cancel_already_cancelled(self):
        """Test cancelling an already cancelled booking."""
        # Create and cancel booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]
        client.delete(f"/api/v1/bookings/{booking_id}")

        # Try to cancel again
        response = client.delete(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 400
        assert "already_cancelled" in response.json()["error"]

    def test_cancelled_booking_not_in_list(self):
        """Test that cancelled bookings don't appear in conflict checks."""
        # Create and cancel booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]
        client.delete(f"/api/v1/bookings/{booking_id}")

        # Create new booking for same dates (should succeed)
        response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )
        assert response.status_code == 201
