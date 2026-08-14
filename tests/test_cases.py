"""Tests for case management and face embedding endpoints."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app modules
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


def test_create_case_with_embedding(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test creating a case with a pre-computed embedding."""
    payload = {
        "child_name_encrypted": "encrypted_name_123",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-15",
        "location": "New Delhi, India",
        "notes": "Missing from school",
        "face_embedding": [0.1] * 512,  # Dummy 512-d vector
        "photo_path": "/uploads/test.jpg",
    }
    response = client.post("/cases", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["child_name_encrypted"] == "encrypted_name_123"
    assert data["age_at_disappearance"] == 5
    assert data["location"] == "New Delhi, India"
    assert data["status"] == "active"
    assert "id" in data


def test_create_case_invalid_embedding_dim(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test that case creation rejects non-512 embeddings."""
    payload = {
        "child_name_encrypted": "test",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-15",
        "location": "Delhi",
        "face_embedding": [0.1] * 256,  # Wrong dimension
        "photo_path": "/uploads/test.jpg",
    }
    response = client.post("/cases", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_create_case_unauthorized(client: TestClient) -> None:
    """Test that creating a case requires authentication."""
    payload = {
        "child_name_encrypted": "test",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-15",
        "location": "Delhi",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 401


def test_list_cases(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test listing cases for the authenticated user."""
    # Create two cases
    base_payload = {
        "child_name_encrypted": "name",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-15",
        "location": "Delhi",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    client.post(
        "/cases",
        json={**base_payload, "child_name_encrypted": "case1"},
        headers=auth_headers,
    )
    client.post(
        "/cases",
        json={**base_payload, "child_name_encrypted": "case2"},
        headers=auth_headers,
    )

    response = client.get("/cases", headers=auth_headers)
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 2
    assert cases[0]["child_name_encrypted"] == "case2"  # Most recent first
    assert cases[1]["child_name_encrypted"] == "case1"


def test_get_case(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test retrieving a single case by ID."""
    payload = {
        "child_name_encrypted": "test_child",
        "age_at_disappearance": 8,
        "date_missing": "2024-03-20",
        "location": "Mumbai",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=auth_headers)
    case_id = create_resp.json()["id"]

    response = client.get(f"/cases/{case_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == case_id
    assert data["child_name_encrypted"] == "test_child"
    assert data["age_at_disappearance"] == 8
    assert data["location"] == "Mumbai"


def test_get_case_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test 404 for non-existent case."""
    response = client.get("/cases/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404


def test_get_case_forbidden(client: TestClient) -> None:
    """Test that users cannot access other users' cases."""
    # User 1 creates a case
    user1_token = client.post(
        "/auth/register",
        json={"email": "u1@test.com", "password": "Pass123!", "full_name": "User 1"},
    ).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {user1_token}"}
    payload = {
        "child_name_encrypted": "secret",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-01",
        "location": "Delhi",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=headers1)
    case_id = create_resp.json()["id"]

    # User 2 tries to access it
    user2_token = client.post(
        "/auth/register",
        json={"email": "u2@test.com", "password": "Pass123!", "full_name": "User 2"},
    ).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {user2_token}"}

    response = client.get(f"/cases/{case_id}", headers=headers2)
    assert response.status_code == 403


def test_update_case(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test updating a case."""
    payload = {
        "child_name_encrypted": "original",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-15",
        "location": "Delhi",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=auth_headers)
    case_id = create_resp.json()["id"]

    update_payload = {"location": "Mumbai", "notes": "Updated location"}
    response = client.patch(
        f"/cases/{case_id}", json=update_payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Mumbai"
    assert data["notes"] == "Updated location"


def test_delete_case(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test soft-deleting a case."""
    payload = {
        "child_name_encrypted": "to_delete",
        "age_at_disappearance": 5,
        "date_missing": "2024-01-15",
        "location": "Delhi",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=auth_headers)
    case_id = create_resp.json()["id"]

    response = client.delete(f"/cases/{case_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's archived
    get_resp = client.get(f"/cases/{case_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "archived"
    assert get_resp.json()["deleted_at"] is not None


def test_upload_photo_endpoint_requires_auth(client: TestClient) -> None:
    """Test that photo upload requires authentication."""
    # Create a simple test image (1x1 pixel JPEG)
    import io
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("test.jpg", buf, "image/jpeg")}
    response = client.post("/cases/photo/upload", files=files)
    assert response.status_code == 401


def test_extract_embedding_endpoint_requires_auth(client: TestClient) -> None:
    """Test that embedding extraction requires authentication."""
    import io
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("test.jpg", buf, "image/jpeg")}
    response = client.post("/cases/photo/embedding", files=files)
    assert response.status_code == 401


# Note: Full face detection tests require InsightFace models which are heavy.
# These tests verify the API structure; integration tests with real models
# should be run separately with proper test images.
