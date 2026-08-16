#!/usr/bin/env python
"""Evaluate cross-age face recognition performance.

For each person in the corpus, use their youngest photo as query
and measure rank of their older photos in the results.

Metrics:
- Rank-1 accuracy: Is the same person's oldest photo at rank 1?
- Rank-5 accuracy: Is any same-person photo in top 5?
- Rank-10 accuracy: Is any same-person photo in top 10?
- Mean Reciprocal Rank (MRR)
- CMC curve (Cumulative Match Characteristic)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database.models import Base, FaceRecord
from backend.search.service import search_face_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-age face recognition evaluation")
    parser.add_argument(
        "--database-url",
        default=os.environ.get(
            "DATABASE_URL", "postgresql+psycopg://app:changeme@localhost:5432/appdb"
        ),
        help="Database URL",
    )
    parser.add_argument(
        "--dataset", default=None, help="Filter by dataset name (optional)"
    )
    parser.add_argument(
        "--top-k", type=int, default=20, help="Top-K results to retrieve"
    )
    parser.add_argument(
        "--min-similarity", type=float, default=0.0, help="Minimum similarity threshold"
    )
    parser.add_argument(
        "--min-age-gap", type=int, default=5, help="Minimum age gap to consider as cross-age"
    )
    parser.add_argument(
        "--output", type=Path, help="Output JSON file for detailed results"
    )
    return parser.parse_args()


def get_face_records(db: Session, dataset: Optional[str] = None) -> list[FaceRecord]:
    """Get all face records, optionally filtered by dataset."""
    query = db.query(FaceRecord)
    if dataset:
        query = query.filter(FaceRecord.dataset == dataset)
    return query.all()


def group_by_person(records: list[FaceRecord]) -> dict[str, list[FaceRecord]]:
    """Group face records by person_id."""
    groups = defaultdict(list)
    for r in records:
        groups[r.person_id].append(r)
    return groups


def evaluate_person(
    person_id: str,
    records: list[FaceRecord],
    db: Session,
    top_k: int,
    min_similarity: float,
    min_age_gap: int,
) -> list[dict]:
    """Evaluate cross-age retrieval for one person.

    For each photo, use it as query and check if other photos of same person
    appear in top-K (with age gap >= min_age_gap).
    """
    if len(records) < 2:
        return []  # Need at least 2 photos of same person

    results = []
    for query_record in records:
        # Search
        response = search_face_records(
            db,
            query_embedding=query_record.face_embedding,
            top_k=top_k,
            min_similarity=min_similarity,
        )

        # Find same-person records in results with sufficient age gap
        query_age = query_record.age
        same_person_hits = []

        for rank, res in enumerate(response.results, 1):
            if res.person_id == person_id:
                age_gap = abs(res.age - query_age)
                if age_gap >= min_age_gap:
                    same_person_hits.append(
                        {
                            "rank": rank,
                            "similarity": res.face_similarity,
                            "query_age": query_age,
                            "match_age": res.age,
                            "age_gap": age_gap,
                            "match_record_id": res.record_id,
                        }
                    )

        if same_person_hits:
            best = same_person_hits[0]
            results.append(
                {
                    "person_id": person_id,
                    "query_record_id": query_record.record_id,
                    "query_age": query_age,
                    "best_rank": best["rank"],
                    "best_similarity": best["similarity"],
                    "best_age_gap": best["age_gap"],
                    "match_record_id": best["match_record_id"],
                    "all_hits": same_person_hits,
                }
            )
        else:
            # No same-person cross-age match found
            results.append(
                {
                    "person_id": person_id,
                    "query_record_id": query_record.record_id,
                    "query_age": query_age,
                    "best_rank": None,
                    "best_similarity": None,
                    "best_age_gap": None,
                    "match_record_id": None,
                    "all_hits": [],
                }
            )

    return results


def compute_metrics(all_results: list[dict], top_k: int) -> dict:
    """Compute aggregate metrics from per-query results."""
    total_queries = len(all_results)
    if total_queries == 0:
        return {}

    rank1 = sum(1 for r in all_results if r["best_rank"] == 1)
    rank5 = sum(1 for r in all_results if r["best_rank"] and r["best_rank"] <= 5)
    rank10 = sum(1 for r in all_results if r["best_rank"] and r["best_rank"] <= 10)

    # MRR
    mrr = sum(1.0 / r["best_rank"] for r in all_results if r["best_rank"]) / total_queries

    # CMC curve
    cmc = [0] * top_k
    for r in all_results:
        if r["best_rank"]:
            for k in range(r["best_rank"] - 1, top_k):
                cmc[k] += 1
    cmc = [c / total_queries for c in cmc]

    return {
        "total_queries": total_queries,
        "rank1_accuracy": rank1 / total_queries,
        "rank5_accuracy": rank5 / total_queries,
        f"rank{top_k}_accuracy": rank10 / total_queries,
        "mrr": mrr,
        "cmc_curve": cmc,
    }


def main() -> None:
    args = parse_args()

    engine = create_engine(args.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        records = get_face_records(db, args.dataset)
        print(f"Loaded {len(records)} face records")

        if not records:
            print("No records found. Run ingestion first.")
            return

        groups = group_by_person(records)
        print(f"Found {len(groups)} unique persons")
        print(f"  Persons with >=2 photos: {sum(1 for v in groups.values() if len(v) >= 2)}")

        all_results = []
        for person_id, person_records in groups.items():
            if len(person_records) < 2:
                continue

            person_results = evaluate_person(
                person_id,
                person_records,
                db,
                args.top_k,
                args.min_similarity,
                args.min_age_gap,
            )
            all_results.extend(person_results)

        metrics = compute_metrics(all_results, args.top_k)

        print("\n=== Cross-Age Evaluation Results ===")
        print(f"Total queries: {metrics.get('total_queries', 0)}")
        print(f"Rank-1 accuracy: {metrics.get('rank1_accuracy', 0):.4f}")
        print(f"Rank-5 accuracy: {metrics.get('rank5_accuracy', 0):.4f}")
        print(f"Rank-{args.top_k} accuracy: {metrics.get(f'rank{args.top_k}_accuracy', 0):.4f}")
        print(f"MRR: {metrics.get('mrr', 0):.4f}")
        print("\nCMC Curve (top-20):")
        for i, val in enumerate(metrics.get("cmc_curve", [])[:20]):
            print(f"  Rank {i+1}: {val:.4f}")

        if args.output:
            output_data = {
                "config": {
                    "dataset": args.dataset,
                    "top_k": args.top_k,
                    "min_similarity": args.min_similarity,
                    "min_age_gap": args.min_age_gap,
                },
                "metrics": metrics,
                "per_query_results": all_results,
            }
            args.output.write_text(json.dumps(output_data, indent=2))
            print(f"\nDetailed results saved to {args.output}")


if __name__ == "__main__":
    main()