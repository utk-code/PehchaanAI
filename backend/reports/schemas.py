"""Pydantic schemas for generated investigation reports."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportCandidate(BaseModel):
    """A single ranked candidate summarized inside a report."""

    rank: int = Field(ge=1, description="1-based rank by face similarity")
    record_id: str
    person_id: str
    age: int
    dataset: str
    face_similarity: float = Field(
        ge=0.0, le=1.0, description="Cosine similarity of face embeddings"
    )
    photo_path: str = Field(default="", description="Absolute URL of the photo")


class ReportRead(BaseModel):
    """Rule-generated investigation report for a case."""

    case_id: str
    query_name: Optional[str] = None
    query_age: Optional[int] = None
    query_location: Optional[str] = None
    query_date: Optional[datetime] = None
    generated_at: datetime
    total_records: int = Field(description="Corpus records searched")
    total_candidates: int = Field(description="Candidates above threshold")
    top_match_similarity: float = Field(
        ge=0.0, le=1.0, description="Best candidate cosine similarity"
    )
    high_confidence: int = Field(description="Candidates with similarity >= 0.6")
    medium_confidence: int = Field(description="Candidates with similarity 0.4-0.6")
    low_confidence: int = Field(description="Candidates with similarity 0.3-0.4")
    summary: str
    findings: list[str]
    candidates: list[ReportCandidate]
    recommendations: list[str]
    next_steps: list[str]
