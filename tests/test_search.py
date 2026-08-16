"""Tests for vector search request validation and cosine similarity.

Note: pgvector-backed vector search requires PostgreSQL, so the database-level
search is validated through unit tests on the cosine similarity utility and
request schema validation. The endpoint is exercised with a mocked service so
the API contract stays covered without a live pgvector instance.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Fixtures (client, auth_token, auth_headers) are provided by tests/conftest.py

from backend.search.ranking import cosine_similarity
from backend.search.schemas import SearchRequest, SearchResult, SearchResponse


# --------------------------------------------------------------------------- #
# Cosine similarity tests
# --------------------------------------------------------------------------- #
def test_cosine_similarity_identical() -> None:
    a = [1.0, 0.0, 0.0] * 10
    assert abs(cosine_similarity(a, a) - 1.0) < 1e-6


def test_cosine_similarity_orthogonal() -> None:
    a = [1.0, 0.0] * 10
    b = [0.0, 1.0] * 10
    assert abs(cosine_similarity(a, b)) < 1e-6


def test_cosine_similarity_zero_vector() -> None:
    assert cosine_similarity([0.0] * 5, [1.0, 2.0, 3.0, 4.0, 5.0]) == 0.0


# --------------------------------------------------------------------------- #
# Schema validation tests
# --------------------------------------------------------------------------- #
def test_search_request_requires_512_embedding() -> None:
    with pytest.raises(Exception):
        SearchRequest(face_embedding=[0.1] * 256)


def test_search_request_valid() -> None:
    req = SearchRequest(
        face_embedding=[0.1] * 512,
        top_k=10,
        min_similarity=0.5,
    )
    assert req.top_k == 10
    assert req.min_similarity == 0.5


# --------------------------------------------------------------------------- #
# Endpoint tests (service mocked to avoid pgvector dependency)
# --------------------------------------------------------------------------- #
def _fake_response() -> SearchResponse:
    return SearchResponse(
        query_id=None,
        total_records=3,
        results=[
            SearchResult(
                record_id="r1",
                person_id="person_001",
                age=18,
                capture_year=2020,
                dataset="MORPH",
                photo_path="/uploads/r1.jpg",
                face_similarity=0.92,
            )
        ],
    )


def test_search_endpoint_requires_auth(client: TestClient) -> None:
    payload = {"face_embedding": [0.1] * 512}
    resp = client.post("/search", json=payload)
    assert resp.status_code == 401


def test_search_endpoint_success(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    payload = {
        "face_embedding": [0.1] * 512,
        "top_k": 10,
        "min_similarity": 0.3,
    }
    with patch(
        "backend.search.routes.search_face_records", return_value=_fake_response()
    ):
        resp = client.post("/search", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] == 3
    assert len(data["results"]) == 1
    assert data["results"][0]["face_similarity"] == 0.92


def test_search_case_endpoint_forbidden(client: TestClient) -> None:
    # Register a second user, but don't create a case -> 404 path
    token = client.post(
        "/auth/register",
        json={
            "email": "searcher@example.org",
            "password": "StrongPass123!",
            "full_name": "Searcher",
        },
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/search/case/nonexistent", headers=headers)
    assert resp.status_code in (403, 404)


def test_search_endpoint_service_error_returns_400(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """A service-level error is surfaced as a 400 with its message."""
    payload = {"face_embedding": [0.1] * 512}
    with patch(
        "backend.search.routes.search_face_records",
        side_effect=ValueError("bad embedding"),
    ):
        resp = client.post("/search", json=payload, headers=auth_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "bad embedding"


def test_search_case_endpoint_service_error_returns_400(
    client: TestClient, auth_headers: dict[str, str], db_session
) -> None:
    """A search_by_case failure is surfaced as a 400 for the own case."""
    from backend.database.models import Case

    case = Case(
        investigator_id="owner-id",
        query_name="value_error_case",
        photo_path="query.jpg",
        face_embedding=[0.1] * 512,
    )
    # Bind the case to the registered user so ownership checks pass
    me = client.get("/auth/me", headers=auth_headers).json()
    case.investigator_id = me["id"]
    db_session.add(case)
    db_session.commit()

    with patch("backend.search.routes.search_by_case", side_effect=ValueError("boom")):
        resp = client.get(
            f"/search/case/{case.id}",
            params={"min_similarity": 0.0},
            headers=auth_headers,
        )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "boom"
