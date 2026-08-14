"""Tests for vector search request validation and multi-factor ranking.

Note: pgvector-backed vector search requires PostgreSQL, so the database-level
search is validated through unit tests on the ranking utilities and request
schema validation. The endpoint is exercised with a mocked service so the API
contract stays covered without a live pgvector instance.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Fixtures are provided by tests/conftest.py

from backend.search.ranking import (
    RankingWeights,
    _age_score,
    _date_score,
    _location_score,
    combine_scores,
    cosine_similarity,
)
from backend.search.schemas import MatchScore, SearchRequest, SearchResponse


# --------------------------------------------------------------------------- #
# Ranking utility tests
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


def test_age_score_exact() -> None:
    assert _age_score(10, 10) == 1.0


def test_age_score_decay() -> None:
    assert _age_score(10, 20) == 0.0  # 10 year diff -> 0
    assert _age_score(None, 10) == 0.5  # no query -> neutral


def test_location_score_region_overlap() -> None:
    assert _location_score("Mumbai, Maharashtra", "Mumbai, Maharashtra") == 1.0


def test_location_score_no_overlap() -> None:
    score = _location_score("Delhi", "Kolkata, West Bengal")
    assert 0.0 <= score <= 1.0


def test_location_score_neutral_when_no_query() -> None:
    assert _location_score(None, "Delhi") == 0.5


def test_date_score_decay() -> None:
    from datetime import datetime, timezone

    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    near = datetime(2024, 6, 1, tzinfo=timezone.utc)
    far = datetime(2030, 1, 1, tzinfo=timezone.utc)
    assert _date_score(base, near) > _date_score(base, far)
    assert _date_score(None, base) == 0.5


def test_combine_scores_within_range() -> None:
    score = combine_scores(0.9, 0.8, 0.7, 0.6)
    assert 0.0 <= score <= 100.0
    # Face similarity dominates:
    high_face = combine_scores(0.99, 0.0, 0.0, 0.0)
    low_face = combine_scores(0.1, 1.0, 1.0, 1.0)
    assert high_face > low_face


def test_custom_weights_sum_rule() -> None:
    w = RankingWeights(0.8, 0.1, 0.05, 0.05)
    score = combine_scores(1.0, 1.0, 1.0, 1.0, w)
    assert abs(score - 100.0) < 1e-6


# --------------------------------------------------------------------------- #
# Schema validation tests
# --------------------------------------------------------------------------- #
def test_search_request_requires_512_embedding() -> None:
    with pytest.raises(Exception):
        SearchRequest(face_embedding=[0.1] * 256)


def test_search_request_valid() -> None:
    req = SearchRequest(
        face_embedding=[0.1] * 512,
        age_at_disappearance=8,
        location="Delhi",
        top_k=10,
    )
    assert req.top_k == 10


# --------------------------------------------------------------------------- #
# Endpoint tests (service mocked to avoid pgvector dependency)
# --------------------------------------------------------------------------- #
def _fake_response() -> SearchResponse:
    return SearchResponse(
        query_id=None,
        total_candidates=3,
        results=[
            MatchScore(
                candidate_id="c1",
                name_encrypted="child_001",
                age_at_record=8,
                record_date="2024-01-01T00:00:00+00:00",
                location="Delhi",
                photo_path="/uploads/c1.jpg",
                source="seed",
                face_similarity=0.92,
                age_score=0.9,
                location_score=1.0,
                date_score=0.8,
                combined_score=93.4,
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
        "age_at_disappearance": 8,
        "location": "Delhi",
        "date_missing": "2024-01-01T00:00:00Z",
        "top_k": 10,
    }
    with patch(
        "backend.search.routes.search_candidates", return_value=_fake_response()
    ):
        resp = client.post("/search", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_candidates"] == 3
    assert len(data["results"]) == 1
    assert data["results"][0]["combined_score"] == 93.4


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
