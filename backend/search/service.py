"""High-level search service using pgvector cosine similarity + multi-factor ranking."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.search.ranking import (
    RankingWeights,
    _age_score,
    _date_score,
    _location_score,
    combine_scores,
)
from backend.search.schemas import MatchScore, SearchRequest, SearchResponse

logger = logging.getLogger(__name__)


def search_candidates(
    db: Session,
    request: SearchRequest,
    weights: RankingWeights | None = None,
    min_face_similarity: float = 0.3,
) -> SearchResponse:
    """Search the candidate pool and return ranked multi-factor matches.

    1. Uses pgvector's cosine distance operator (<=>) with IVFFlat index
       to retrieve the top-K candidates by face similarity.
    2. Applies multi-factor ranking (age, location, date) to re-rank and
       compute a composite confidence score.
    3. Returns a SearchResponse with the final ranked list.
    """
    w = weights or RankingWeights()

    # Build the pgvector cosine similarity query
    # We use <=> for cosine distance, so 1 - distance = similarity
    query = text(
        """
        SELECT id, name_encrypted, age_at_record, record_date, location,
               source, photo_path, face_embedding,
               1 - (face_embedding <=> :embedding) AS face_similarity
        FROM candidates
        WHERE 1 - (face_embedding <=> :embedding) >= :min_sim
        ORDER BY face_embedding <=> :embedding
        LIMIT :top_k
    """
    )

    embedding = request.face_embedding
    result = db.execute(
        query,
        {
            "embedding": embedding,
            "min_sim": min_face_similarity,
            "top_k": request.top_k,
        },
    ).fetchall()

    total_considered = len(result)

    ranked: list[MatchScore] = []
    for row in result:
        face_sim = float(row.face_similarity)

        # Sub-scores
        age_s = _age_score(request.age_at_disappearance, row.age_at_record)
        loc_s = _location_score(request.location, row.location)
        date_s = _date_score(request.date_missing, row.record_date)

        combined = combine_scores(face_sim, age_s, loc_s, date_s, w)

        ranked.append(
            MatchScore(
                candidate_id=row.id,
                name_encrypted=row.name_encrypted,
                age_at_record=row.age_at_record,
                record_date=row.record_date,
                location=row.location,
                photo_path=row.photo_path,
                source=row.source,
                face_similarity=round(face_sim, 4),
                age_score=round(age_s, 4),
                location_score=round(loc_s, 4),
                date_score=round(date_s, 4),
                combined_score=combined,
            )
        )

    # Final re-rank by composite score descending
    ranked.sort(key=lambda m: m.combined_score, reverse=True)

    logger.info(
        "Search returned %d candidates (from %d initial), top composite=%.2f",
        len(ranked),
        total_considered,
        ranked[0].combined_score if ranked else 0.0,
    )

    return SearchResponse(
        query_id=None,  # Will be set by the endpoint if linked to a case
        total_candidates=total_considered,
        results=ranked,
    )


def search_by_case(
    db: Session,
    case_id: str,
    top_k: int = 20,
    weights: RankingWeights | None = None,
) -> SearchResponse:
    """Convenience wrapper: search using an existing Case's stored embedding."""
    from backend.database.models import Case

    case = db.get(Case, case_id)
    if not case:
        raise ValueError(f"Case {case_id} not found")

    request = SearchRequest(
        face_embedding=case.face_embedding,
        age_at_disappearance=case.age_at_disappearance,
        location=case.location,
        date_missing=case.date_missing,
        top_k=top_k,
    )

    response = search_candidates(db, request, weights)
    response.query_id = case_id
    return response
