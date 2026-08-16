"""Unit tests for FaceEmbedder logic with a fake recognition model."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from backend.face.embedder import FaceEmbedder
from backend.face.exceptions import FaceDetectionError


class FakeRecognitionModel:
    def __init__(self, embedding=None, raises: Exception | None = None):
        self._embedding = embedding
        self._raises = raises
        self.calls = 0

    def get(self, face_bgr):
        self.calls += 1
        if self._raises is not None:
            raise self._raises
        return self._embedding


class FakeDetector:
    def __init__(self, aligned):
        self._aligned = aligned

    def get_aligned_face(self, image):
        return self._aligned


def make_embedder(model: FakeRecognitionModel) -> FaceEmbedder:
    embedder = FaceEmbedder.__new__(FaceEmbedder)
    embedder._app = SimpleNamespace(models={"recognition": model})
    return embedder


def aligned_face() -> np.ndarray:
    return np.zeros((112, 112, 3), dtype=np.uint8)


def test_embed_rejects_wrong_shape() -> None:
    embedder = make_embedder(FakeRecognitionModel())
    with pytest.raises(FaceDetectionError, match="Expected aligned face shape"):
        embedder.embed(np.zeros((64, 64, 3), dtype=np.uint8))


def test_embed_returns_normalized_embedding() -> None:
    model = FakeRecognitionModel(embedding=np.ones(512, dtype=np.float32) * 4.0)
    embedder = make_embedder(model)

    result = embedder.embed(aligned_face())

    assert model.calls == 1
    assert result.shape == (512,)
    assert result.dtype == np.float32
    assert np.linalg.norm(result) == pytest.approx(1.0, abs=1e-5)


def test_embed_handles_zero_embedding() -> None:
    model = FakeRecognitionModel(embedding=np.zeros(512, dtype=np.float32))
    embedder = make_embedder(model)

    result = embedder.embed(aligned_face())

    # zero vector is returned unchanged (nothing to normalize)
    assert np.linalg.norm(result) == 0.0


def test_embed_model_returning_none_raises() -> None:
    embedder = make_embedder(FakeRecognitionModel(embedding=None))
    with pytest.raises(FaceDetectionError, match="returned None"):
        embedder.embed(aligned_face())


def test_embed_model_failure_is_wrapped() -> None:
    model = FakeRecognitionModel(raises=RuntimeError("gpu died"))
    embedder = make_embedder(model)
    with pytest.raises(FaceDetectionError, match="Embedding extraction failed"):
        embedder.embed(aligned_face())


def test_embed_from_image_uses_detector_alignment() -> None:
    model = FakeRecognitionModel(embedding=np.ones(512, dtype=np.float32))
    embedder = make_embedder(model)
    embedder._detector = FakeDetector(aligned=aligned_face())

    result = embedder.embed_from_image(np.zeros((200, 200, 3), dtype=np.uint8))

    assert model.calls == 1
    assert result.shape == (512,)
