"""API routes for candidate vector search and multi-factor ranking."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.database.models import Case, User
from backend.database.session import get_db
from backend.search.ranking import RankingWeights
from backend.search.schemas import (
    SearchRequest,
    SearchResponse,
)
from backend.search.service import search_by_case, search_candidates

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "",
    response_model=SearchResponse,
    summary="Search candidate pool with a face embedding + context",
)
def search(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """Search the candidate pool using vector similarity + multi-factor ranking.

    Accepts a 512-d query embedding plus optional demographic/contextual
    signals (age, location, date) used to refine the composite ranking.
    """
    try:
        return search_candidates(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/case/{case_id}",
    response_model=SearchResponse,
    summary="Search candidate pool using an existing case's embedding",
)
def search_for_case(
    case_id: str,
    top_k: int = 20,
    weights: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """Run the full search pipeline against a stored case.

    Weights can be supplied as a comma-separated string
    ``face,age,location,date`` (e.g. ``0.6,0.2,0.1,0.1``).
    """
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )
    if case.investigator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your case"
        )

    parsed_weights = _parse_weights(weights)
    try:
        return search_by_case(db, case_id, top_k=top_k, weights=parsed_weights)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


def _parse_weights(raw: str | None) -> RankingWeights | None:
    """Parse a 'face,age,location,date' string into RankingWeights."""
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 4:
        raise ValueError("weights must be 'face,age,location,date'")
    try:
        values = [float(p) for p in parts]
    except ValueError as e:
        raise ValueError("weights must be numeric") from e
    if abs(sum(values) - 1.0) > 1e-3:
        raise ValueError("weights must sum to 1.0")
    return RankingWeights(*values[:4])
