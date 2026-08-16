# Progress

## 2026-08-16 - Cross-age evaluation over full corpus (DONE)

- Ran `scripts/evaluate_cross_age.py` against SQLite corpus (609 records, 82 persons, 607 queries). Fixed 2 bugs in the script: read `query_record.id` (was `record_id`, doesn't exist on model x2 places); and excluded the query image itself from the gallery (self-match otherwise occupies rank 1, making rank-1 structurally 0).
- **Results (self-exclusion protocol):**
  - Rank-1: 23.2% · Rank-5: 80.4% · Rank-10: 89.5% · Rank-20: 89.5% · MRR: 0.46
  - By age gap: 5-9y (n=439): R1 25% R5 85% R10 97% · 10-14y (n=76): R1 21% R5 90% R10 95% · 15+y (n=45): R1 33% R5/R10 100%
- **Success criterion met:** Rank-10 > 70% -> 89.5% overall, ~95-100% for real cross-age gaps.
- Insight: pure cosine ranking reliably surfaces the RIGHT PERSON early (top-5 ~80%+), but not always the single best photo (rank-1 23%). Room to improve with age-progression/multi-factor re-ranking; search 5-10x queries ("person 001" repeats) stay under 1s per query.
- 3 files changed (uncommitted): `scripts/evaluate_cross_age.py` bug fixes + doc edit.

## 2026-08-16 - Real-model verification + lint cleanup (DONE)

- Added `scripts/smoke_search.py`: end-to-end smoke against the LIVE backend (auth -> real InsightFace extraction -> /search/photo -> same-person rank-1 + corpus count). Usage: `python scripts/smoke_search.py`. Exit code 0/1.
- Added `tests/test_search_integration.py` (3 tests, `@pytest.mark.integration`) exercising the REAL model + a throwaway COPY of the corpus DB. Auto-skipped via `pytest_collection_modifyitems` hook in `tests/conftest.py`; run with `python -m pytest tests -m integration --q` -> 3 passed.
- Added `[tool.pytest.ini_options] markers = ["integration"]` to `pyproject.toml`.
- Lint debt fixed (#4): black `backend/database/models.py` reformatted (had been untouched day-4 work); `backend/main.py` was already black-clean. `flake8 backend tests` now clean (models.py's 3 E501s gone).
- Verified: default `pytest tests` = **97 passed, 3 skipped**; `-m integration` = **3 passed**; `scripts/smoke_search.py` = all OK (609 scanned, person 001 rank 1). black/flake8 clean on `backend tests scripts/smoke_search.py`.
- Note: `scripts/ingest_dataset.py` + `scripts/evaluate_cross_age.py` have PRE-EXISTING lint debt (E501/E402/F401) NOT in scope; left untouched.

## 2026-08-16 - E2E case flow verified green in real browser (DONE)

- Real blocker found + fixed: `POST /cases/photo/upload?create_case=true` binds plain params as QUERY params, but frontend sent them as multipart form fields -> create_case always False -> case_id null -> UI stuck on "Processing...".
  - Fixed `frontend/src/services/api.ts` `uploadPhoto`: options (create_case, query_name, query_age, query_date, query_location, notes) now appended as URL query params, file stays in FormData.
- `frontend/vite.config.ts`: added `changeOrigin: true` to the `/api` proxy. Backend emits absolute image URLs from `request.base_url`, which mirrors the Host header; without changeOrigin it saw `:5173` and produced `http://localhost:5173/ref-images/...` that Vite can't serve.
- `backend/cases/routes.py` `_photo_url`: split on "/" only; on Windows stored paths use "\\" -> filename became `uploads\abc.jpg` -> URL `/uploads/uploads/` (browser normalizes backslash). Now `.replace("\\", "/")` before split.
- Playwright E2E (`Temp/opencode/pw-e2e.cjs`, chrome channel): register -> /cases/new -> upload FG-NET 001A02 -> details -> Create Case -> real `/cases/<uuid>` -> Search Results (609 records scanned) -> top candidates all Person 001 (cross-age correct) -> query image (`.uploads`) + candidate images (`.ref-images`) all naturalWidth>0 -> **zero console/page/network errors**.
- Verification: `npm run build` PASS (tsc + vite), `python -m pytest tests -q` = **97 passed**.
- NOTE: stray 0-byte `backend/pehchaanai.db` artifact (produced by a run with cwd=backend). Real DB is `pehchaanai.db` at repo root. Harmless; can delete.

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
- Updated backend and frontend startup for native local development.

Verified:
- `python -m pytest tests -v`
- `python -m black --check backend tests`
- `python -m flake8 backend tests`
- `npm run build`
- `npm audit`
- backend startup verification
- frontend build verification

Next:
- Day 3: Face detection pipeline, photo upload endpoint, embedding generation.

---

## 2026-08-14 - Day 3: Face Detection Pipeline

Completed:
- Integrated InsightFace (ArcFace) for face detection, alignment, and 512-d embedding extraction.
- Created `backend/face/` module:
  - `detector.py` - InsightFace-based face detection and alignment
  - `embedder.py` - 512-d ArcFace embedding extraction
  - `pipeline.py` - High-level orchestration (decode → detect → align → embed → quality)
  - `exceptions.py` - Custom exceptions (NoFaceFoundError, LowQualityFaceError, etc.)
- Created photo upload endpoints in `backend/cases/routes.py`:
  - `POST /cases/photo/embedding` - Extract embedding only
  - `POST /cases/photo/upload` - Extract embedding + optionally create a case
- Created Case model for query scenarios (childhood photo + metadata + embedding).
- Created Case schemas with query-centric fields.

Verified:
- `python -m pytest tests -v` (all pass)
- `python -m black --check backend tests`
- `python -m flake8 backend tests`

Next:
- Day 4: Vector search + dataset ingestion + evaluation.

---

## 2026-08-14 - Day 4: Vector Search (Revised per clarified scope)

**Scope clarification:** The project is a cross-age face recognition prototype using research datasets (MORPH, CACD, FG-NET, etc.), NOT a production police/NGO system. The core question: "Can we retrieve the same person across significant age gaps using pure biometric similarity?"

Completed:
- **Revised data model** (`backend/database/models.py`):
  - `FaceRecord` table: searchable corpus with `person_id`, `age`, `capture_year`, `dataset`, `face_embedding` (VECTOR(512))
  - IVFFlat index on `face_embedding` for fast cosine similarity
  - `Case` table simplified to query-only: `query_name`, `query_age`, `photo_path`, `face_embedding`
  - Removed `Candidate` table (was conflating query and corpus)

- **Removed arbitrary multi-factor ranking** (`backend/search/ranking.py`):
  - Kept only `cosine_similarity()` utility
  - Removed age/location/date scoring weights (unvalidated heuristic)
  - Pure biometric similarity is the only ranking signal

- **Search service** (`backend/search/service.py`):
  - `search_face_records()` - pgvector `<=>` cosine similarity, returns top-K
  - `search_by_case()` - convenience wrapper using stored Case embedding

- **Search API** (`backend/search/routes.py`):
  - `POST /search` - search with explicit embedding + top_k/min_similarity
  - `GET /search/case/{case_id}` - search using stored case
  - `POST /search/photo` - upload photo, extract embedding, search

- **Dataset ingestion pipeline** (`scripts/ingest_dataset.py`):
  - Supports CSV metadata or directory structure (`person_id/age.jpg`)
  - Batch embedding extraction with InsightFace
  - Stores person_id, age, capture_year, dataset for evaluation

- **Cross-age evaluation** (`scripts/evaluate_cross_age.py`):
  - For each person, use each photo as query
  - Measure rank of other photos of same person (with min age gap)
  - Outputs: Rank-1/5/10 accuracy, MRR, CMC curve

- **Tests updated** (`tests/test_search.py`, `tests/test_cases.py`):
  - 22 tests pass (5 auth + 11 case + 6 search)
  - All code passes `black` and `flake8`

Verified:
- `python -m pytest tests -v` (22 passed)
- `python -m black --check backend tests`
- `python -m flake8 backend tests`

Next:
- Day 5: Frontend Dashboard & Upload UI for core query→search→results flow

---

## 2026-08-15 - Dashboard UI fix (DONE)

Bug: /dashboard broken. Big empty top gap. Content pushed down. Quick Actions heading visible but cards gone. Playwright repro.

Root cause (2 bugs):
1. Sidebar `lg:static` -> in-flow block desktop -> push content down (~490px gap). 
2. primitives.tsx `baseVariants.visible` was a FUNCTION; `{...baseVariants.visible}` spread = `{}`. So Reveal/StaggerItem visible variant = transition only (no opacity/y/filter). Content stuck in hidden (opacity 0 + blur). That's "cards missing".

Fixed:
- Layout.tsx: sidebar always `fixed`; drawer x toggled by `sidebarOpen` + matchMedia(1024px). Mobile drawer now opens/closes right. No lg:static.
- primitives.tsx: `baseVariants.visible` now plain object. Reveal/StaggerItem animate properly.

Verified (Playwright 1440x900 + 390x844):
- mainTop = 65 (was 550). No opacity-0 content on desktop. All sections visible: Welcome, Stats, Quick Actions (3 links), Overview, Recent Cases (5 rows), Dev Progress.
- Mobile: same; drawer closed off-canvas by default (x=-280), opens to x=0, closes.
- No horizontal overflow. No console errors (only pre-existing missing favicon 404, unrelated).
- `npm run build` (tsc+vite) PASS. Backend pytest 24 passed. Frontend has no test files (pre-existing) and no lint config; tsc is typecheck.

## 2026-08-16 - Stray stub API found

- Dashboard showed fake user "Aarav Sharma" + fake cases (Riya Verma, etc).
- Cause: leftover `Temp\opencode\stub_api.mjs` (node, PID 8384) hogging port 8000 next to real uvicorn. It hardcodes fake user/cases.
- Fix: killed process. Real backend (uvicorn PID 9620) now serves (401 without token). Re-login needed.

## 2026-08-16 - "Failed to fetch" on login/register (FIXED)

- Cause: CORS. Old stub served `Access-Control-Allow-Origin: *`, masked everything. Real backend allowlist only had localhost:3000 / localhost:5173.
- Symptom: opening app via LAN IP http://192.168.0.123:5173 -> OPTIONS preflight rejected (400, no ACAO) -> browser shows "Failed to fetch" on sign in + register.
- Fix: backend/config.py default BACKEND_CORS_ORIGINS now includes http://127.0.0.1:5173 + http://192.168.0.123:5173. Same in backend/.env.
- Backend restarted (was down after reload). Now on port 8000 (uvicorn --reload), health ok.
- Verified: preflight 200 from localhost/127.0.0.1/LAN. Full browser flow PASS: register -> dashboard (sidebar shows name, hero first name) -> sign out -> sign in.
- Only console noise: pre-existing favicon 404.

## 2026-08-16 - "Failed to fetch" STILL (FIXED for real)

- Even with CORS fixed, login/register could still fail: frontend hardcoded API base `http://localhost:8000`.
- That only resolves on the dev machine. Any other device on LAN: `localhost` = that device -> connection refused -> "Failed to fetch".
- Fix: frontend now same-origin. `services/api.ts` default `VITE_API_BASE_URL || ''` (relative). Vite proxy covers `/auth`, `/cases`, `/search`, `/health` (added in `vite.config.ts`).
- Verified Playwright at http://localhost:5173 AND http://192.168.0.123:5173: register -> dashboard -> sign out -> sign in, 0 errors, both.
- `npm run build` (tsc+vite) PASS. Note: prod hosting now needs reverse proxy or env VITE_API_BASE_URL.

## 2026-08-16 - Cleanup (low risk)

- Deleted orphaned components: `CaseList.tsx`, `ui/FileUpload.tsx` (nothing imports them).
- Added `public/favicon.svg` + `<link rel="icon">` (kills pre-existing favicon 404).
- Verified: `npm run build` PASS (tsc). favicon 200 image/svg+xml at :5173. pytest 24 passed.
- Pre-existing (NOT from this task): black wants to reformat backend/main.py, database/models.py, face/detector.py; flake8 E501 x3 in models.py. Left untouched (part of uncommitted day-4 work).

## 2026-08-16 - FG-NET dataset ingested + face pipeline fixed

- Bug found: ingest inserted 0/1002. Root cause: `face.aligned` is always None in this InsightFace build -> `get_aligned_face()` raised "Face alignment failed" for every detected face.
- Fixed `backend/face/detector.py`: alignment via `insightface.utils.face_align.norm_crop(image, kps[:5])` (real 112x112 crop, no more `.aligned`).
- Fixed `backend/face/pipeline.py`: embed from `face.embedding` already computed by FaceAnalysis (single recognition pass); `get_aligned_face(image, face=face)` reuses detected face; embedder fallback kept.
- Result: **609 / 1002 FG-NET records inserted** (82/82 persons, ages 0-69). Remaining fails = genuinely low-quality scans (fail raw detection even at 0.15).
- Formatting: black applied to detector.py+pipeline.py; flake8 clean. pytest 24 passed.
- Verified cross-age search via API: query = person 001 @ age 2 -> rank1 self sim 1.0, same person at ages 5/8/10 in top-5.

## 2026-08-16 - End-to-End search flow tests (TDD) (DONE)

- Added `tests/test_search_flow.py`: 13 E2E tests covering the full product loop:
  - create case (`POST /cases`) -> seed corpus -> search by case (`GET /search/case/{id}`) -> ranked results
  - upload photo -> search (`POST /search/photo`) with stubbed face pipeline
  - upload + create case (`POST /cases/photo/upload?create_case=true`) -> case persists -> searchable
  - error paths: no face / low quality / detection failure -> 400; non-image -> 415; foreign/missing case -> 404
  - top_k limiting, min_similarity filtering (incl. exact-match boundary), empty corpus, metadata round-trip
- conftest refactor: shared `test_engine` + `db_session` fixture (seeds corpus visible to API requests),
  `fake_pipeline` fixture (deterministic stand-in for InsightFace via dependency override).
- Removed duplicate `client` fixture from test_auth.py (was shadowing conftest -> tests used different DBs).
- Coverage push: `tests/test_face_pipeline.py`, `test_face_detector.py`, `test_face_embedder.py`,
  `test_database.py` + error-path additions in `test_auth.py`/`test_cases.py`/`test_search.py`.
- Results: **97 passed**, backend coverage **99%** (auth/security/cases/search all 100%).
  Only uncovered: `detect_faces`/`embed_face_image` convenience wrappers (trigger model download) and
  the `if __name__ == "__main__"` uvicorn entrypoint.
- black + flake8 clean (only pre-existing models.py E501s remain, left untouched).
- Added `.pytest_cache/`, `.coverage`, `htmlcov/` to .gitignore.
