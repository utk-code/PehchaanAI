"""Age progression service using InsightFace's age estimation.

Implements a "multi-age search" strategy:
- Estimate age from uploaded photo
- Search for matches in older age ranges
- Return combined results
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from backend.face.detector import get_face_detector
from backend.search.service import search_face_records
from backend.search.schemas import SearchResponse

logger = logging.getLogger(__name__)


class AgeProgressionService:
    """Lightweight age progression using InsightFace's age estimation."""

    def __init__(self) -> None:
        self._detector = get_face_detector()

    def estimate_age(self, image: np.ndarray) -> Optional[int]:
        """Estimate age from face image using InsightFace."""
        faces = self._detector.detect(image)
        if not faces:
            return None
        return faces[0].age

    def search_with_age_progression(
        self, 
        db, 
        query_embedding: list[float], 
        current_age: Optional[int] = None,
        top_k: int = 20,
        min_similarity: float = 0.3,
    ) -> dict[str, SearchResponse]:
        """Search with age progression by filtering older age ranges."""
        if current_age is None:
            # If no age provided, use multi-age search strategy with weights
            age_ranges = [
                (0, 12, 1.0),    # Child (highest weight)
                (13, 19, 0.9),   # Teen
                (20, 30, 0.8),   # Young adult
                (31, 50, 0.7),   # Adult
                (51, 100, 0.6),  # Senior
            ]
        else:
            # If age provided, search older ranges with weights
            age_ranges = [
                (current_age, min(current_age + 5, 100), 1.0),      # +0-5 years (highest weight)
                (current_age + 5, min(current_age + 15, 100), 0.8),  # +5-15 years
                (current_age + 15, min(current_age + 30, 100), 0.6),  # +15-30 years
            ]

        results = {}
        weighted_results = []
        for min_age, max_age, weight in age_ranges:
            range_name = f"age_{min_age}_to_{max_age}"
            # Filter face records by age range
            filtered_records = self._filter_records_by_age(db, min_age, max_age)
            # Search within this age range
            range_results = self._search_with_records(
                db,
                query_embedding,
                filtered_records,
                top_k=top_k,
                min_similarity=min_similarity,
            )
            results[range_name] = range_results
            
            # Add weight to results for combined ranking
            for result in range_results.results:
                weighted_results.append((result, weight))

        # Sort weighted results by similarity * weight
        weighted_results.sort(key=lambda x: x[0].similarity * x[1], reverse=True)
        
        # Return top_k combined results
        combined_results = [r[0] for r in weighted_results[:top_k]]
        return {"combined": SearchResponse(query_id=None, total_records=len(combined_results), results=combined_results)}

    def _filter_records_by_age(self, db, min_age: int, max_age: int):
        """Filter face records by estimated age range."""
        from backend.database.models import FaceRecord
        from sqlalchemy import select

        # Get all face records with age estimates
        records = db.scalars(select(FaceRecord)).all()
        filtered = []
        for record in records:
            if record.estimated_age is not None and min_age <= record.estimated_age <= max_age:
                filtered.append(record)
        return filtered
        
    def _search_with_records(self, db, query_embedding: list[float], records, top_k: int = 20, min_similarity: float = 0.3):
        """Search within a specific set of records."""
        from backend.search.service import search_face_records
        
        # Create a temporary in-memory search
        if not records:
            from backend.search.schemas import SearchResponse
            return SearchResponse(query_id=None, total_records=0, results=[])
            
        # Vectorized cosine scan
        import numpy as np
        matrix = np.stack([np.asarray(record.face_embedding, dtype=np.float32) for record in records])
        with np.errstate(divide="ignore", invalid="ignore"):
            matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)

        query = np.asarray(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query)
        if query_norm > 0:
            query = query / query_norm

        similarities = matrix @ query
        similarities = np.nan_to_num(similarities, nan=0.0, posinf=0.0, neginf=0.0)

        order = np.argsort(similarities)[::-1]
        matches = []
        for idx in order[:top_k]:
            similarity = float(similarities[idx])
            if similarity < min_similarity:
                continue
            record = records[idx]
            from backend.search.schemas import SearchResult
            matches.append(
                SearchResult(
                    record_id=record.id,
                    person_id=record.person_id,
                    age=record.age,
                    capture_year=record.capture_year,
                    dataset=record.dataset,
                    photo_path=record.photo_path,
                    face_similarity=similarity,
                )
            )
        
        from backend.search.schemas import SearchResponse
        return SearchResponse(query_id=None, total_records=len(records), results=matches)