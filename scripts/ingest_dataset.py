#!/usr/bin/env python
"""Ingest a research face dataset into the face_records table.

Supports datasets with age labels (e.g., MORPH, CACD, FG-NET, AgeDB).
Expected input format: a CSV with columns:
    image_path, person_id, age, capture_year, dataset

Or a directory structure:
    dataset_name/
        person_id/
            age_image.jpg

Usage:
    python scripts/ingest_dataset.py --csv metadata.csv --images-root /path/to/images
    python scripts/ingest_dataset.py --dataset-dir /path/to/dataset --dataset-name MORPH
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database.models import Base, FaceRecord
from backend.face.pipeline import FacePipeline, get_face_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest face dataset into database")
    parser.add_argument(
        "--database-url",
        default=os.environ.get(
            "DATABASE_URL", "postgresql+psycopg://app:changeme@localhost:5432/appdb"
        ),
        help="Database URL",
    )
    parser.add_argument(
        "--reset", action="store_true", help="Clear face_records table before ingest"
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--csv", type=Path, help="CSV metadata file (columns: image_path, person_id, age, capture_year, dataset)"
    )
    input_group.add_argument(
        "--dataset-dir", type=Path, help="Root directory with person_id/age_image.jpg structure"
    )

    parser.add_argument(
        "--dataset-name",
        default="unknown",
        help="Dataset name (used when --dataset-dir is provided)",
    )
    parser.add_argument(
        "--images-root", type=Path, help="Root directory for images (when using --csv with relative paths)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=50, help="Batch size for embedding extraction"
    )

    return parser.parse_args()


def validate_image(image_path: Path) -> tuple[bool, str]:
    """Quick validation that file exists and is readable."""
    if not image_path.exists():
        return False, f"File not found: {image_path}"
    if image_path.stat().st_size == 0:
        return False, f"Empty file: {image_path}"
    return True, ""


def ingest_from_csv(
    csv_path: Path,
    images_root: Path,
    dataset_name: str,
    db: Session,
    pipeline: FacePipeline,
    batch_size: int = 50,
) -> int:
    """Ingest records from a CSV metadata file."""
    records_to_insert = []
    count = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_path = row["image_path"]
            person_id = row["person_id"]
            age = int(row["age"])
            capture_year = int(row["capture_year"]) if row.get("capture_year") else None
            dataset = row.get("dataset", dataset_name)

            image_path = (images_root / rel_path).resolve()
            valid, msg = validate_image(image_path)
            if not valid:
                print(f"  Skipping {rel_path}: {msg}")
                continue

            records_to_insert.append(
                {
                    "image_path": image_path,
                    "person_id": person_id,
                    "age": age,
                    "capture_year": capture_year,
                    "dataset": dataset,
                    "rel_path": rel_path,
                }
            )

            if len(records_to_insert) >= batch_size:
                count += process_batch(records_to_insert, db, pipeline)
                records_to_insert.clear()

    if records_to_insert:
        count += process_batch(records_to_insert, db, pipeline)

    return count


def ingest_from_directory(
    dataset_dir: Path,
    dataset_name: str,
    db: Session,
    pipeline: FacePipeline,
    batch_size: int = 50,
) -> int:
    """Ingest records from a directory structure: person_id/age_image.jpg"""
    records_to_insert = []
    count = 0

    # Expect: dataset_dir/person_id/age_year.jpg or person_id/age.jpg
    for person_dir in sorted(dataset_dir.iterdir()):
        if not person_dir.is_dir():
            continue
        person_id = person_dir.name

        for img_path in sorted(person_dir.glob("*.jpg")) + sorted(person_dir.glob("*.png")):
            # Try to parse age from filename: e.g., "25.jpg" or "25_2010.jpg"
            stem = img_path.stem
            parts = stem.split("_")
            try:
                age = int(parts[0])
            except ValueError:
                print(f"  Skipping {img_path}: cannot parse age from filename")
                continue

            capture_year = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

            valid, msg = validate_image(img_path)
            if not valid:
                print(f"  Skipping {img_path}: {msg}")
                continue

            records_to_insert.append(
                {
                    "image_path": img_path,
                    "person_id": person_id,
                    "age": age,
                    "capture_year": capture_year,
                    "dataset": dataset_name,
                    "rel_path": img_path.relative_to(dataset_dir).as_posix(),
                }
            )

            if len(records_to_insert) >= batch_size:
                count += process_batch(records_to_insert, db, pipeline)
                records_to_insert.clear()

    if records_to_insert:
        count += process_batch(records_to_insert, db, pipeline)

    return count


def process_batch(
    batch: list[dict],
    db: Session,
    pipeline: FacePipeline,
) -> int:
    """Process a batch of images: extract embeddings and insert into DB."""
    records = []
    for item in batch:
        try:
            image_bytes = item["image_path"].read_bytes()
            result = pipeline.process_bytes(image_bytes)
        except Exception as e:
            print(f"  Failed to process {item['rel_path']}: {e}")
            continue

        records.append(
            FaceRecord(
                person_id=item["person_id"],
                age=item["age"],
                capture_year=item["capture_year"],
                dataset=item["dataset"],
                photo_path=item["rel_path"],
                face_embedding=result["embedding"],
            )
        )

    if records:
        db.add_all(records)
        db.commit()
        print(f"  Inserted {len(records)} records")

    return len(records)


def main() -> None:
    args = parse_args()

    engine = create_engine(args.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    pipeline = get_face_pipeline()

    with Session(engine) as db:
        if args.reset:
            from sqlalchemy import delete

            db.execute(delete(FaceRecord))
            db.commit()
            print("Cleared existing face_records.")

        if args.csv:
            count = ingest_from_csv(
                args.csv,
                args.images_root or args.csv.parent,
                args.dataset_name,
                db,
                pipeline,
                args.batch_size,
            )
        else:
            count = ingest_from_directory(
                args.dataset_dir,
                args.dataset_name,
                db,
                pipeline,
                args.batch_size,
            )

    print(f"Done. Total records ingested: {count}")


if __name__ == "__main__":
    main()