"""High-level search service using cosine similarity search."""

from __future__ import annotations

import logging

import numpy as np

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Case, FaceRecord
from backend.search.schemas import SearchResponse, SearchResult

logger = logging.getLogger(__name__)


def search_face_records(
    db: Session,
    query_embedding: list[float],
    top_k: int = 20,
    min_similarity: float = 0.3,
) -> SearchResponse:
    records = db.scalars(select(FaceRecord)).all()
    if not records:
        return SearchResponse(query_id=None, total_records=0, results=[])

    # Vectorized cosine scan: one matrix multiply over all corpus embeddings
    # instead of a per-record Python loop (~2s -> ~20ms for 609 records).
    matrix = np.stack(
        [np.asarray(record.face_embedding, dtype=np.float32) for record in records]
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)

    query = np.asarray(query_embedding, dtype=np.float32)
    query_norm = np.linalg.norm(query)
    if query_norm > 0:
        query = query / query_norm

    similarities = matrix @ query
    similarities = np.nan_to_num(similarities, nan=0.0, posinf=0.0, neginf=0.0)

    order = np.argsort(similarities)[::-1]
    matches: list[SearchResult] = []
    for idx in order[:top_k]:
        similarity = float(similarities[idx])
        if similarity < min_similarity:
            continue
        record = records[idx]
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
