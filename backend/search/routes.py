"""API routes for face corpus cosine similarity search."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, status, UploadFile
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.database.models import Case, User
from backend.database.session import get_db
from backend.face.exceptions import (
    FaceDetectionError,
    LowQualityFaceError,
    NoFaceFoundError,
)
from backend.face.pipeline import FacePipeline, get_soft_face_pipeline
from backend.search.schemas import SearchRequest, SearchResponse
from backend.search.service import search_by_case, search_face_records

router = APIRouter(prefix="/search", tags=["search"])


def _rewrite_photo_urls(response: SearchResponse, request: Request) -> SearchResponse:
    """Return absolute URLs for reference corpus images."""
    base = str(request.base_url).rstrip("/")
    for result in response.results:
        if result.photo_path:
            result.photo_path = f"{base}/ref-images/{result.photo_path.strip('/')}"
    return response


@router.post(
    "",
    response_model=SearchResponse,
    summary="Search face corpus with a face embedding",
)
def search(
    payload: SearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """Search the face_records corpus using vector similarity.

    Accepts a 512-d query embedding and returns top-K matches ranked by
    cosine similarity.
    """
    try:
        response = search_face_records(
            db,
            query_embedding=payload.face_embedding,
            top_k=payload.top_k,
            min_similarity=payload.min_similarity,
        )
        return _rewrite_photo_urls(response, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/case/{case_id}",
    response_model=SearchResponse,
    summary="Search face corpus using an existing case's embedding",
)
def search_for_case(
    case_id: str,
    request: Request,
    top_k: int = 20,
    min_similarity: float = 0.3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """Run the search pipeline against a stored case.

    Returns top-K face records most similar to the case's query image.
    """
    case = db.get(Case, case_id)
    if case is None or case.investigator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    try:
        response = search_by_case(
            db, case_id, top_k=top_k, min_similarity=min_similarity
        )
        return _rewrite_photo_urls(response, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/photo",
    response_model=SearchResponse,
    summary="Upload photo, extract embedding, search face corpus",
)
async def search_by_photo(
    file: UploadFile = File(...),
    top_k: int = 20,
    min_similarity: float = 0.3,
    use_age_progression: bool = False,
    estimated_age: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    pipeline: FacePipeline = Depends(get_soft_face_pipeline),
    request: Request = None,
) -> SearchResponse:
    """Upload
    a photo, extract a face embedding, and search the corpus.

    Uses the non-strict pipeline: a detected-but-low-quality face produces a
    ``quality_warning`` on the response instead of a 400. A photo with no
    detectable face (or an undecodable image) is still rejected with a 400.
    """
    from backend.cases.routes import _validate_image_file

    _validate_image_file(file)
    image_bytes = await file.read()

    try:
        result = pipeline.process_bytes(image_bytes)
    except NoFaceFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except LowQualityFaceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Face quality check failed: {e}",
        ) from e
    except FaceDetectionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Face processing failed: {e}",
        ) from e

    # Use estimated age from photo if available and not provided
    if estimated_age is None and result.get("estimated_age") is not None:
        estimated_age = result.get("estimated_age")

    # Use age progression if enabled
    if use_age_progression and estimated_age is not None:
        from backend.age.service import AgeProgressionService
        age_service = AgeProgressionService()
        age_results = age_service.search_with_age_progression(
            db, 
            result["embedding"], 
            current_age=estimated_age,
            top_k=top_k,
            min_similarity=min_similarity
        )
        # Merge results from all age ranges
        all_results = []
        for range_name, range_response in age_results.items():
            all_results.extend(range_response.results)
        
        # Remove duplicates and sort by similarity
        unique_results = {}
        for r in all_results:
            if r.record_id not in unique_results or r.similarity > unique_results[r.record_id].similarity:
                unique_results[r.record_id] = r
        
        # Sort by similarity and take top_k
        merged_results = sorted(unique_results.values(), key=lambda x: x.similarity, reverse=True)[:top_k]
        
        response = SearchResponse(
            query_id=None,
            total_records=len(unique_results),
            results=merged_results
        )
    else:
        response = search_face_records(
            db,
            query_embedding=result["embedding"],
            top_k=top_k,
            min_similarity=min_similarity,
        )
    
    response.quality_warning = result.get("quality_warning")
    return _rewrite_photo_urls(response, request)
