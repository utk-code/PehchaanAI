"""Pydantic schemas for search requests and cosine similarity results."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SearchResult(BaseModel):
    """Single candidate match with cosine similarity score."""

    record_id: str
    person_id: str
    age: int
    capture_year: Optional[int] = None
    dataset: str
    photo_path: str

    # Pure cosine similarity in [0, 1]
    face_similarity: float = Field(description="Cosine similarity of face embeddings")

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """Ranked list of candidate matches by cosine similarity."""

    query_id: Optional[str] = Field(
        default=None, description="Optional associated case id"
    )
    total_records: int = Field(
        description="Number of records considered before ranking"
    )
    results: list[SearchResult] = Field(
        description="Ranked candidate matches by similarity"
    )
    quality_warning: Optional[str] = Field(
        default=None,
        description=(
            "Set when the query face was detected but failed the quality "
            "checks; results may be unreliable"
        ),
    )


class SearchRequest(BaseModel):
    """Request to search the face corpus with a face embedding."""

    face_embedding: list[float] = Field(
        min_length=512,
        max_length=512,
        description="512-dimensional query face embedding",
    )
    top_k: int = Field(
        default=20, ge=1, le=100, description="Maximum number of records to return"
    )
    min_similarity: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Minimum cosine similarity threshold"
    )
