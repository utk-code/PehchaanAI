"""Unit tests for the face pipeline's pure logic with mocked models.

The InsightFace models are not loaded here; the pipeline is wired to fake
detector/embedder objects so decode, quality checks, alignment fallback, and
embedding normalization are exercised for real.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.face.exceptions import FaceDetectionError, LowQualityFaceError
from backend.face.pipeline import FacePipeline


class FakeFace:
    def __init__(self, bbox, det_score, embedding=None):
        self.bbox = bbox
        self.det_score = det_score
        self.embedding = embedding


class FakeDetector:
    def __init__(self, face, aligned=None, align_raises=False, align_raise_once=False):
        self.face = face
        self.aligned = (
            aligned if aligned is not None else np.zeros((112, 112, 3), np.uint8)
        )
        self.align_raises = align_raises
        self.align_raise_once = align_raise_once
        self.detect_calls = 0
        self.align_calls = 0

    def detect(self, image, max_faces=1):
        self.detect_calls += 1
        return [self.face]

    def get_aligned_face(self, image, face=None):
        self.align_calls += 1
        if self.align_raises:
            raise RuntimeError("alignment backend unavailable")
        if self.align_raise_once and self.align_calls == 1:
            raise RuntimeError("alignment backend unavailable")
        return self.aligned


class FakeEmbedder:
    def __init__(self):
        self.calls = 0

    def embed(self, aligned):
        self.calls += 1
        return np.ones(512, dtype=np.float32) / np.sqrt(512)


def make_pipeline(face, aligned=None, align_raises=False, align_raise_once=False):
    pipeline = FacePipeline.__new__(FacePipeline)
    pipeline._detector = FakeDetector(
        face,
        aligned=aligned,
        align_raises=align_raises,
        align_raise_once=align_raise_once,
    )
    pipeline._embedder = FakeEmbedder()
    pipeline._min_face_pixels = 40
    pipeline._min_det_score = 0.5
    return pipeline


def fake_image() -> np.ndarray:
    return np.zeros((200, 200, 3), dtype=np.uint8)


# --------------------------------------------------------------------------- #
# Decode behaviour
# --------------------------------------------------------------------------- #
def test_process_bytes_empty_payload_raises() -> None:
    with pytest.raises(FaceDetectionError, match="Empty image payload"):
        FacePipeline._decode(b"")


def test_process_bytes_undecodable_payload_raises() -> None:
    with pytest.raises(FaceDetectionError, match="Could not decode image"):
        FacePipeline._decode(b"this is not a jpeg")


def test_process_bytes_valid_payload_returns_image() -> None:
    # A tiny valid PNG encoded to bytes via cv2.imencode
    import cv2

    buf = cv2.imencode(".png", np.zeros((8, 8, 3), dtype=np.uint8) + 255)[1]
    image = FacePipeline._decode(buf.tobytes())
    assert image.shape == (8, 8, 3)


def test_process_bytes_full_flow() -> None:
    """process_bytes decodes then runs the full detection/embedding flow."""
    import cv2

    expected = np.ones(512, dtype=np.float32) / np.sqrt(512)
    pipeline = make_pipeline(
        FakeFace(bbox=[0, 0, 100, 100], det_score=0.99, embedding=expected)
    )
    buf = cv2.imencode(".png", np.zeros((64, 64, 3), dtype=np.uint8))[1]

    result = pipeline.process_bytes(buf.tobytes())

    assert pipeline._detector.detect_calls == 1
    assert result["embedding"] == pytest.approx(expected.tolist())
    assert result["num_faces"] == 1


# --------------------------------------------------------------------------- #
# Quality checks
# --------------------------------------------------------------------------- #
def test_process_image_rejects_undersized_face() -> None:
    pipeline = make_pipeline(FakeFace(bbox=[0, 0, 10, 10], det_score=0.99))
    with pytest.raises(LowQualityFaceError, match="too small"):
        pipeline.process_image(fake_image())


def test_process_image_rejects_low_detection_confidence() -> None:
    pipeline = make_pipeline(FakeFace(bbox=[0, 0, 100, 100], det_score=0.3))
    with pytest.raises(LowQualityFaceError, match="below threshold"):
        pipeline.process_image(fake_image())


# --------------------------------------------------------------------------- #
# Success paths
# --------------------------------------------------------------------------- #
def test_process_image_uses_detector_embedding() -> None:
    expected = np.ones(512, dtype=np.float32) / np.sqrt(512)
    pipeline = make_pipeline(
        FakeFace(bbox=[0, 0, 100, 100], det_score=0.99, embedding=expected)
    )
    result = pipeline.process_image(fake_image())

    assert result["quality_pass"] is True
    assert result["num_faces"] == 1
    assert result["bbox"] == [0.0, 0.0, 100.0, 100.0]
    assert result["det_score"] == 0.99
    assert result["embedding"] == pytest.approx(expected.tolist())
    # No fallback embedding pass was needed
    assert pipeline._embedder.calls == 0


def test_process_image_normalizes_unnormalized_embedding() -> None:
    unnormalized = np.ones(512, dtype=np.float32) * 3.0  # norm = 3*sqrt(512)
    pipeline = make_pipeline(
        FakeFace(bbox=[0, 0, 100, 100], det_score=0.99, embedding=unnormalized)
    )
    result = pipeline.process_image(fake_image())

    embedding = np.asarray(result["embedding"])
    assert np.linalg.norm(embedding) == pytest.approx(1.0, abs=1e-5)


def test_process_image_falls_back_to_embedder() -> None:
    pipeline = make_pipeline(FakeFace(bbox=[0, 0, 100, 100], det_score=0.99))
    assert pipeline._detector.face.embedding is None

    result = pipeline.process_image(fake_image())

    assert pipeline._embedder.calls == 1
    assert pipeline._detector.align_calls == 1
    assert result["embedding"] == pytest.approx(
        (np.ones(512, dtype=np.float32) / np.sqrt(512)).tolist()
    )


def test_process_image_alignment_failure_uses_detector_embedding() -> None:
    expected = np.ones(512, dtype=np.float32) / np.sqrt(512)
    pipeline = make_pipeline(
        FakeFace(bbox=[0, 0, 100, 100], det_score=0.99, embedding=expected),
        align_raises=True,
    )
    result = pipeline.process_image(fake_image())

    # Alignment failed but we never need it: embedding comes from the detector
    assert result["embedding"] == pytest.approx(expected.tolist())
    assert pipeline._embedder.calls == 0


def test_process_image_rescues_alignment_on_second_call() -> None:
    """When alignment fails but is retried for the fallback, it can succeed."""
    pipeline = make_pipeline(
        FakeFace(bbox=[0, 0, 100, 100], det_score=0.99, embedding=None),
        align_raise_once=True,
    )
    result = pipeline.process_image(fake_image())

    # First alignment attempt failed; the rescue call succeeded, then embedder ran
    assert pipeline._detector.align_calls == 2
    assert pipeline._embedder.calls == 1
    assert result["embedding"] == pytest.approx(
        (np.ones(512, dtype=np.float32) / np.sqrt(512)).tolist()
    )
