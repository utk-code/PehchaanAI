"""Real-model integration tests for the face + search stack.

These exercise the actual InsightFace model and a throwaway copy of the
live corpus database, proving the model works end to end (not just the
mocked paths in the unit suite). They are auto-skipped and only run when
explicitly requested:

    python -m pytest tests -m integration -q
"""

from __future__ import annotations

import shutil
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.models import Base
from backend.database.session import get_db
from backend.face.pipeline import FacePipeline, get_face_pipeline
from backend.main import app
from backend.search.service import search_face_records

pytestmark = pytest.mark.integration

FGNET_ROOT = Path("FGNET/images")
QUERY_IMG = FGNET_ROOT / "001A08.JPG"
EXPECTED_PERSON = "001"


@pytest.fixture(scope="module")
def real_pipeline() -> FacePipeline:
    """Pipeline backed by the actual InsightFace model (loads weights once)."""
    return FacePipeline()


@pytest.fixture(scope="module")
def real_engine(tmp_path_factory) -> Generator[Engine, None, None]:
    """Engine on a throwaway copy of the live corpus DB.

    Uses a copy so the tests never mutate the real pehchaanai.db file.
    """
    src = Path("pehchaanai.db")
    dst = tmp_path_factory.mktemp("integ") / "corpus.db"
    if src.exists():
        shutil.copy2(src, dst)
    engine = create_engine(
        f"sqlite+pysqlite:///{dst.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


def test_real_pipeline_extracts_embedding(real_pipeline: FacePipeline) -> None:
    """The real model must detect a face and emit a 512-d embedding."""
    result = real_pipeline.process_bytes(QUERY_IMG.read_bytes())
    assert len(result["embedding"]) == 512
    assert result["det_score"] > 0.5
    assert result["quality_pass"] is True
    assert result["num_faces"] == 1


def test_real_search_ranks_query_person_top(
    real_pipeline: FacePipeline, real_engine: Engine
) -> None:
    """Searching a real photo ranks the same person first (cross-age match)."""
    result = real_pipeline.process_bytes(QUERY_IMG.read_bytes())
    session = Session(bind=real_engine)
    try:
        response = search_face_records(
            session,
            query_embedding=result["embedding"],
            top_k=5,
            min_similarity=0.3,
        )
    finally:
        session.close()

    assert response.total_records >= 100
    assert response.results
    assert response.results[0].person_id == EXPECTED_PERSON
    assert response.results[0].face_similarity >= 0.9


@pytest.fixture(scope="module")
def integration_client(
    real_engine: Engine, real_pipeline: FacePipeline
) -> Generator[TestClient, None, None]:
    """TestClient wired to the real pipeline and the corpus DB copy."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=real_engine,
        class_=Session,
    )

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_face_pipeline] = lambda: real_pipeline
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_search_photo_api_with_real_model(integration_client: TestClient) -> None:
    """The /search/photo API works against the real model + corpus."""
    resp = integration_client.post(
        "/auth/register",
        json={
            "email": f"integ_{uuid.uuid4().hex[:10]}@test.dev",
            "password": "StrongPass123!",
            "full_name": "Integration Tester",
        },
    )
    assert resp.status_code == 201
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    with QUERY_IMG.open("rb") as f:
        r = integration_client.post(
            "/search/photo",
            headers=headers,
            files={"file": (QUERY_IMG.name, f, "image/jpeg")},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["total_records"] >= 100
    assert body["results"][0]["person_id"] == EXPECTED_PERSON
