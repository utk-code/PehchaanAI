"""API routes for age progression."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.age.service import AgeProgressionService
from backend.database.session import get_db
from backend.search.schemas import SearchResponse

router = APIRouter(prefix="/age", tags=["age-progression"])
age_service = AgeProgressionService()


@router.post("/estimate", response_model=dict)
async def estimate_age(
    file: UploadFile,
    db: Session = Depends(get_db),
) -> dict:
    """Estimate age from uploaded face image."""
    import cv2
    import numpy as np

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    age = age_service.estimate_age(image)
    if age is None:
        raise HTTPException(status_code=400, detail="No face detected")

    return {"estimated_age": age}


@router.post("/search", response_model=dict[str, SearchResponse])
async def search_with_age_progression(
    query_embedding: list[float],
    current_age: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict[str, SearchResponse]:
    """Search with age progression by filtering older age ranges."""
    return age_service.search_with_age_progression(
        db, query_embedding, current_age=current_age
    )