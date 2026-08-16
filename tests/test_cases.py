"""Tests for case management and face embedding endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# Fixtures (client, auth_token, auth_headers) are provided by tests/conftest.py


def test_create_case_with_embedding(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test creating a case with a pre-computed embedding."""
    payload = {
        "query_name": "query_001",
        "query_age": 7,
        "query_date": "2024-01-15",
        "query_location": "New Delhi, India",
        "notes": "Test query",
        "face_embedding": [0.1] * 512,  # Dummy 512-d vector
        "photo_path": "/uploads/test.jpg",
    }
    response = client.post("/cases", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["query_name"] == "query_001"
    assert data["query_age"] == 7
    assert data["query_location"] == "New Delhi, India"
    assert data["status"] == "active"
    assert "id" in data


def test_create_case_invalid_embedding_dim(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test that case creation rejects non-512 embeddings."""
    payload = {
        "query_name": "test",
        "query_age": 5,
        "face_embedding": [0.1] * 256,  # Wrong dimension
        "photo_path": "/uploads/test.jpg",
    }
    response = client.post("/cases", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_create_case_unauthorized(client: TestClient) -> None:
    """Test that case creation requires authentication."""
    payload = {
        "query_name": "test",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 401


def test_list_cases(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test listing cases for the current investigator."""
    # Create a case first
    payload = {
        "query_name": "list_test",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    client.post("/cases", json=payload, headers=auth_headers)

    response = client.get("/cases", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_case(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test retrieving a specific case."""
    payload = {
        "query_name": "get_test",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=auth_headers)
    case_id = create_resp.json()["id"]

    response = client.get(f"/cases/{case_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == case_id
    assert data["query_name"] == "get_test"


def test_get_case_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test retrieving a non-existent case."""
    response = client.get(
        "/cases/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert response.status_code == 404


def test_get_case_forbidden(client: TestClient) -> None:
    """Test that a user cannot access another user's case."""
    # Create case with user 1
    token1 = client.post(
        "/auth/register",
        json={
            "email": "user1@example.org",
            "password": "StrongPass123!",
            "full_name": "User One",
        },
    ).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    payload = {
        "query_name": "forbidden_test",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=headers1)
    case_id = create_resp.json()["id"]

    # Try to access with user 2
    token2 = client.post(
        "/auth/register",
        json={
            "email": "user2@example.org",
            "password": "StrongPass123!",
            "full_name": "User Two",
        },
    ).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    response = client.get(f"/cases/{case_id}", headers=headers2)
    assert response.status_code == 403


def test_update_case(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test updating a case."""
    payload = {
        "query_name": "update_test",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=auth_headers)
    case_id = create_resp.json()["id"]

    update_payload = {"query_age": 10, "notes": "Updated notes"}
    response = client.patch(
        f"/cases/{case_id}", json=update_payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_age"] == 10
    assert data["notes"] == "Updated notes"


def test_delete_case(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Test soft-deleting a case."""
    payload = {
        "query_name": "delete_test",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/test.jpg",
    }
    create_resp = client.post("/cases", json=payload, headers=auth_headers)
    case_id = create_resp.json()["id"]

    response = client.delete(f"/cases/{case_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's soft-deleted (should return 404 or 403)
    get_resp = client.get(f"/cases/{case_id}", headers=auth_headers)
    assert get_resp.status_code in (404, 403)


def test_upload_photo_endpoint_requires_auth(client: TestClient) -> None:
    """Test that photo upload requires authentication."""
    response = client.post("/cases/photo/upload")
    assert response.status_code == 401


def test_extract_embedding_endpoint_requires_auth(client: TestClient) -> None:
    """Test that embedding extraction requires authentication."""
    response = client.post("/cases/photo/embedding")
    assert response.status_code == 401


# --------------------------------------------------------------------------- #
# Photo endpoints with a stubbed pipeline
# --------------------------------------------------------------------------- #
def test_extract_embedding_success(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Embedding extraction returns the pipeline embedding and metadata."""
    fake_pipeline.embedding = [0.1] * 512

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/embedding",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["embedding"] == [0.1] * 512
    assert data["quality_pass"] is True
    assert data["num_faces"] == 1
    assert data["det_score"] == 0.99


def test_upload_photo_no_face_returns_400(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Upload with an undetectable face is rejected with a 400."""
    from backend.face.exceptions import NoFaceFoundError

    fake_pipeline.error = NoFaceFoundError("No face detected in image")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/upload",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "No face detected" in response.json()["detail"]


def test_upload_photo_low_quality_returns_400(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Upload with a low-quality face is rejected with a 400."""
    from backend.face.exceptions import LowQualityFaceError

    fake_pipeline.error = LowQualityFaceError("blurry")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/upload",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "Face quality check failed: blurry" in response.json()["detail"]


def test_upload_photo_detection_error_returns_400(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Upload with a processing failure is rejected with a 400."""
    from backend.face.exceptions import FaceDetectionError

    fake_pipeline.error = FaceDetectionError("decode exploded")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/upload",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "Face processing failed: decode exploded" in response.json()["detail"]


def test_upload_photo_create_case_without_name_returns_422(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """create_case=true requires a query_name."""
    fake_pipeline.embedding = [0.1] * 512

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/upload",
            params={"create_case": True},
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 422
    assert "query_name required" in response.json()["detail"]


def test_upload_photo_without_create_case_returns_no_case(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline, tmp_path
) -> None:
    """create_case=false returns case_id=None and stores no case."""
    from unittest.mock import patch

    fake_pipeline.embedding = [0.1] * 512

    with patch("backend.cases.routes.UPLOAD_DIR", tmp_path):
        with open("test_images/lenna.png", "rb") as image_file:
            response = client.post(
                "/cases/photo/upload",
                files={"file": ("lenna.png", image_file, "image/png")},
                headers=auth_headers,
            )
    assert response.status_code == 200
    assert response.json()["case_id"] is None
    assert client.get("/cases", headers=auth_headers).json() == []


# --------------------------------------------------------------------------- #
# File validation helper
# --------------------------------------------------------------------------- #
def test_validate_image_file_rejects_non_image() -> None:
    """Non-image MIME types are rejected with 415."""
    from fastapi import HTTPException

    from backend.cases.routes import _validate_image_file

    class FakeFile:
        content_type = "text/plain"
        size = 1024

    with pytest.raises(HTTPException) as exc_info:
        _validate_image_file(FakeFile())  # type: ignore[arg-type]
    assert exc_info.value.status_code == 415


def test_validate_image_file_rejects_oversized() -> None:
    """Files over 10MB are rejected with 413."""
    from fastapi import HTTPException

    from backend.cases.routes import _validate_image_file

    class FakeFile:
        content_type = "image/jpeg"
        size = 11 * 1024 * 1024

    with pytest.raises(HTTPException) as exc_info:
        _validate_image_file(FakeFile())  # type: ignore[arg-type]
    assert exc_info.value.status_code == 413


def test_validate_image_file_accepts_image() -> None:
    """A valid image passes validation."""
    from backend.cases.routes import _validate_image_file

    class FakeFile:
        content_type = "image/png"
        size = 2048

    assert _validate_image_file(FakeFile()) is None  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Case photo URL helpers
# --------------------------------------------------------------------------- #
def test_photo_url_empty_stored_returns_empty() -> None:
    """An empty stored path yields an empty photo URL."""
    from starlette.requests import Request

    from backend.cases.routes import _photo_url

    request = Request({"type": "http", "method": "GET", "path": "/", "root_path": ""})
    assert _photo_url(request, "") == ""


def test_get_case_rewrites_photo_url(client: TestClient, auth_headers) -> None:
    """GET /cases/{id} rewrites stored paths to absolute /uploads URLs."""
    create = client.post(
        "/cases",
        json={
            "query_name": "photo_url_case",
            "face_embedding": [0.1] * 512,
            "photo_path": "/uploads/stored.jpg",
        },
        headers=auth_headers,
    )
    case_id = create.json()["id"]
    response = client.get(f"/cases/{case_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["photo_path"].endswith("/uploads/stored.jpg")


def test_create_case_keeps_remote_photo_url(client: TestClient, auth_headers) -> None:
    """Photo paths that are already absolute URLs pass through unchanged."""
    create = client.post(
        "/cases",
        json={
            "query_name": "remote_photo_case",
            "face_embedding": [0.1] * 512,
            "photo_path": "https://example.com/photos/img.jpg",
        },
        headers=auth_headers,
    )
    assert create.status_code == 201
    assert create.json()["photo_path"] == "https://example.com/photos/img.jpg"


# --------------------------------------------------------------------------- #
# Remaining error-path coverage
# --------------------------------------------------------------------------- #
def test_extract_embedding_no_face_returns_400(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Embedding extraction surfaces NoFaceFoundError as a 400."""
    from backend.face.exceptions import NoFaceFoundError

    fake_pipeline.error = NoFaceFoundError("No face detected in image")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/embedding",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "No face detected" in response.json()["detail"]


def test_extract_embedding_low_quality_returns_400(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Embedding extraction surfaces LowQualityFaceError as a 400."""
    from backend.face.exceptions import LowQualityFaceError

    fake_pipeline.error = LowQualityFaceError("blurry")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/embedding",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "Face quality check failed: blurry" in response.json()["detail"]


def test_extract_embedding_detection_error_returns_400(
    client: TestClient, auth_headers: dict[str, str], fake_pipeline
) -> None:
    """Embedding extraction surfaces FaceDetectionError as a 400."""
    from backend.face.exceptions import FaceDetectionError

    fake_pipeline.error = FaceDetectionError("decode exploded")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/cases/photo/embedding",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "Face processing failed: decode exploded" in response.json()["detail"]


def test_list_cases_by_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    """list_cases filters by status when status_filter is provided."""
    payload = {
        "query_name": "status_case",
        "face_embedding": [0.1] * 512,
        "photo_path": "/uploads/status.jpg",
    }
    created = client.post("/cases", json=payload, headers=auth_headers).json()

    active = client.get(
        "/cases", params={"status_filter": "active"}, headers=auth_headers
    )
    archived = client.get(
        "/cases", params={"status_filter": "archived"}, headers=auth_headers
    )
    assert any(c["id"] == created["id"] for c in active.json())
    assert all(c["id"] != created["id"] for c in archived.json())


def test_update_case_not_found(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Updating a non-existent case returns 404."""
    response = client.patch(
        "/cases/00000000-0000-0000-0000-000000000000",
        json={"notes": "nope"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_case_forbidden(client: TestClient) -> None:
    """A user cannot update another user's case (403)."""
    headers1 = _register_headers(client, "updator@example.org", "Updator")
    created = client.post(
        "/cases",
        json={
            "query_name": "shared_case",
            "face_embedding": [0.1] * 512,
            "photo_path": "/uploads/x.jpg",
        },
        headers=headers1,
    ).json()
    headers2 = _register_headers(client, "updatetarget@example.org", "Target")

    response = client.patch(
        f"/cases/{created['id']}",
        json={"notes": "sneaky"},
        headers=headers2,
    )
    assert response.status_code == 403


def test_delete_case_not_found(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Deleting a non-existent case returns 404."""
    response = client.delete(
        "/cases/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_case_forbidden(client: TestClient) -> None:
    """A user cannot delete another user's case (403)."""
    headers1 = _register_headers(client, "deleter@example.org", "Deleter")
    created = client.post(
        "/cases",
        json={
            "query_name": "delete_me",
            "face_embedding": [0.1] * 512,
            "photo_path": "/uploads/x.jpg",
        },
        headers=headers1,
    ).json()
    headers2 = _register_headers(client, "deletetarget@example.org", "Target")

    response = client.delete(f"/cases/{created['id']}", headers=headers2)
    assert response.status_code == 403


def _register_headers(client: TestClient, email: str, name: str) -> dict[str, str]:
    """Helper to register a throwaway user and return bearer headers."""
    token = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": name,
        },
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
