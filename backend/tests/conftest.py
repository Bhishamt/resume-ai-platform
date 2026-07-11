"""Pytest fixtures for authentication tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

settings.APP_ENV = "testing"

from app.api.dependencies import get_db  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.main import app  # noqa: E402

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a transactional database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Provide a FastAPI test client with overridden DB dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Register and return a test user with credentials."""
    user_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "SecureP@ss1",
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data


@pytest.fixture
def auth_tokens(client, registered_user):
    """Login the registered user and return tokens."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }


@pytest.fixture
def auth_headers(auth_tokens):
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}
