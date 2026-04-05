"""Tests for Chat API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_chat(client):
    """Test creating a new chat."""
    # First create a user
    user_response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "chat_test_user",
            "name": "Chat Test User",
            "role": "tenant",
        },
    )
    assert user_response.status_code == 201
    user = user_response.json()

    # Create chat
    response = await client.post(
        "/api/v1/chats",
        json={"user_id": user["id"]},
    )
    assert response.status_code == 201
    chat = response.json()
    assert chat["user_id"] == user["id"]
    assert "id" in chat


@pytest.mark.asyncio
async def test_create_chat_user_not_found(client):
    """Test creating a chat for non-existent user."""
    response = await client.post(
        "/api/v1/chats",
        json={"user_id": 99999},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message(client):
    """Test sending a message to chat."""
    # Create user
    user_response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "msg_test_user",
            "name": "Message Test User",
            "role": "tenant",
        },
    )
    user = user_response.json()

    # Create chat
    chat_response = await client.post(
        "/api/v1/chats",
        json={"user_id": user["id"]},
    )
    chat = chat_response.json()

    # Send message (will fail without LLM API key, but tests the flow)
    response = await client.post(
        f"/api/v1/chats/{chat['id']}/messages",
        json={"content": "Hello!"},
    )
    # Should return 201 even if LLM fails (fallback response)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_messages(client):
    """Test getting chat messages."""
    # Create user
    user_response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "get_msg_user",
            "name": "Get Messages User",
            "role": "tenant",
        },
    )
    user = user_response.json()

    # Create chat
    chat_response = await client.post(
        "/api/v1/chats",
        json={"user_id": user["id"]},
    )
    chat = chat_response.json()

    # Get messages (should have welcome message)
    response = await client.get(f"/api/v1/chats/{chat['id']}/messages")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1  # At least welcome message


@pytest.mark.asyncio
async def test_get_messages_chat_not_found(client):
    """Test getting messages for non-existent chat."""
    response = await client.get("/api/v1/chats/99999/messages")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_chat_not_found(client):
    """Test sending message to non-existent chat."""
    response = await client.post(
        "/api/v1/chats/99999/messages",
        json={"content": "Hello!"},
    )
    assert response.status_code == 404
