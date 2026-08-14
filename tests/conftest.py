"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app modules
import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from backend.database.models import Base  # noqa: E402
from backend.database.session import get_db  # noqa: E402
from backend.main import app  # noqa: E402


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    """Test client with SQLite in-memory database."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="auth_token")
def auth_token_fixture(client: TestClient) -> str:
    """Register a user and return their access token."""
    user_payload = {
        "email": "investigator@example.org",
        "password": "StrongPass123!",
        "full_name": "Test Investigator",
    }
    response = client.post("/auth/register", json=user_payload)
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str) -> dict[str, str]:
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}
