"""Pytest fixtures for backend tests with async database support."""

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from backend.database import Base, get_db
from backend.main import app

# Test database URL - uses the same postgres container but different database
TEST_DATABASE_URL = "postgresql+asyncpg://booking:booking@postgres/booking_test"
# Admin URL to create test database
ADMIN_DATABASE_URL = "postgresql+asyncpg://booking:booking@postgres/postgres"


def pytest_configure(config):
    """Configure pytest-asyncio mode."""
    config.option.asyncio_mode = "auto"


async def _ensure_test_database_exists():
    """Ensure test database exists."""
    admin_engine = create_async_engine(
        ADMIN_DATABASE_URL, echo=False, isolation_level="AUTOCOMMIT"
    )
    try:
        async with admin_engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'booking_test'")
            )
            if not result.scalar():
                # Create test database
                await conn.execute(text("CREATE DATABASE booking_test"))
    finally:
        await admin_engine.dispose()


@pytest_asyncio.fixture
async def engine():
    """Create engine for test database - function scoped to avoid event loop issues."""
    # Ensure test database exists
    await _ensure_test_database_exists()

    # Create engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        # Rollback any changes after test
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """Create test client with overridden database dependency."""
    from httpx import ASGITransport

    async def override_get_db():
        yield db_session

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(engine):
    """Clean all tables before each test."""
    # Create a new session for cleanup
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Truncate all tables
        await session.execute(text("TRUNCATE TABLE bookings, houses, users, tariffs RESTART IDENTITY CASCADE"))
        await session.commit()


@pytest_asyncio.fixture
async def test_user(client):
    """Create a test user and return its data."""
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "test_user_123",
            "name": "Test User",
            "role": "owner",
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def test_house(client, test_user):
    """Create a test house and return its data."""
    response = await client.post(
        "/api/v1/houses",
        json={
            "name": "Test House",
            "description": "A test house",
            "capacity": 6,
            "is_active": True,
            "owner_id": test_user["id"],
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def test_tariff(client):
    """Create a test tariff and return its data."""
    response = await client.post(
        "/api/v1/tariffs",
        json={
            "name": "Adult",
            "amount": 250,
        },
    )
    return response.json()
