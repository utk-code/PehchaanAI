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
from backend.face.pipeline import FacePipeline, get_face_pipeline
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    pipeline: FacePipeline = Depends(get_face_pipeline),
    request: Request = None,
) -> SearchResponse:
    """Upload a photo, extract face embedding, then search the face corpus."""
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

    response = search_face_records(
        db,
        query_embedding=result["embedding"],
        top_k=top_k,
        min_similarity=min_similarity,
    )
    return _rewrite_photo_urls(response, request)
