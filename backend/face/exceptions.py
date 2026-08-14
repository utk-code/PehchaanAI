"""Custom exceptions raised by the face processing pipeline."""

from __future__ import annotations


class FaceDetectionError(Exception):
    """Base class for errors raised while processing face images."""


class NoFaceFoundError(FaceDetectionError):
    """Raised when no face is detected in a submitted image."""


class MultipleFacesError(FaceDetectionError):
    """Raised when more than one face is detected and disambiguation fails."""


class LowQualityFaceError(FaceDetectionError):
    """Raised when the detected face does not meet minimum quality thresholds."""
