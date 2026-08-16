"""End-to-end search flow tests.

Covers the core product loop: create a case -> (optionally upload a photo) ->
search the face_records corpus -> retrieve ranked results.

The corpus is seeded directly through the ``db_session`` fixture (same in-memory
SQLite engine the app uses), and photo endpoints replace the heavy InsightFace
pipeline with a deterministic fake via the ``fake_pipeline`` fixture.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

# Fixtures (client, auth_token, auth_headers, db_session, fake_pipeline) are
# provided by tests/conftest.py

from backend.database.models import FaceRecord
from backend.face.exceptions import (
    FaceDetectionError,
    LowQualityFaceError,
    NoFaceFoundError,
)
from backend.search.service import search_by_case, search_face_records

EMBEDDING_DIM = 512


# --------------------------------------------------------------------------- #
# Corpus seeding helpers
# --------------------------------------------------------------------------- #
def _unit_vector(rng: np.random.Generator) -> list[float]:
    """Build a random unit vector of length EMBEDDING_DIM."""
    vec = rng.normal(size=EMBEDDING_DIM)
    vec = vec / np.linalg.norm(vec)
    return [float(v) for v in vec]


def _perturbed(
    base: list[float], rng: np.random.Generator, amount: float
) -> list[float]:
    """Return a normalized vector that is close to (but not equal to) base."""
    vec = np.asarray(base, dtype=np.float64) + rng.normal(
        scale=amount, size=EMBEDDING_DIM
    )
    vec = vec / np.linalg.norm(vec)
    return [float(v) for v in vec]


def build_corpus() -> dict[str, tuple[str, int, list[float]]]:
    """Three-face mini corpus returning {person_id: (dataset, age, embedding)}.

    - person_A embedding == the query embedding (similarity exactly 1.0)
    - person_B embedding is a close perturbation (high, < 1.0)
    - person_C embedding is the negated query (similarity exactly -1.0)
    """
    rng = np.random.default_rng(42)
    query = _unit_vector(rng)
    return {
        "person_A": ("FGNET", 7, query),
        "person_B": ("FGNET", 18, _perturbed(query, rng, amount=0.02)),
        "person_C": ("FGNET", 45, [-v for v in query]),
    }


def seed_corpus(db_session, corpus: dict) -> None:
    """Insert corpus records into the shared test database."""
    for person_id, (dataset, age, embedding) in corpus.items():
        db_session.add(
            FaceRecord(
                person_id=person_id,
                age=age,
                capture_year=2000 + age,
                dataset=dataset,
                photo_path=f"{person_id}.jpg",
                face_embedding=embedding,
            )
        )
    db_session.commit()


def query_embedding(corpus: dict) -> list[float]:
    """Return person_A's embedding (the intended query)."""
    return corpus["person_A"][2]


