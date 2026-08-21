"""High-level face processing pipeline.

Decode -> detect -> align -> embed -> quality.
"""

from __future__ import annotations

import cv2
import logging
from functools import lru_cache

import numpy as np

from backend.face.detector import get_face_detector
from backend.face.embedder import get_face_embedder
from backend.face.exceptions import (
    FaceDetectionError,
    LowQualityFaceError,
)

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 512


class FacePipeline:
    """Orchestrates the full face processing flow for a single uploaded image.

    Responsibilities:
        1. Decode raw image bytes to a BGR numpy array.
        2. Detect and align the most prominent face.
        3. Extract a 512-d ArcFace embedding.
        4. Run basic quality checks (resolution, detection confidence).
    """

    def __init__(
        self,
        ctx_id: int = -1,
        min_face_pixels: int = 40,
        min_det_score: float = 0.5,
        strict_quality: bool = True,
    ) -> None:
        self._detector = get_face_detector(ctx_id=ctx_id)
        self._embedder = get_face_embedder(ctx_id=ctx_id)
        self._min_face_pixels = min_face_pixels
        self._min_det_score = min_det_score
        self._strict_quality = strict_quality

    def process_bytes(self, image_bytes: bytes) -> dict:
        """Process an uploaded image from raw bytes.

        Args:
            image_bytes: Raw image file bytes (JPEG/PNG/etc.).

        Returns:
            Dict with keys:
                - 'embedding': list[float] of length 512
                - 'aligned_face': np.ndarray (112, 112, 3) RGB, or None
                - 'bbox': list[float] bounding box [x1, y1, x2, y2]
                - 'det_score': float
                - 'num_faces': int
                - 'quality_pass': bool

        Raises:
            FaceDetectionError: On decode failure.
            NoFaceFoundError: If no face is detected.
            LowQualityFaceError: If face fails quality checks.
        """
        image = self._decode(image_bytes)
        return self.process_image(image)

    def process_image(self, image: np.ndarray) -> dict:
        """Process a decoded BGR image array.

        See process_bytes for return shape.
        """
        faces = self._detector.detect(image, max_faces=1)
        face = faces[0]

        # Quality checks. In strict mode a failing face is rejected outright;
        # in soft mode the failure is recorded as a warning so the caller can
        # still search with the (degraded) embedding.
        x1, y1, x2, y2 = face.bbox[:4]
        face_w = x2 - x1
        face_h = y2 - y1
        problems: list[str] = []
        if face_w < self._min_face_pixels or face_h < self._min_face_pixels:
            problems.append(
                f"Detected face too small ({face_w:.0f}x{face_h:.0f}px) "
                f"for reliable matching"
            )
        if face.det_score < self._min_det_score:
            problems.append(
                f"Face detection confidence {face.det_score:.2f} below threshold"
            )
        if problems:
            if self._strict_quality:
                raise LowQualityFaceError(problems[0])
            quality_warning = "; ".join(problems)
        else:
            quality_warning = None

        # Aligned crop is computed best-effort (used only for previews).
        try:
            aligned = self._detector.get_aligned_face(image, face=face)
        except Exception:
            logger.warning("Could not align face; alignment skipped.", exc_info=False)
            aligned = None

        # Prefer the embedding already computed by InsightFace during detection
        # (avoids a second recognition pass).
        embedding = getattr(face, "embedding", None)
        if embedding is None:
            # Fallback: align then embed explicitly. Aligned input is BGR here.
            if aligned is None:
                aligned = self._detector.get_aligned_face(image, face=face)
            embedding = self._embedder.embed(aligned)

        embedding = np.asarray(embedding, dtype=np.float32)
        norm = float(np.linalg.norm(embedding))
        if norm > 0:
            embedding = embedding / norm

        return {
            "embedding": embedding.tolist(),
            "aligned_face": aligned,
            "bbox": face.bbox.tolist(),
            "det_score": float(face.det_score),
            "num_faces": len(faces),
            "quality_pass": not problems,
            "quality_warnings": problems,
            "estimated_age": face.age,
            "estimated_gender": face.sex,
        }

    @staticmethod
    def _decode(image_bytes: bytes) -> np.ndarray:
        """Decode image bytes to a contiguous BGR numpy array."""
        if not image_bytes:
            raise FaceDetectionError("Empty image payload")

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise FaceDetectionError("Could not decode image (unsupported format?)")
        return image


@lru_cache(maxsize=1)
def get_face_pipeline(
    ctx_id: int = -1,
    min_face_pixels: int = 40,
    min_det_score: float = 0.5,
) -> FacePipeline:
    """Cached singleton factory for FacePipeline."""
    return FacePipeline(
        ctx_id=ctx_id,
        min_face_pixels=min_face_pixels,
        min_det_score=min_det_score,
    )


@lru_cache(maxsize=1)
def get_soft_face_pipeline(
    ctx_id: int = -1,
    min_face_pixels: int = 40,
    min_det_score: float = 0.5,
) -> FacePipeline:
    """Cached singleton factory for a non-strict FacePipeline.

    Returns results with a ``quality_warning`` (and ``quality_pass=False``)
    instead of raising :class:`LowQualityFaceError`, so callers can still
    search with a detected-but-degraded face.
    """
    return FacePipeline(
        ctx_id=ctx_id,
        min_face_pixels=min_face_pixels,
        min_det_score=min_det_score,
        strict_quality=False,
    )
