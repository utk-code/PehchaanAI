"""API routes for case management and face embedding."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.cases.schemas import (
    CaseCreate,
    CaseListItem,
    CaseRead,
    CaseUpdate,
    EmbeddingResponse,
    PhotoUploadResponse,
)
from backend.database.models import Case, User
from backend.database.session import get_db
from backend.face.exceptions import (
    FaceDetectionError,
    LowQualityFaceError,
    NoFaceFoundError,
)
from backend.face.pipeline import FacePipeline, get_face_pipeline

router = APIRouter(prefix="/cases", tags=["cases"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/photo/embedding",
    response_model=EmbeddingResponse,
    summary="Extract face embedding from an uploaded photo",
)
async def extract_embedding(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    pipeline: FacePipeline = Depends(get_face_pipeline),
) -> EmbeddingResponse:
    """Upload a photo and return the 512-d face embedding.

    Does NOT create a case; useful for preview/testing.
    """
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

    return EmbeddingResponse(
        embedding=result["embedding"],
        det_score=result["det_score"],
        bbox=result["bbox"],
        quality_pass=result["quality_pass"],
        num_faces=result["num_faces"],
    )


@router.post(
    "/photo/upload",
    response_model=PhotoUploadResponse,
    summary="Upload photo, extract embedding, and optionally create a case",
)
async def upload_photo(
    file: UploadFile = File(...),
    create_case: bool = False,
    child_name_encrypted: str | None = None,
    age_at_disappearance: int | None = None,
    date_missing: date | None = None,
    location: str | None = None,
    notes: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    pipeline: FacePipeline = Depends(get_face_pipeline),
) -> PhotoUploadResponse:
    """Upload a photo, process it, and optionally create a case.

    If create_case is True, all case fields are required.
    """
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

    # Save uploaded file
    file_ext = Path(file.filename).suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(image_bytes)

    case_id = None
    if create_case:
        if not all(
            [
                child_name_encrypted,
                age_at_disappearance is not None,
                date_missing,
                location,
            ]
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="All case fields required when create_case=true",
            )

        case = Case(
            investigator_id=current_user.id,
            child_name_encrypted=child_name_encrypted,
            age_at_disappearance=age_at_disappearance,
            date_missing=datetime.combine(
                date_missing, datetime.min.time(), tzinfo=timezone.utc
            ),
            location=location,
            notes=notes,
            photo_path=str(file_path),
            face_embedding=result["embedding"],
            status="active",
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        case_id = case.id

    return PhotoUploadResponse(
        embedding=result["embedding"],
        det_score=result["det_score"],
        bbox=result["bbox"],
        quality_pass=result["quality_pass"],
        num_faces=result["num_faces"],
        case_id=case_id,
    )


@router.post(
    "",
    response_model=CaseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new missing child case",
)
def create_case(
    payload: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Case:
    """Create a new case with a pre-computed face embedding."""
    case = Case(
        investigator_id=current_user.id,
        child_name_encrypted=payload.child_name_encrypted,
        age_at_disappearance=payload.age_at_disappearance,
        date_missing=datetime.combine(
            payload.date_missing, datetime.min.time(), tzinfo=timezone.utc
        ),
        location=payload.location,
        notes=payload.notes,
        photo_path=payload.photo_path,
        face_embedding=payload.face_embedding,
        status="active",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get(
    "", response_model=list[CaseListItem], summary="List cases for current investigator"
)
def list_cases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Case]:
    query = select(Case).where(Case.investigator_id == current_user.id)
    if status_filter:
        query = query.where(Case.status == status_filter)
    query = query.order_by(Case.created_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(query))


@router.get("/{case_id}", response_model=CaseRead, summary="Get a case by ID")
def get_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )
    if case.investigator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your case"
        )
    return case


@router.patch("/{case_id}", response_model=CaseRead, summary="Update a case")
def update_case(
    case_id: str,
    payload: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )
    if case.investigator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your case"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)
    return case


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a case",
    response_model=None,
)
def delete_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )
    if case.investigator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your case"
        )

    case.deleted_at = datetime.now(timezone.utc)
    case.status = "archived"
    db.commit()


def _validate_image_file(file: UploadFile) -> None:
    """Validate that the uploaded file is an image."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be an image (JPEG, PNG, etc.)",
        )
    # Limit file size to 10MB
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10MB",
        )