# --------------------------------------------------------------------------- #
# E2E: create case -> search by case
# --------------------------------------------------------------------------- #
def test_e2e_create_case_then_search_by_case_returns_ranked_results(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
) -> None:
    """Full flow: register -> seed corpus -> create case -> search by case."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)

    create = client.post(
        "/cases",
        json={
            "query_name": "missing_child_001",
            "query_age": 7,
            "query_location": "Kanpur, India",
            "notes": "E2E flow test",
            "face_embedding": query_embedding(corpus),
            "photo_path": "/uploads/query.jpg",
        },
        headers=auth_headers,
    )
    assert create.status_code == 201
    case_id = create.json()["id"]

    response = client.get(
        f"/search/case/{case_id}",
        params={"top_k": 20, "min_similarity": 0.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["query_id"] == case_id
    assert data["total_records"] == 3

    results = data["results"]
    assert len(results) == 2  # person_C filtered out (similarity -1.0)
    assert results[0]["person_id"] == "person_A"
    assert results[0]["face_similarity"] == pytest.approx(1.0, abs=1e-4)
    assert results[1]["person_id"] == "person_B"
    assert results[1]["face_similarity"] < results[0]["face_similarity"]
    assert results[1]["face_similarity"] > 0.9

    # Similarities must be sorted descending
    sims = [r["face_similarity"] for r in results]
    assert sims == sorted(sims, reverse=True)


def test_e2e_search_case_top_k_limits_results(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
) -> None:
    """top_k must cap the number of returned matches."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)

    create = client.post(
        "/cases",
        json={
            "query_name": "topk_test",
            "face_embedding": query_embedding(corpus),
            "photo_path": "/uploads/query.jpg",
        },
        headers=auth_headers,
    )
    case_id = create.json()["id"]

    response = client.get(
        f"/search/case/{case_id}",
        params={"top_k": 1, "min_similarity": 0.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["person_id"] == "person_A"


def test_e2e_search_case_min_similarity_filters_corpus(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
) -> None:
    """min_similarity must remove below-threshold matches."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)

    create = client.post(
        "/cases",
        json={
            "query_name": "threshold_test",
            "face_embedding": query_embedding(corpus),
            "photo_path": "/uploads/query.jpg",
        },
        headers=auth_headers,
    )
    case_id = create.json()["id"]

    response = client.get(
        f"/search/case/{case_id}",
        params={"top_k": 20, "min_similarity": 0.95},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 3
    assert len(data["results"]) == 1
    assert data["results"][0]["person_id"] == "person_A"

    # Impossibly strict threshold (>= 1.0): only the exact duplicate survives,
    # person_B (~0.91) is filtered. sim == threshold passes.
    response = client.get(
        f"/search/case/{case_id}",
        params={"top_k": 20, "min_similarity": 1.0},
        headers=auth_headers,
    )
    data = response.json()
    assert data["total_records"] == 3
    assert len(data["results"]) == 1
    assert data["results"][0]["person_id"] == "person_A"


def test_e2e_search_case_foreign_case_returns_404(
    client: TestClient,
    db_session,
) -> None:
    """A case owned by another user must not be searchable."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)

    headers1 = {
        "Authorization": (
            "Bearer "
            + client.post(
                "/auth/register",
                json={
                    "email": "owner@example.org",
                    "password": "StrongPass123!",
                    "full_name": "Owner",
                },
            ).json()["access_token"]
        )
    }
    create = client.post(
        "/cases",
        json={
            "query_name": "private_case",
            "face_embedding": query_embedding(corpus),
            "photo_path": "/uploads/query.jpg",
        },
        headers=headers1,
    )
    case_id = create.json()["id"]

    headers2 = {
        "Authorization": (
            "Bearer "
            + client.post(
                "/auth/register",
                json={
                    "email": "intruder@example.org",
                    "password": "StrongPass123!",
                    "full_name": "Intruder",
                },
            ).json()["access_token"]
        )
    }
    response = client.get(
        f"/search/case/{case_id}", params={"min_similarity": 0.0}, headers=headers2
    )
    assert response.status_code == 404


def test_e2e_search_case_missing_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Searching a non-existent case returns 404."""
    response = client.get(
        "/search/case/00000000-0000-0000-0000-000000000000",
        params={"min_similarity": 0.0},
        headers=auth_headers,
    )
    assert response.status_code == 404


# --------------------------------------------------------------------------- #
# E2E: upload photo -> search
# --------------------------------------------------------------------------- #
def test_e2e_upload_photo_and_search_returns_ranked_results(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
    fake_pipeline,
) -> None:
    """Upload a photo, let the pipeline produce an embedding, search corpus."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)
    fake_pipeline.embedding = query_embedding(corpus)

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/search/photo",
            params={"top_k": 20, "min_similarity": 0.0},
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 3
    results = data["results"]
    assert len(results) == 2
    assert results[0]["person_id"] == "person_A"
    assert results[0]["face_similarity"] == pytest.approx(1.0, abs=1e-4)
    assert results[1]["person_id"] == "person_B"

    # Corpus photo paths are rewritten to absolute static URLs for the browser
    for result in results:
        assert (
            result["photo_path"]
            == f"http://testserver/ref-images/{result['person_id']}.jpg"
        )


def test_e2e_upload_photo_create_case_then_search_by_case(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
    fake_pipeline,
    tmp_path,
) -> None:
    """Upload with create_case=true -> case persists -> search by case id."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)
    fake_pipeline.embedding = query_embedding(corpus)

    with patch("backend.cases.routes.UPLOAD_DIR", tmp_path):
        with open("test_images/lenna.png", "rb") as image_file:
            upload = client.post(
                "/cases/photo/upload",
                params={
                    "create_case": True,
                    "query_name": "upload_created_case",
                    "query_age": 7,
                },
                files={"file": ("lenna.png", image_file, "image/png")},
                headers=auth_headers,
            )

    assert upload.status_code == 200
    payload = upload.json()
    assert payload["quality_pass"] is True
    assert payload["num_faces"] == 1
    assert payload["case_id"] is not None
    case_id = payload["case_id"]

    # The created case is listed for the investigator
    cases = client.get("/cases", headers=auth_headers).json()
    assert any(case["id"] == case_id for case in cases)

    # And it is searchable
    response = client.get(
        f"/search/case/{case_id}",
        params={"top_k": 20, "min_similarity": 0.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == case_id
    assert data["results"][0]["person_id"] == "person_A"


def test_e2e_search_photo_no_face_returns_400(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
    fake_pipeline,
) -> None:
    """Searching a photo with no detectable face returns a 400."""
    seed_corpus(db_session, build_corpus())
    fake_pipeline.error = NoFaceFoundError("No face detected in image")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/search/photo",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "No face detected" in response.json()["detail"]


def test_e2e_search_photo_low_quality_returns_400(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
    fake_pipeline,
) -> None:
    """Searching a low-quality face returns a 400 with quality detail."""
    seed_corpus(db_session, build_corpus())
    fake_pipeline.error = LowQualityFaceError("Detected face too small")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/search/photo",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "Face quality check failed" in response.json()["detail"]


def test_e2e_search_photo_detection_error_returns_400(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session,
    fake_pipeline,
) -> None:
    """A face-processing failure returns a 400 with processing detail."""
    seed_corpus(db_session, build_corpus())
    fake_pipeline.error = FaceDetectionError("Could not decode image")

    with open("test_images/lenna.png", "rb") as image_file:
        response = client.post(
            "/search/photo",
            files={"file": ("lenna.png", image_file, "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 400
    assert "Face processing failed" in response.json()["detail"]


def test_e2e_search_photo_rejects_non_image(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Non-image uploads are rejected before any face processing."""
    response = client.post(
        "/search/photo",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 415


# --------------------------------------------------------------------------- #
# Service-level integration tests
# --------------------------------------------------------------------------- #
def test_search_face_records_empty_corpus(db_session) -> None:
    """Searching an empty corpus yields zero results and total_records=0."""
    response = search_face_records(
        db_session, query_embedding=build_corpus()["person_A"][2]
    )
    assert response.total_records == 0
    assert response.results == []


def test_search_face_records_returns_all_metadata(db_session) -> None:
    """SearchResult carries corpus metadata (person_id, age, year, dataset)."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)

    response = search_face_records(
        db_session,
        query_embedding=query_embedding(corpus),
        top_k=1,
        min_similarity=0.0,
    )
    assert response.total_records == 3
    match = response.results[0]
    assert match.person_id == "person_A"
    assert match.age == 7
    assert match.capture_year == 2007
    assert match.dataset == "FGNET"
    assert match.photo_path == "person_A.jpg"  # raw path, rewrite happens in routes


def test_search_by_case_sets_query_id(db_session, auth_headers, client) -> None:
    """search_by_case binds the response to the case id."""
    corpus = build_corpus()
    seed_corpus(db_session, corpus)

    create = client.post(
        "/cases",
        json={
            "query_name": "service_test",
            "face_embedding": query_embedding(corpus),
            "photo_path": "/uploads/query.jpg",
        },
        headers=auth_headers,
    )
    case_id = create.json()["id"]

    response = search_by_case(db_session, case_id, min_similarity=0.0)
    assert response.query_id == case_id
    assert response.results[0].person_id == "person_A"


def test_search_by_case_missing_case_raises_value_error(db_session) -> None:
    """search_by_case with an unknown case id raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        search_by_case(
            db_session, "00000000-0000-0000-0000-000000000000", min_similarity=0.0
        )
