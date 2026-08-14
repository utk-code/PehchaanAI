import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from backend.database.models import Base  # noqa: E402
from backend.database.session import get_db  # noqa: E402
from backend.main import app  # noqa: E402


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
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


def test_register_user_returns_access_token(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "investigator@example.org",
            "password": "StrongPass123!",
            "full_name": "Case Investigator",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    user_payload = {
        "email": "duplicate@example.org",
        "password": "StrongPass123!",
        "full_name": "Duplicate User",
    }

    first_response = client.post("/auth/register", json=user_payload)
    second_response = client.post("/auth/register", json=user_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_login_returns_access_token_for_valid_credentials(client: TestClient) -> None:
    user_payload = {
        "email": "login@example.org",
        "password": "StrongPass123!",
        "full_name": "Login User",
    }
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        data={
            "username": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={
            "username": "missing@example.org",
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_requires_valid_bearer_token(client: TestClient) -> None:
    user_payload = {
        "email": "me@example.org",
        "password": "StrongPass123!",
        "full_name": "Current User",
    }
    register_response = client.post("/auth/register", json=user_payload)
    token = register_response.json()["access_token"]

    unauthorized_response = client.get("/auth/me")
    authorized_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert unauthorized_response.status_code == 401
    assert authorized_response.status_code == 200
    assert authorized_response.json()["email"] == user_payload["email"]
    assert authorized_response.json()["full_name"] == user_payload["full_name"]
