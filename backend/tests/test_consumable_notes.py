"""Tests for Consumable Notes API endpoints."""

import pytest


@pytest.fixture
async def test_user_for_notes(client):
    """Create a test user for notes tests."""
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "notes_test_user",
            "name": "Notes Test User",
            "role": "owner",
        },
    )
    return response.json()


@pytest.fixture
async def test_house_for_notes(client, test_user_for_notes):
    """Create a test house for notes tests."""
    response = await client.post(
        "/api/v1/houses",
        json={
            "name": "Test House for Notes",
            "description": "A test house",
            "capacity": 6,
            "is_active": True,
        },
    )
    return response.json()


@pytest.mark.asyncio
async def test_create_note(client, test_house_for_notes, test_user_for_notes):
    """Test creating a consumable note."""
    response = await client.post(
        "/api/v1/consumable-notes",
        json={
            "house_id": test_house_for_notes["id"],
            "name": "Туалетная бумага",
            "comment": "Закончилась",
            "created_by": test_user_for_notes["id"],
        },
    )
    assert response.status_code == 201
    note = response.json()
    assert note["name"] == "Туалетная бумага"
    assert note["comment"] == "Закончилась"
    assert note["house_id"] == test_house_for_notes["id"]


@pytest.mark.asyncio
async def test_create_note_house_not_found(client, test_user_for_notes):
    """Test creating a note for non-existent house."""
    response = await client.post(
        "/api/v1/consumable-notes",
        json={
            "house_id": 99999,
            "name": "Test Item",
            "created_by": test_user_for_notes["id"],
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_notes(client, test_house_for_notes, test_user_for_notes):
    """Test listing consumable notes."""
    # Create a note first
    await client.post(
        "/api/v1/consumable-notes",
        json={
            "house_id": test_house_for_notes["id"],
            "name": "Моющее средство",
            "created_by": test_user_for_notes["id"],
        },
    )

    # List notes
    response = await client.get("/api/v1/consumable-notes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_notes_by_house(client, test_house_for_notes, test_user_for_notes):
    """Test listing notes filtered by house."""
    # Create a note
    await client.post(
        "/api/v1/consumable-notes",
        json={
            "house_id": test_house_for_notes["id"],
            "name": "Губки",
            "created_by": test_user_for_notes["id"],
        },
    )

    # List notes by house
    response = await client.get(f"/api/v1/consumable-notes?house_id={test_house_for_notes['id']}")
    assert response.status_code == 200
    data = response.json()
    assert all(n["house_id"] == test_house_for_notes["id"] for n in data["items"])


@pytest.mark.asyncio
async def test_update_note(client, test_house_for_notes, test_user_for_notes):
    """Test updating a consumable note."""
    # Create a note
    create_response = await client.post(
        "/api/v1/consumable-notes",
        json={
            "house_id": test_house_for_notes["id"],
            "name": "Старый комментарий",
            "created_by": test_user_for_notes["id"],
        },
    )
    note = create_response.json()

    # Update the note
    response = await client.patch(
        f"/api/v1/consumable-notes/{note['id']}",
        json={
            "name": "Новое название",
            "comment": "Новый комментарий",
        },
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Новое название"
    assert updated["comment"] == "Новый комментарий"


@pytest.mark.asyncio
async def test_update_note_not_found(client):
    """Test updating non-existent note."""
    response = await client.patch(
        "/api/v1/consumable-notes/99999",
        json={"name": "New Name"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_note(client, test_house_for_notes, test_user_for_notes):
    """Test deleting a consumable note."""
    # Create a note
    create_response = await client.post(
        "/api/v1/consumable-notes",
        json={
            "house_id": test_house_for_notes["id"],
            "name": "To be deleted",
            "created_by": test_user_for_notes["id"],
        },
    )
    note = create_response.json()

    # Delete the note
    response = await client.delete(f"/api/v1/consumable-notes/{note['id']}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get("/api/v1/consumable-notes")
    data = get_response.json()
    assert not any(n["id"] == note["id"] for n in data["items"])


@pytest.mark.asyncio
async def test_delete_note_not_found(client):
    """Test deleting non-existent note."""
    response = await client.delete("/api/v1/consumable-notes/99999")
    assert response.status_code == 404
