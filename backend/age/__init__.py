"""Age progression module using InsightFace's built-in age estimation.

This module implements a lightweight "multi-age search" approach:
1. When a user uploads a child photo, we estimate the current age
2. We search the database with age filters for older age ranges
3. This simulates age progression without heavy image transformation
"""