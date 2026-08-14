#!/usr/bin/env python
"""Seed the database with synthetic candidate records for demo/testing.

This script generates deterministic synthetic 512-d embeddings clustered around
a handful of "anchor" identities so that similarity search + multi-factor
ranking can be exercised without requiring the heavy InsightFace models.

Usage:
    python scripts/seed_candidates.py [--count N] [--reset]

Environment: DATABASE_URL (defaults to local postgres).
"""
from __future__ import annotations

import argparse
import os
import random
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from backend.database.models import Base, Candidate

DIM = 512
CITIES = [
    ("Mumbai, Maharashtra", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Bengaluru, Karnataka", "Karnataka"),
    ("Chennai, Tamil Nadu", "Tamil Nadu"),
    ("Kolkata, West Bengal", "West Bengal"),
    ("Hyderabad, Telangana", "Telangana"),
    ("Ahmedabad, Gujarat", "Gujarat"),
    ("Jaipur, Rajasthan", "Rajasthan"),
    ("Lucknow, Uttar Pradesh", "Uttar Pradesh"),
    ("Patna, Bihar", "Bihar"),
]
NAMES = [f"child_{i:03d}" for i in range(1, 101)]


def _make_anchor(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(DIM).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed candidate pool")
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--reset", action="store_true", help="Clear table first")
    args = parser.parse_args()

    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://app:changeme@localhost:5432/appdb",
    )
    engine = create_engine(db_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    # Create anchor identities so clusters exist for meaningful ranking.
    num_anchors = max(5, args.count // 20)
    anchors = [_make_anchor(i) for i in range(num_anchors)]

    if args.reset:
        with Session(engine) as db:
            db.execute(delete(Candidate))
            db.commit()
        print("Cleared existing candidates.")

    rng = random.Random(42)
    nprng = np.random.default_rng(7)

    records: list[Candidate] = []
    base_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    for i in range(args.count):
        anchor = anchors[rng.randrange(num_anchors)]
        # Jitter the anchor to simulate same-person photo variation.
        noise = nprng.standard_normal(DIM).astype(np.float32) * 0.15
        vec = anchor + noise
        vec /= np.linalg.norm(vec)

        city, region = CITIES[rng.randrange(len(CITIES))]
        age = rng.randint(3, 16)
        days_offset = rng.randint(0, 900)
        record_date = base_date + timedelta(days=days_offset)
        name = NAMES[i % len(NAMES)]

        records.append(
            Candidate(
                name_encrypted=name,
                age_at_record=age,
                record_date=record_date,
                location=city,
                source="seed",
                photo_path=f"seed/{name}.jpg",
                face_embedding=vec.tolist(),
            )
        )

    with Session(engine) as db:
        db.add_all(records)
        db.commit()

    print(f"Inserted {len(records)} candidate records.")


if __name__ == "__main__":
    main()
