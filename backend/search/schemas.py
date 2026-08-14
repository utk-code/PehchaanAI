"""Pydantic schemas for search requests and multi-factor ranked results."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    """Request to search the candidate pool for a missing child."""

    face_embedding: list[float] = Field(
        min_length=512,
        max_length=512,
        description="512-dimensional query face embedding",
    )
    age_at_disappearance: Optional[int] = Field(
        default=None, ge=0, le=18, description="Age of the child at disappearance"
    )
    location: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Last known location of disappearance",
    )
    date_missing: Optional[datetime] = Field(
        default=None, description="Date the child went missing"
    )
    top_k: int = Field(
        default=20, ge=1, le=100, description="Maximum number of candidates to return"
    )


class MatchScore(BaseModel):
    """Multi-factor ranking breakdown for a single candidate match."""

    candidate_id: str
    name_encrypted: str
    age_at_record: int
    record_date: datetime
    location: str
    photo_path: str
    source: str

    # Sub-scores (each in [0, 1])
    face_similarity: float = Field(description="Cosine similarity of face embeddings")
    age_score: float = Field(description="Closeness of recorded age to query age")
    location_score: float = Field(description="Geographic proximity to query location")
    date_score: float = Field(description="Temporal proximity to date missing")

    # Aggregate weighted score (0-100)
    combined_score: float = Field(description="Weighted composite match confidence")

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """Ranked list of candidate matches for a missing child query."""

    query_id: Optional[str] = Field(
        default=None, description="Optional associated case id"
    )
    total_candidates: int = Field(
        description="Number of candidates considered before ranking"
    )
    results: list[MatchScore] = Field(description="Ranked candidate matches")
