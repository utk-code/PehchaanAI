"""Pydantic schemas for age progression."""

from pydantic import BaseModel


class AgeEstimate(BaseModel):
    """Age estimation result."""
    estimated_age: int


class AgeSearchRequest(BaseModel):
    """Request for age-progressed search."""
    query_embedding: list[float]
    current_age: int | None = None