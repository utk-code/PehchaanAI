import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    cases: Mapped[list["Case"]] = relationship(back_populates="investigator")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    investigator_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )
    child_name_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    age_at_disappearance: Mapped[int] = mapped_column(nullable=False)
    date_missing: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    face_embedding: Mapped[list[float]] = mapped_column(Vector(512), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    investigator: Mapped["User"] = relationship(back_populates="cases")

    __table_args__ = (
        Index("idx_cases_investigator", "investigator_id"),
        # IVFFlat index for vector similarity search (created via migration)
        # CREATE INDEX idx_cases_embedding ON cases USING ivfflat
        # (face_embedding vector_cosine_ops) WITH (lists = 100);
    )
