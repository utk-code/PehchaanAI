"""API routes for rule-based investigation reports.

Reports are generated deterministically from the case record and its live
search results (no LLM call): they summarize how many corpus records were
searched, which candidates ranked highest, and include investigation
recommendations based on the confidence distribution.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.database.models import Case, User
from backend.database.session import get_db
from backend.reports.schemas import ReportCandidate, ReportRead
from backend.search.routes import _rewrite_photo_urls
from backend.search.service import search_by_case

router = APIRouter(prefix="/reports", tags=["reports"])

HIGH_SIMILARITY = 0.6
MEDIUM_SIMILARITY = 0.4
REPORT_TOP_K = 20
REPORT_MIN_SIMILARITY = 0.3


def _confidence_counts(
    similarities: list[float],
) -> tuple[int, int, int]:
    """Bucket candidates into high / medium / low confidence (high, med, low)."""
    high = sum(1 for s in similarities if s >= HIGH_SIMILARITY)
    medium = sum(1 for s in similarities if MEDIUM_SIMILARITY <= s < HIGH_SIMILARITY)
    low = sum(1 for s in similarities if REPORT_MIN_SIMILARITY <= s < MEDIUM_SIMILARITY)
    return high, medium, low


def _fmt_similarity(value: float) -> str:
    return f"{value:.0%}"


@router.get(
    "/{case_id}",
    response_model=ReportRead,
    summary="Generate an investigation report for a case",
)
def generate_report(
    case_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportRead:
    """Build a report from the case record and its current search results."""
    case = db.get(Case, case_id)
    if case is None or case.investigator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )
    if case.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    response = search_by_case(
        db,
        case_id,
        top_k=REPORT_TOP_K,
        min_similarity=REPORT_MIN_SIMILARITY,
    )
    response = _rewrite_photo_urls(response, request)

    similarities = [r.face_similarity for r in response.results]
    high, medium, low = _confidence_counts(similarities)
    top_sim = similarities[0] if similarities else 0.0

    candidates = [
        ReportCandidate(
            rank=rank,
            record_id=r.record_id,
            person_id=r.person_id,
            age=r.age,
            dataset=r.dataset,
            face_similarity=r.face_similarity,
            photo_path=r.photo_path,
        )
        for rank, r in enumerate(response.results, 1)
    ]

    name = case.query_name or "this case"
    age = f" (age {case.query_age})" if case.query_age is not None else ""
    if not candidates:
        summary = (
            f"No corpus candidates matched {name}{age} above the "
            f"similarity threshold ({REPORT_MIN_SIMILARITY:.0%}). Consider "
            "re-uploading a clearer query photo or expanding the reference corpus."
        )
    else:
        top = candidates[0]
        summary = (
            f"{response.total_records} reference records were searched for "
            f"{name}{age}. The top match is person {top.person_id} "
            f"at {_fmt_similarity(top.face_similarity)} similarity "
            f"(age {top.age}, {top.dataset})."
        )

    findings = [
        "Face detection and embedding extraction succeeded on the query image.",
        f"{len(candidates)} candidate match(es) found across "
        f"{response.total_records} reference records.",
    ]
    if candidates:
        findings.append(
            f"Confidence distribution: {high} high, {medium} medium, and "
            f"{low} low confidence candidate(s)."
        )
    else:
        findings.append("No candidate exceeded the minimum similarity threshold.")

    recommendations = [
        "Prioritize candidates with at least 60% similarity for immediate review.",
    ]
    if high == 0:
        recommendations.append(
            "Consider age-progression analysis, since the top match did not "
            "reach high confidence."
        )
    recommendations.append(
        "Cross-reference top candidates with external missing-person records."
    )

    next_steps = [
        "Review the candidate photo gallery below.",
        "Coordinate with field investigators to verify the top matches.",
        "Update the case status as the investigation progresses.",
    ]

    return ReportRead(
        case_id=case.id,
        query_name=case.query_name,
        query_age=case.query_age,
        query_location=case.query_location,
        query_date=case.query_date,
        generated_at=datetime.now(timezone.utc),
        total_records=response.total_records,
        total_candidates=len(candidates),
        top_match_similarity=top_sim,
        high_confidence=high,
        medium_confidence=medium,
        low_confidence=low,
        summary=summary,
        findings=findings,
        candidates=candidates,
        recommendations=recommendations,
        next_steps=next_steps,
    )
