"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app modules
import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from backend.database.models import Base  # noqa: E402
from backend.database.session import get_db  # noqa: E402
from backend.face.pipeline import (  # noqa: E402
    get_face_pipeline,
    get_soft_face_pipeline,
)
from backend.main import app  # noqa: E402


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Auto-skip integration tests unless explicitly requested.

    The real InsightFace model loads on first use and the corpus search
    depends on a populated database, so these tests stay out of the default
    run. Opt in with:

        python -m pytest tests -m integration -q
    """
    args = config.invocation_params.args
    requested = False
    for i, arg in enumerate(args):
        if arg == "-m":
            requested = i + 1 < len(args) and "integration" in args[i + 1]
        elif arg.startswith("-m="):
            requested = "integration" in arg[3:]

    for item in items:
        if "integration" in item.keywords and not requested:
            item.add_marker(
                pytest.mark.skip(reason="integration tests require -m integration")
            )


@pytest.fixture(scope="session", autouse=True)
def _dispose_module_engine() -> Generator[None, None, None]:
    """Release the module-level engine's connections at session end.

    The app's module-level engine opens SQLite connections on import; disposing
    them avoids ResourceWarnings about unclosed databases.
    """
    yield
    from backend.database.session import engine

    engine.dispose()


@pytest.fixture(name="test_engine")
def test_engine_fixture() -> Generator[Engine, None, None]:
    """Single in-memory SQLite engine shared by the app and test sessions."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="db_session")
def db_session_fixture(test_engine: Engine) -> Generator[Session, None, None]:
    """A direct ORM session on the same engine the app uses.

    Lets tests seed corpus rows (FaceRecord) that API requests will see.
    """
    session = Session(bind=test_engine)
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture(name="client")
def client_fixture(test_engine: Engine) -> Generator[TestClient, None, None]:
    """Test client with SQLite in-memory database."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        class_=Session,
    )

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


class FakePipeline:
    """Deterministic stand-in for the InsightFace pipeline."""

    def __init__(self) -> None:
        self.embedding: list[float] | None = None
        self.error: Exception | None = None
        self.quality_warning: str | None = None

    def process_bytes(self, image_bytes: bytes) -> dict:
        if self.error is not None:
            raise self.error
        if self.embedding is None:
            raise RuntimeError("test error: fake_pipeline.embedding is not set")
        return {
            "embedding": self.embedding,
            "aligned_face": None,
            "bbox": [0.0, 0.0, 64.0, 64.0],
            "det_score": 0.99,
            "num_faces": 1,
            "quality_pass": self.quality_warning is None,
            "quality_warning": self.quality_warning,
        }


@pytest.fixture(name="fake_pipeline")
def fake_pipeline_fixture() -> Generator[FakePipeline, None, None]:
    """Override the face pipeline dependencies with a configurable fake.

    Covers both the strict pipeline (case upload/embedding) and the soft
    pipeline (/search/photo), so tests never load the real InsightFace model.
    """
    pipeline = FakePipeline()
    app.dependency_overrides[get_face_pipeline] = lambda: pipeline
    app.dependency_overrides[get_soft_face_pipeline] = lambda: pipeline
    yield pipeline
    app.dependency_overrides.pop(get_face_pipeline, None)
    app.dependency_overrides.pop(get_soft_face_pipeline, None)


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
