# Progress

## 2026-08-12 - Day 2: Authentication & Basic Backend

Completed:
- Initialized FastAPI backend in `backend/`.
- Added SQLAlchemy database session wiring and a `users` table model.
- Implemented JWT auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /auth/me`
- Added Argon2 password hashing via `pwdlib`.
- Added isolated auth API tests using SQLite overrides.
- Initialized Vite React TypeScript frontend in `frontend/`.
- Updated Docker Compose to use PostgreSQL with pgvector.
- Fixed backend and frontend Dockerfiles for service-local build contexts.

Verified:
- `python -m pytest tests -v`
- `python -m black --check backend tests`
- `python -m flake8 backend tests`
- `npm run build`
- `npm audit`
- `docker compose config`
- `docker compose build --progress plain`

Next:
- Day 3: Case model, face detection pipeline, photo upload endpoint, and embedding generation.

---

## 2026-08-14 - Day 3: Face Detection Pipeline & Case Management

Completed:
- Created Case SQLAlchemy model with VECTOR(512) face_embedding column
- Added pgvector, numpy, opencv-python-headless, insightface, onnxruntime to requirements.txt
- Created face detection module (`backend/face/`):
  - `detector.py` - InsightFace-based face detection and alignment
  - `embedder.py` - 512-d ArcFace embedding extraction
  - `pipeline.py` - High-level orchestration (decode → detect → align → embed → quality)
  - `exceptions.py` - Custom exceptions (NoFaceFoundError, LowQualityFaceError, etc.)
- Created Case schemas in `backend/cases/schemas.py` (CaseCreate, CaseRead, CaseUpdate, EmbeddingResponse, PhotoUploadResponse)
- Implemented photo upload endpoints in `backend/cases/routes.py`:
  - `POST /cases/photo/embedding` - Extract embedding only
  - `POST /cases/photo/upload` - Upload + embedding + optional case creation
  - `POST /cases` - Create case with pre-computed embedding
  - `GET /cases` - List cases for current investigator
  - `GET /cases/{id}` - Get case by ID
  - `PATCH /cases/{id}` - Update case
  - `DELETE /cases/{id}` - Soft delete (archive) case
- Added case routes to main app with JWT authentication
- Wrote 11 unit tests for case endpoints (`tests/test_cases.py`)
- All 16 tests pass (5 auth + 11 case tests)
- Code passes black formatting and flake8 linting

Verified:
- `python -m pytest tests -v` (16 passed)
- `python -m black --check backend tests`
- `python -m flake8 backend tests`

Next:
- Day 4: Vector Search & Multi-Factor Ranking
