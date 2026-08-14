"""Pydantic schemas for Case and face embedding API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    """Payload for creating a new missing child case."""

    child_name_encrypted: str = Field(
        min_length=1, max_length=255, description="Encrypted child name"
    )
    age_at_disappearance: int = Field(
        ge=0, le=18, description="Child's age when they went missing"
    )
    date_missing: date = Field(description="Date the child went missing")
    location: str = Field(
        min_length=1, max_length=255, description="Location of disappearance"
    )
    notes: Optional[str] = Field(
        default=None, max_length=5000, description="Additional notes"
    )
    face_embedding: list[float] = Field(
        min_length=512,
        max_length=512,
        description="512-dimensional face embedding vector",
    )
    photo_path: str = Field(
        min_length=1, max_length=500, description="Path to uploaded photo"
    )


class CaseUpdate(BaseModel):
    """Payload for updating an existing case."""

    child_name_encrypted: Optional[str] = Field(
        default=None, min_length=1, max_length=255
    )
    age_at_disappearance: Optional[int] = Field(default=None, ge=0, le=18)
    date_missing: Optional[date] = None
    location: Optional[str] = Field(default=None, min_length=1, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[str] = Field(default=None, pattern="^(active|closed|archived)$")


class CaseRead(BaseModel):
    """Response model for a case."""

    id: str
    investigator_id: str
    child_name_encrypted: str
    age_at_disappearance: int
    date_missing: date
    location: str
    notes: Optional[str]
    photo_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CaseListItem(BaseModel):
    """Lightweight case representation for list views."""

    id: str
    child_name_encrypted: str
    age_at_disappearance: int
    date_missing: date
    location: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmbeddingResponse(BaseModel):
    """Response for face embedding endpoint."""

    embedding: list[float] = Field(min_length=512, max_length=512)
    det_score: float
    bbox: list[float]
    quality_pass: bool
    num_faces: int


class PhotoUploadResponse(BaseModel):
    """Response for photo upload with embedding."""

    embedding: list[float] = Field(min_length=512, max_length=512)
    det_score: float
    bbox: list[float]
    quality_pass: bool
    num_faces: int
    case_id: Optional[str] = None
