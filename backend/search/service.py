"""High-level search service using cosine similarity search."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Case, FaceRecord
from backend.search.ranking import cosine_similarity
from backend.search.schemas import SearchResponse, SearchResult

logger = logging.getLogger(__name__)


def search_face_records(
    db: Session,
    query_embedding: list[float],
    top_k: int = 20,
    min_similarity: float = 0.3,
) -> SearchResponse:
    records = db.scalars(select(FaceRecord)).all()
    matches: list[SearchResult] = []

    for record in records:
        similarity = cosine_similarity(query_embedding, record.face_embedding)
        if similarity < min_similarity:
            continue
        matches.append(
            SearchResult(
                record_id=record.id,
                person_id=record.person_id,
                age=record.age,
                capture_year=record.capture_year,
                dataset=record.dataset,
                photo_path=record.photo_path,
                face_similarity=round(similarity, 4),
            )
        )

    matches.sort(key=lambda item: item.face_similarity, reverse=True)
    matches = matches[:top_k]

    logger.info(
        "Face search returned %d records (from %d considered), top similarity=%.4f",
        len(matches),
        len(records),
        matches[0].face_similarity if matches else 0.0,
    )

    return SearchResponse(query_id=None, total_records=len(records), results=matches)


def search_by_case(
    db: Session,
    case_id: str,
    top_k: int = 20,
    min_similarity: float = 0.3,
) -> SearchResponse:
    case = db.get(Case, case_id)
    if not case:
        raise ValueError(f"Case {case_id} not found")

    response = search_face_records(
        db,
        query_embedding=case.face_embedding,
        top_k=top_k,
        min_similarity=min_similarity,
    )
    response.query_id = case_id
    return response
