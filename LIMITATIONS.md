# Age Progression Limitations

## Current Approach
- Uses **filter-based search with weighted age ranges** instead of visual age progression.
- Relies on InsightFace's age estimation to filter and rank corpus records by relevance to the target age.

## Why Not Visual Age Progression?
- **No lightweight, free models available** for local use:
  - InsightFace's `age_transform` is undocumented and non-functional.
  - Other models (e.g., SAM, CAAE) are outdated or require unavailable pre-trained weights.
- **Zero-budget constraint** rules out API-based solutions (e.g., Lambda Labs, DeepAI).

## Accuracy
- Cross-age matching is **less precise** than same-age matching but improved by:
  - Weighted age ranges (e.g., prioritizing ages 20–40 for a 30-year-old target).
  - Combined ranking of results from multiple age ranges.

## Future Work
- Revisit visual age progression if lightweight models or APIs become available.