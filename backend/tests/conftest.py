"""Pytest configuration and shared fixtures for SIRMS backend tests.

Provides:
- Async test session and event loop fixtures
- Test database setup and teardown
- AsyncClient with and without authentication
- Test data factories
- User/token fixtures for authenticated tests
"""

import asyncio
import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.compiler import compiles

from main import create_app
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.models.security import User


# Test database configuration
settings = get_settings()
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SCHEMAS = ("master", "security", "common", "infrastructure", "asset", "incident")


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def register_sqlite_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function("gen_random_uuid", 0, lambda: str(uuid4()))
    
    # Create tables
    async with engine.begin() as conn:
        for schema in TEST_SCHEMAS:
            await conn.execute(text(f"ATTACH DATABASE ':memory:' AS {schema}"))
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """Create test session factory."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )


@pytest.fixture
async def test_session(test_session_factory):
    """Provide test database session for each test."""
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def app():
    """Create and configure test application."""
    return create_app()


@pytest.fixture
async def client(app, test_session):
    """Create async test client without authentication."""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user_data():
    """Fixture providing test user data."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "TestPassword123!",
    }


@pytest.fixture
async def test_admin_data():
    """Fixture providing test admin user data."""
    return {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "full_name": "Test Admin",
        "password": "AdminPassword123!",
    }


@pytest.fixture
async def create_test_user(test_session):
    """Factory fixture to create test users in database."""
    async def _create_user(
        username: str = "testuser",
        email: str = "testuser@example.com",
        full_name: str = "Test User",
        is_active: bool = True,
        is_locked: bool = False,
    ) -> User:
        user = User(
            id=uuid4(),
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password("TestPassword123!"),
            is_active=is_active,
            is_locked=is_locked,
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        return user
    
    return _create_user


@pytest.fixture
async def authenticated_client(app, test_session, test_user_data):
    """Create async test client with authentication headers."""
    user = User(
        id=uuid4(),
        username=test_user_data["username"],
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        password_hash=hash_password(test_user_data["password"]),
    )
    test_session.add(user)
    await test_session.commit()

    # Create test user token
    access_token = create_access_token(str(user.id))
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=headers,
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_client(app, test_session, test_admin_data):
    """Create async test client with admin authentication headers."""
    user = User(
        id=uuid4(),
        username=test_admin_data["username"],
        email=test_admin_data["email"],
        full_name=test_admin_data["full_name"],
        password_hash=hash_password(test_admin_data["password"]),
    )
    test_session.add(user)
    await test_session.commit()

    # Create admin user token
    access_token = create_access_token(str(user.id), {"is_admin": True})
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=headers,
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_project_data():
    """Fixture providing test project data."""
    return {
        "project_name": "Test Project",
        "description": "A test project",
        "project_code": "TP001",
    }


@pytest.fixture
async def test_asset_data():
    """Fixture providing test asset data."""
    return {
        "asset_number": "AST-001",
        "asset_name": "Test Asset",
        "description": "A test asset",
        "status_id": 1,  # Would be replaced with actual lookup ID
    }


@pytest.fixture
async def test_incident_data():
    """Fixture providing test incident data."""
    return {
        "incident_title": "Test Incident",
        "description": "A test incident",
        "priority_id": 2,  # Would be replaced with actual lookup ID
        "status_id": 1,
    }


@pytest.fixture
async def test_maintenance_data():
    """Fixture providing test maintenance data."""
    return {
        "checklist_name": "Test Checklist",
        "description": "A test maintenance checklist",
        "frequency_days": 30,
    }


# Marker for tests requiring database
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "db: mark test as requiring database")
    config.addinivalue_line("markers", "auth: mark test as requiring authentication")
