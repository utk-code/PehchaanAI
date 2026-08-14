"""Multi-factor ranking for candidate matches.

Combines several independent signals into a single composite confidence score:

* ``face_similarity`` - cosine similarity between query and candidate embeddings.
* ``age_score``       - how close the candidate's recorded age is to the
  child's age at disappearance.
* ``location_score``  - geographic proximity (derived from a coarse region
  hierarchy + a Levenshtein-normalised string distance).
* ``date_score``      - temporal proximity of the candidate record date to the
  date the child went missing.

Each sub-score is normalised to ``[0, 1]`` and then combined using configurable
weights. The default weights emphasize biometric similarity (the strongest
signal) while still rewarding corroborating demographic / contextual evidence.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)

# Default weights for the composite score. They sum to 1.0 and can be
# overridden at search time if needed.
DEFAULT_WEIGHTS: dict[str, float] = {
    "face": 0.55,
    "age": 0.20,
    "location": 0.15,
    "date": 0.10,
}

# Major Indian states / regions used for a coarse hierarchical location match.
REGION_KEYWORDS = (
    "delhi",
    "mumbai",
    "maharashtra",
    "karnataka",
    "bengaluru",
    "bangalore",
    "tamil nadu",
    "chennai",
    "west bengal",
    "kolkata",
    "uttar pradesh",
    "lucknow",
    "bihar",
    "patna",
    "gujarat",
    "ahmedabad",
    "rajasthan",
    "jaipur",
    "telangana",
    "hyderabad",
    "kerala",
    "thiruvananthapuram",
    "punjab",
    "chandigarh",
    "haryana",
    "gurugram",
    "madhya pradesh",
    "bhopal",
    "odisha",
    "bhubaneswar",
    "assam",
    "guwahati",
    "jharkhand",
    "ranchi",
)


@dataclass
class RankingWeights:
    face: float = DEFAULT_WEIGHTS["face"]
    age: float = DEFAULT_WEIGHTS["age"]
    location: float = DEFAULT_WEIGHTS["location"]
    date: float = DEFAULT_WEIGHTS["date"]

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.face, self.age, self.location, self.date)


def cosine_similarity(
    a: list[float] | np.ndarray, b: list[float] | np.ndarray
) -> float:
    """Return the cosine similarity between two vectors in [-1, 1]."""
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def _age_score(query_age: int | None, candidate_age: int) -> float:
    """Score based on absolute age difference (no query age => neutral 0.5)."""
    if query_age is None:
        return 0.5
    diff = abs(query_age - candidate_age)
    # Within 2 years -> >= 0.7, decays to 0 by ~10 years difference.
    return float(max(0.0, 1.0 - diff / 10.0))


def _region_overlap(a: str, b: str) -> bool:
    """True if both location strings share a known region keyword."""
    la, lb = a.lower(), b.lower()
    for region in REGION_KEYWORDS:
        if region in la and region in lb:
            return True
    return False


def _levenshtein_ratio(a: str, b: str) -> float:
    """Normalised Levenshtein similarity in [0, 1]."""
    a, b = a.lower().strip(), b.lower().strip()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    distance = prev[-1]
    return float(1.0 - distance / max(len(a), len(b)))


def _location_score(query_loc: str | None, candidate_loc: str) -> float:
    """Score based on region overlap and string similarity."""
    if not query_loc:
        return 0.5
    if _region_overlap(query_loc, candidate_loc):
        return 1.0
    return float(min(1.0, _levenshtein_ratio(query_loc, candidate_loc)))


def _date_score(query_date: datetime | None, candidate_date: datetime) -> float:
    """Score based on temporal distance (no query date => neutral 0.5)."""
    if query_date is None:
        return 0.5
    q = query_date.replace(tzinfo=None) if query_date.tzinfo else query_date
    c = candidate_date.replace(tzinfo=None) if candidate_date.tzinfo else candidate_date
    days = abs((q - c).days)
    # Within ~1 year strongly relevant, decays to 0 by ~6 years.
    return float(max(0.0, 1.0 - days / (6 * 365.0)))


def combine_scores(
    face: float,
    age: float,
    location: float,
    date: float,
    weights: RankingWeights | None = None,
) -> float:
    """Combine normalised sub-scores into a 0-100 composite confidence."""
    w = weights or RankingWeights()
    wf, wa, wl, wd = w.as_tuple()
    composite = wf * face + wa * age + wl * location + wd * date
    return round(composite * 100.0, 2)
