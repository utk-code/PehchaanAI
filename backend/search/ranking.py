"""Cosine similarity utility for face embeddings.

Multi-factor ranking has been removed from the MVP.
The core retrieval uses pure cosine similarity between face embeddings.
This module is kept for future extensibility if a validated multimodal model
is developed.
"""

from __future__ import annotations

import numpy as np


def cosine_similarity(
    a: list[float] | np.ndarray, b: list[float] | np.ndarray
) -> float:
    """Return the cosine similarity between two vectors in [-1, 1]."""
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))
