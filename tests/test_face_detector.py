"""Unit tests for FaceDetector logic with a fake InsightFace app.

``FaceAnalysis.__init__`` downloads model packs, so the detector is built via
``__new__`` and wired to fake ``_app`` objects. All branching logic (confidence
filtering, ordering, max-faces truncation, alignment, largest-face selection)
is exercised for real.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.face.detector import FaceDetector
from backend.face.exceptions import FaceDetectionError, NoFaceFoundError


class FakeFace:
    def __init__(self, bbox, det_score, kps=None):
        self.bbox = bbox
        self.det_score = det_score
        self.kps = kps


class FakeApp:
    def __init__(self, faces):
        self._faces = faces

    def get(self, image):
        return self._faces


def make_detector(faces, det_thresh: float = 0.5) -> FaceDetector:
    detector = FaceDetector.__new__(FaceDetector)
    detector._app = FakeApp(faces)
    detector._det_thresh = det_thresh
    return detector


def test_detect_returns_single_best_face() -> None:
    low = FakeFace([0, 0, 50, 50], det_score=0.4)  # below threshold
    good = FakeFace([0, 0, 80, 80], det_score=0.9)
    best = FakeFace([0, 0, 90, 90], det_score=0.95)

    detector = make_detector([low, good, best])
    faces = detector.detect(np.zeros((200, 200, 3), dtype=np.uint8))

    assert len(faces) == 1
    assert faces[0] is best


def test_detect_filters_below_conf_threshold() -> None:
    detector = make_detector([FakeFace([0, 0, 50, 50], det_score=0.3)])
    with pytest.raises(NoFaceFoundError, match="confidence threshold"):
        detector.detect(np.zeros((200, 200, 3), dtype=np.uint8))


def test_detect_respects_max_faces() -> None:
    faces = [FakeFace([0, 0, 80, 80], det_score=0.9) for _ in range(3)]
    detector = make_detector(faces)
    result = detector.detect(np.zeros((200, 200, 3), dtype=np.uint8), max_faces=2)
    assert len(result) == 2
    # highest scoring faces first
    assert [f.det_score for f in result] == [0.9, 0.9]


def test_get_aligned_face_detects_when_face_missing() -> None:
    kps = np.array([[50, 50], [150, 50], [100, 100], [60, 150], [140, 150]])
    detector = make_detector([FakeFace([10, 10, 180, 180], det_score=0.99, kps=kps)])

    aligned = detector.get_aligned_face(np.zeros((200, 200, 3), dtype=np.uint8))
    assert aligned.shape == (112, 112, 3)


def test_get_aligned_face_reuses_provided_face() -> None:
    kps = np.array([[50, 50], [150, 50], [100, 100], [60, 150], [140, 150]])
    face = FakeFace([10, 10, 180, 180], det_score=0.99, kps=kps)
    # No faces registered -> reused face must mean no detection is attempted
    detector = make_detector([])

    aligned = detector.get_aligned_face(
        np.zeros((200, 200, 3), dtype=np.uint8), face=face
    )
    assert aligned.shape == (112, 112, 3)


def test_get_aligned_face_missing_landmarks_raises() -> None:
    detector = make_detector([FakeFace([0, 0, 80, 80], det_score=0.99, kps=None)])
    with pytest.raises(FaceDetectionError, match="missing landmarks"):
        detector.get_aligned_face(
            np.zeros((200, 200, 3), dtype=np.uint8),
            face=FakeFace([0, 0, 80, 80], det_score=0.99, kps=None),
        )


def test_get_aligned_face_norm_crop_failure_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kps = np.array([[50, 50], [150, 50], [100, 100], [60, 150], [140, 150]])
    face = FakeFace([10, 10, 180, 180], det_score=0.99, kps=kps)
    detector = make_detector([face])

    monkeypatch.setattr(
        "backend.face.detector.face_align.norm_crop", lambda *a, **k: None
    )
    with pytest.raises(FaceDetectionError, match="alignment failed"):
        detector.get_aligned_face(np.zeros((200, 200, 3), dtype=np.uint8), face=face)


def test_get_largest_face_returns_largest_bbox() -> None:
    small = FakeFace([0, 0, 40, 40], det_score=0.9)
    large = FakeFace([0, 0, 120, 120], det_score=0.85)
    detector = make_detector([small, large])

    face = detector.get_largest_face(np.zeros((200, 200, 3), dtype=np.uint8))
    assert face is large


def test_get_largest_face_no_face_raises() -> None:
    detector = make_detector([FakeFace([0, 0, 40, 40], det_score=0.1)])
    with pytest.raises(NoFaceFoundError):
        detector.get_largest_face(np.zeros((200, 200, 3), dtype=np.uint8))
