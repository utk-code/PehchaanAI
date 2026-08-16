"""Tests for the rule-based investigation report endpoint.

Uses the shared in-memory SQLite engine and auth fixtures from conftest.
"""

from __future__ import annotations

import uuid

import numpy as np
from fastapi.testclient import TestClient

from backend.database.models import FaceRecord

EMBEDDING_DIM = 512


def _unit_vector(rng: np.random.Generator) -> list[float]:
    vec = rng.normal(size=EMBEDDING_DIM)
    vec = vec / np.linalg.norm(vec)
    return [float(v) for v in vec]


def _perturbed(
    base: list[float], rng: np.random.Generator, amount: float
) -> list[float]:
    vec = np.asarray(base, dtype=np.float64) + rng.normal(
        scale=amount, size=EMBEDDING_DIM
    )
    vec = vec / np.linalg.norm(vec)
    return [float(v) for v in vec]


def _build_corpus() -> dict[str, tuple[int, list[float]]]:
    """A exact match (A), a near match (B), and an anti-match (C)."""
    rng = np.random.default_rng(7)
    query = _unit_vector(rng)
    return {
        "person_A": (7, query),
        "person_B": (18, _perturbed(query, rng, amount=0.02)),
        "person_C": (45, [-v for v in query]),
    }


def _seed_corpus(db_session, corpus: dict) -> None:
    for i, (person_id, (age, embedding)) in enumerate(corpus.items()):
        db_session.add(
            FaceRecord(
                person_id=person_id,
                age=age,
                capture_year=2000 + age,
                dataset="FGNET",
                photo_path=f"{person_id}.jpg",
                face_embedding=embedding,
            )
        )
    db_session.commit()


def _create_case(client: TestClient, auth_headers, embedding: list[float]) -> str:
    resp = client.post(
        "/cases",
        json={
            "query_name": "Missing Child",
            "query_age": 7,
            "face_embedding": embedding,
            "photo_path": "uploads/test.jpg",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_report_requires_auth(client: TestClient) -> None:
    resp = client.get(f"/reports/{uuid.uuid4()}")
    assert resp.status_code == 401


def test_report_missing_case_404(client: TestClient, auth_headers) -> None:
    resp = client.get(f"/reports/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


def test_report_blocks_foreign_case(
    client: TestClient, auth_headers, db_session
) -> None:
    corpus = _build_corpus()
    case_id = _create_case(client, auth_headers, corpus["person_A"][1])

    other = client.post(
        "/auth/register",
        json={
            "email": "other@example.org",
            "password": "StrongPass123!",
            "full_name": "Other Investigator",
        },
    )
    assert other.status_code == 201
    token_b = other.json()["access_token"]

    resp = client.get(
        f"/reports/{case_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 404


def test_report_generates_real_findings(
    client: TestClient, auth_headers, db_session
) -> None:
    corpus = _build_corpus()
    _seed_corpus(db_session, corpus)
    case_id = _create_case(client, auth_headers, corpus["person_A"][1])

    resp = client.get(f"/reports/{case_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()

    assert body["case_id"] == case_id
    assert body["query_name"] == "Missing Child"
    assert body["query_age"] == 7
    assert body["total_records"] == 3
    assert body["total_candidates"] == 2  # A and B; C filtered by threshold
    assert body["high_confidence"] == 2
    assert body["medium_confidence"] == 0
    assert body["low_confidence"] == 0
    assert body["top_match_similarity"] >= 0.99

    assert len(body["candidates"]) == 2
    top, second = body["candidates"]
    assert top["person_id"] == "person_A"
    assert top["face_similarity"] >= second["face_similarity"]
    assert top["photo_path"].startswith("http")

    assert body["summary"]
    assert body["findings"]
    assert body["recommendations"]
    assert body["next_steps"]


def test_report_empty_corpus(client: TestClient, auth_headers) -> None:
    corpus = _build_corpus()
    case_id = _create_case(client, auth_headers, corpus["person_A"][1])

    resp = client.get(f"/reports/{case_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()

    assert body["total_records"] == 0
    assert body["total_candidates"] == 0
    assert body["top_match_similarity"] == 0.0
    assert "No corpus candidates" in body["summary"]
    assert body["findings"]
    assert body["recommendations"]
    assert body["next_steps"]


def test_report_does_not_leak_foreign_case_identity(
    client: TestClient, auth_headers
) -> None:
    """Foreign cases are indistinguishable from missing ones (404)."""
    corpus = _build_corpus()
    case_id = _create_case(client, auth_headers, corpus["person_A"][1])

    other = client.post(
        "/auth/register",
        json={
            "email": "leak@example.org",
            "password": "StrongPass123!",
            "full_name": "Leak Checker",
        },
    )
    token_b = other.json()["access_token"]
    resp = client.get(
        f"/reports/{case_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()
