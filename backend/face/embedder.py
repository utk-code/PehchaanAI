"""Face embedding extraction using InsightFace (ArcFace)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

import cv2
import numpy as np

from backend.face.detector import FaceDetector, get_face_detector
from backend.face.exceptions import FaceDetectionError

logger = logging.getLogger(__name__)


class FaceEmbedder:
    """Extracts 512-dimensional face embeddings from aligned face images.

    Uses InsightFace's ArcFace model (buffalo_l) which produces
    512-d normalized embeddings suitable for cosine similarity search.
    """

    def __init__(self, ctx_id: int = -1) -> None:
        # We reuse the detector's FaceAnalysis instance to avoid loading models twice
        self._detector = get_face_detector(ctx_id=ctx_id)
        # The embedding model is part of the FaceAnalysis app
        self._app = self._detector._app

    def embed(self, aligned_face: np.ndarray) -> np.ndarray:
        """Generate embedding from a pre-aligned 112x112 RGB face.

        Args:
            aligned_face: Aligned face image (112, 112, 3) in RGB format.

        Returns:
            512-dimensional float32 embedding vector (L2 normalized).

        Raises:
            FaceDetectionError: If embedding extraction fails.
        """
        if aligned_face.shape != (112, 112, 3):
            raise FaceDetectionError(
                f"Expected aligned face shape (112, 112, 3), got {aligned_face.shape}"
            )

        # InsightFace expects a list of faces; create a dummy face object
        # with the aligned image and run feature extraction
        try:
            # Convert RGB to BGR for OpenCV/InsightFace internal processing
            face_bgr = cv2.cvtColor(aligned_face, cv2.COLOR_RGB2BGR)
            # Create a minimal face dict with the aligned image
            # We use the internal model directly
            embedding = self._app.models["recognition"].get(face_bgr)
            if embedding is None:
                raise FaceDetectionError("Embedding model returned None")

            # Normalize to unit length (ArcFace outputs are already normalized)
            embedding = embedding.astype(np.float32)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            return embedding

        except Exception as e:
            logger.exception("Failed to extract face embedding")
            raise FaceDetectionError(f"Embedding extraction failed: {e}") from e

    def embed_from_image(
        self,
        image: np.ndarray,
        detector: Optional[FaceDetector] = None,
    ) -> np.ndarray:
        """Detect, align, and embed a face from a full image in one call.

        Args:
            image: BGR image as numpy array (H, W, 3).
            detector: Optional FaceDetector instance (uses cached singleton if None).

        Returns:
            512-dimensional float32 embedding vector (L2 normalized).

        Raises:
            NoFaceFoundError: If no face is detected.
            FaceDetectionError: If alignment or embedding fails.
        """
        if detector is None:
            detector = self._detector

        aligned = detector.get_aligned_face(image)
        return self.embed(aligned)


@lru_cache(maxsize=1)
def get_face_embedder(ctx_id: int = -1) -> FaceEmbedder:
    """Cached singleton factory for FaceEmbedder."""
    return FaceEmbedder(ctx_id=ctx_id)


def embed_face_image(
    image: np.ndarray,
    ctx_id: int = -1,
) -> np.ndarray:
    """Convenience function to embed a face from an image using the cached embedder."""
    embedder = get_face_embedder(ctx_id=ctx_id)
    return embedder.embed_from_image(image)
