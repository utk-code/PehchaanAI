"""Pydantic schemas for Case and face embedding API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    """Payload for creating a new query case."""

    query_name: str = Field(
        min_length=1, max_length=255, description="Name/identifier for the query"
    )
    query_age: Optional[int] = Field(
        default=None, ge=0, le=100, description="Age in the query photo"
    )
    query_date: Optional[date] = Field(
        default=None, description="Date the query photo was taken"
    )
    query_location: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Location of query photo",
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

    query_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    query_age: Optional[int] = Field(default=None, ge=0, le=100)
    query_date: Optional[date] = None
    query_location: Optional[str] = Field(default=None, min_length=1, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[str] = Field(default=None, pattern="^(active|archived)$")


class CaseRead(BaseModel):
    """Full case representation including embedding."""

    id: str
    investigator_id: str
    query_name: Optional[str] = None
    query_age: Optional[int] = None
    query_date: Optional[datetime] = None
    query_location: Optional[str] = None
    notes: Optional[str] = None
    photo_path: str
    face_embedding: list[float]
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CaseListItem(BaseModel):
    """Lightweight case representation for listing."""

    id: str
    query_name: Optional[str] = None
    query_age: Optional[int] = None
    query_date: Optional[datetime] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmbeddingResponse(BaseModel):
    """Response containing a face embedding and detection metadata."""

    embedding: list[float]
    det_score: float
    bbox: list[float]
    quality_pass: bool
    num_faces: int


class PhotoUploadResponse(BaseModel):
    """Response for photo upload endpoint."""

    embedding: list[float]
    det_score: float
    bbox: list[float]
    quality_pass: bool
    num_faces: int
    case_id: Optional[str] = None
