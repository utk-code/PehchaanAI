"""Face detection and alignment using InsightFace."""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from insightface.app import FaceAnalysis
from insightface.utils import face_align

from backend.config import get_settings
from backend.face.exceptions import (
    FaceDetectionError,
    NoFaceFoundError,
)

logger = logging.getLogger(__name__)


class FaceDetector:
    """Wraps InsightFace's FaceAnalysis for face detection and alignment.

    Attributes:
        ctx_id: GPU device id (>= 0) or CPU (-1).
        det_size: Input size for detection model (width, height).
        det_thresh: Detection confidence threshold.
        model_name: InsightFace model pack name (e.g. "buffalo_s", "buffalo_l").
    """

    def __init__(
        self,
        ctx_id: int = -1,
        det_size: tuple[int, int] = (640, 640),
        det_thresh: float = 0.5,
        model_name: str | None = None,
    ) -> None:
        if model_name is None:
            model_name = get_settings().face_model_name
        logger.info("Loading InsightFace model pack %r (ctx_id=%s)", model_name, ctx_id)
        self._app = FaceAnalysis(
            name=model_name,
            providers=(
                ["CUDAExecutionProvider", "CPUExecutionProvider"]
                if ctx_id >= 0
                else ["CPUExecutionProvider"]
            ),
        )
        self._app.prepare(ctx_id=ctx_id, det_size=det_size)
        self._det_thresh = det_thresh

    def detect(self, image: np.ndarray, max_faces: int = 1) -> list[dict]:
        """Detect faces in an image.

        Args:
            image: BGR image as numpy array (H, W, 3).
            max_faces: Maximum number of faces to return (sorted by det_score desc).

        Returns:
            List of face dicts with keys: 'bbox', 'kps', 'det_score', 'embedding', etc.

        Raises:
            NoFaceFoundError: If no faces meet the confidence threshold.
            MultipleFacesError: If more than `max_faces` are found and max_faces == 1.
        """
        faces = self._app.get(image)

        # Filter by detection confidence
        faces = [f for f in faces if f.det_score >= self._det_thresh]
        if not faces:
            raise NoFaceFoundError("No face detected above confidence threshold")

        # Sort by detection score descending
        faces.sort(key=lambda f: f.det_score, reverse=True)

        if max_faces == 1 and len(faces) > 1:
            logger.warning(
                "Multiple faces detected (count=%d); using highest-scoring face.",
                len(faces),
            )
            faces = faces[:1]
        elif len(faces) > max_faces:
            faces = faces[:max_faces]

        return faces

    def get_aligned_face(
        self, image: np.ndarray, face: dict | None = None
    ) -> np.ndarray:
        """Detect (or reuse) the best face and return the aligned 112x112 crop.

        Args:
            image: BGR image as numpy array.
            face: Previously detected face dict (skips re-detection).

        Returns:
            Aligned face image as numpy array (112, 112, 3) in BGR format.

        Raises:
            NoFaceFoundError: If no face is detected.
            FaceDetectionError: If alignment fails.
        """
        if face is None:
            face = self.detect(image, max_faces=1)[0]

        kps = getattr(face, "kps", None)
        if kps is None or len(kps) < 5:
            raise FaceDetectionError("Face alignment failed: missing landmarks")

        # InsightFace's norm_crop performs the standard 112x112 alignment
        # using the first 5 facial keypoints.
        aligned = face_align.norm_crop(image, kps[:5], image_size=112)
        if aligned is None:
            raise FaceDetectionError("Face alignment failed")
        return aligned

    def get_largest_face(self, image: np.ndarray) -> dict:
        """Detect and return the largest face by bounding box area.

        Useful when multiple faces present and we want the most prominent one.

        Args:
            image: BGR image as numpy array.

        Returns:
            Face dict for the largest face.

        Raises:
            NoFaceFoundError: If no faces detected.
        """
        faces = self._app.get(image)
        faces = [f for f in faces if f.det_score >= self._det_thresh]
        if not faces:
            raise NoFaceFoundError("No face detected above confidence threshold")

        # Select face with largest bbox area
        largest = max(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
        )
        return largest


@lru_cache(maxsize=1)
def get_face_detector(
    ctx_id: int = -1,
    det_size: tuple[int, int] = (640, 640),
    det_thresh: float = 0.5,
    model_name: str | None = None,
) -> FaceDetector:
    """Cached singleton factory for FaceDetector.

    If model_name is None, the value from ``FACE_MODEL_NAME`` setting is used.
    """
    return FaceDetector(
        ctx_id=ctx_id,
        det_size=det_size,
        det_thresh=det_thresh,
        model_name=model_name,
    )


def detect_faces(
    image: np.ndarray,
    ctx_id: int = -1,
    det_size: tuple[int, int] = (640, 640),
    det_thresh: float = 0.5,
    max_faces: int = 1,
) -> list[dict]:
    """Convenience function to detect faces using the cached detector."""
    detector = get_face_detector(
        ctx_id=ctx_id, det_size=det_size, det_thresh=det_thresh
    )
    return detector.detect(image, max_faces=max_faces)
