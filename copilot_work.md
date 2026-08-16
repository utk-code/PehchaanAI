# Copilot Work Plan

## Project
PehchaanAI - Cross-Age Face Recognition for Missing Child Identification

## Purpose
This document is the working plan for future agents. Use it as the single source of truth for what the codebase is trying to do, what is already working, what still needs work, and how to pick up tasks safely.

## Current State

### Working now
- Backend starts locally using SQLite by default.
- Frontend builds successfully.
- Auth flow and case/search tests pass.
- API client auth header and file upload handling are fixed.
- Backend health endpoint responds.
- `/dashboard` renders correctly on desktop + mobile (sidebar fixed left, no invisible content).
- Register/login work from localhost AND any LAN device: frontend calls the API same-origin through the Vite dev proxy (no hardcoded `localhost:8000`, no CORS dependence in dev).
- **E2E case flow verified green in a real browser (2026-08-16)**: register -> upload photo -> create case -> search results -> candidate + query images all load, 0 console errors. Two real bugs fixed along the way:
  1. `uploadPhoto` must send `create_case`/`query_name`/etc. as URL query params, NOT multipart form fields (FastAPI binds them as query params) — otherwise `case_id` is null and the UI hangs on "Processing...".
  2. Image URLs must point at the backend: (a) use `changeOrigin: true` on the Vite `/api` proxy, else `request.base_url` keeps Host `:5173` → backend emits `:5173/ref-images/...`; (b) `_photo_url` splits on `/`, but Windows stores `uploads\abc.jpg` → normalize `\` → `/` first, else URL becomes `/uploads/uploads/`.
- Note: `backend/pehchaanai.db` is a stray 0-byte artifact; the real DB is `pehchaanai.db` at repo root.

### Cleanup (2026-08-16)
- Deleted orphaned frontend components: `src/components/cases/CaseList.tsx`, `src/components/ui/FileUpload.tsx` (were not imported).
- Added `public/favicon.svg` + favicon `<link>` (fixes the old 404 favicon console error).
- Known pre-existing lint debt (not from recent work): `backend/main.py`, `backend/database/models.py` would be reformatted by black; `models.py` has 3 flake8 E501 long lines. Safe to fix later.

### FG-NET ingestion (2026-08-16)
- **Pipeline fix (was returning 0/1002):** this InsightFace build never sets `face.aligned`; `get_aligned_face()` failed on every image. `backend/face/detector.py` now aligns via `face_align.norm_crop(image, kps[:5])`; `backend/face/pipeline.py` embeds from the `face.embedding` already computed by FaceAnalysis (fallback still re-embeds the aligned crop). Applies to case-upload and search-photo endpoints too, not just ingest.
- **Ingested:** 609 / 1002 FG-NET records into `face_records` (82/82 persons, ages 0-69; SQLite). Failures are low-quality scans that fail raw detection even at det_thresh 0.15.
- **Ingest command (SQLite-aware):**
  ```
  python scripts/ingest_dataset.py --csv <meta.csv> --images-root <FGNET\images> --dataset-name FG-NET --database-url sqlite+pysqlite:///./pehchaanai.db
  ```
  (script defaults to PostgreSQL; must pass the SQLite URL.) generate meta.csv from filenames `001A02.JPG` -> person 001, age 2.
- **Cross-age sanity check passed:** query person 001 @ age 2 -> rank 1 self (sim 1.0), same person at ages 5/8/10 in top-5.
- Recommendation: use buffalo_s for CPU speed (already configured); `--reset` before re-ingesting to avoid duplicates.

### Recent work completed
- **Networking fix (2026-08-16):** `frontend/src/services/api.ts` default API base is now relative (`VITE_API_BASE_URL || ''`); `frontend/vite.config.ts` dev proxy now forwards `/auth`, `/cases`, `/search`, `/health` to `:8000`. Verified via Playwright at `http://localhost:5173` and `http://192.168.0.123:5173` (register -> dashboard -> sign out -> sign in, 0 errors). Prod hosting now needs a reverse proxy or a `VITE_API_BASE_URL` at build time.
- **Dashboard fixes (2026-08-15):** sidebar no longer in document flow on desktop (`lg:static` removed; kept `fixed`, drawer toggled by state + matchMedia); `primitives.tsx` variants fixed (`visible` was a function, `{...fn}` spread = `{}` so content stayed at opacity 0). Verified via Playwright at 1440x900 and 390x844.
- **Runtime cleanup (2026-08-16):** a stray dev stub (`Temp/opencode/stub_api.mjs`, node) was squatting on port 8000 and answered with a fake user ("Aarav Sharma") and fake cases. Killed it; only real uvicorn serves 8000 now. If fake users/data reappear, check for that process.
- **CORS fix (2026-08-16):** backend CORS allowlist now includes `127.0.0.1:5173` + LAN IP in `backend/config.py` default and `backend/.env` (belts-and-suspenders; dev no longer relies on CORS at all).
- Repaired the frontend API client so bearer auth is sent correctly and multipart uploads keep their form-data headers.
- Reworked backend startup defaults so the app can run without containers.
- Swapped the backend data layer to SQLite-compatible models/session config for local development.
- Replaced the pgvector-backed search service with in-memory cosine similarity search for local dev.
- Verified backend startup with `/health`, backend tests, and the frontend production build.

### Important constraints
- The project is a research prototype, not a production law-enforcement system.
- Face search should remain pure cosine similarity unless a validated change is explicitly introduced.
- Do not reintroduce brittle startup dependencies just to support one deployment mode.
- Keep the repo local-dev first.

## High-Level Goal
Build a usable cross-age face recognition app with:
- JWT auth
- query-case creation and upload
- face embedding extraction
- corpus search by similarity
- dashboard UI for users
- dataset ingestion and evaluation tooling

## Architecture Summary

### Frontend
- React + TypeScript + Vite
- React Router for navigation
- TanStack Query for server state
- Auth context for session handling
- Pages for login, register, dashboard, cases, search, reports

### Backend
- FastAPI
- SQLAlchemy ORM
- JWT auth
- Face pipeline using InsightFace
- Search service using cosine similarity
- Case management endpoints

### Data layer
- SQLite for local startup
- PostgreSQL + pgvector remains an optional full-search path
- FaceRecord is the searchable corpus table
- Case is the user query record

## Key File Map

### Backend
- `backend/main.py` - app startup and router registration
- `backend/config.py` - environment settings
- `backend/database/models.py` - ORM models
- `backend/database/session.py` - engine/session creation
- `backend/auth/*` - auth schemas, routes, security
- `backend/cases/*` - case CRUD and photo upload
- `backend/face/*` - face detection, embedding, pipeline
- `backend/search/*` - search schemas, ranking, service, routes

### Frontend
- `frontend/src/main.tsx` - entry point
- `frontend/src/App.tsx` - routing and auth wrapper
- `frontend/src/context/AuthContext.tsx` - session state
- `frontend/src/services/api.ts` - API client
- `frontend/src/hooks/*` - query/auth hooks
- `frontend/src/pages/*` - top-level screens
- `frontend/src/components/*` - UI building blocks

## Development Strategy

Work in this order:
1. Keep startup reliable.
2. Keep auth stable.
3. Keep search and upload flows working.
4. Improve UI only after the data flow is sound.
5. Expand tooling and docs last.

## Agent Workstreams

### Workstream A - Backend reliability
Goal: make the API start, validate requests, and return predictable errors.

Focus areas:
- config defaults
- database initialization
- auth token flow
- upload/search endpoints
- runtime dependency safety

Done when:
- backend starts with no extra setup
- `/health` works
- auth endpoints work
- case/search endpoints work with tests

### Workstream B - Frontend usability
Goal: ensure the app has a clean working login -> dashboard -> search flow.

Focus areas:
- login/register pages
- protected routing
- dashboard rendering
- case list/detail pages
- upload/search forms
- error/loading states

Done when:
- user can log in
- dashboard loads without blank screen
- upload/search pages render and call the API correctly

### Workstream C - Data/search correctness
Goal: keep face matching logic consistent and testable.

Focus areas:
- cosine similarity ranking
- FaceRecord corpus queries
- case-based search
- result ordering and filtering

Done when:
- search returns correct ordering
- tests cover the expected API contract
- no hidden Postgres-only startup dependency remains for basic dev

### Workstream D - Dataset/evaluation tooling
Goal: support offline ingestion and measurement of cross-age matching.

Focus areas:
- `scripts/ingest_dataset.py`
- `scripts/evaluate_cross_age.py`
- metrics output
- dataset metadata handling

Done when:
- scripts run consistently
- outputs are documented
- evaluation metrics match the project goal

### Workstream E - Documentation and handoff
Goal: keep repo docs aligned with reality.

Focus areas:
- README
- architecture docs
- progress logs
- setup instructions

Done when:
- setup instructions are accurate
- local dev path is explicit
- no container-based instructions remain

## Known Priorities

### Highest priority
1. Keep backend booting locally.
2. Keep frontend compiling and rendering.
3. Keep auth/session behavior consistent.
4. Keep search endpoints and case upload usable.

### Medium priority
1. Improve dashboard UX.
2. Improve empty/error/loading states.
3. Reduce duplication in API types and hooks.

### Lower priority
1. Deep performance tuning.
2. Optional production deployment hardening.

## Operational Rules for Agents

- Read existing code before editing.
- Prefer surgical fixes over broad rewrites.
- Do not break local startup while making unrelated changes.
- Do not add new abstractions unless they remove real duplication.
- If one fix affects multiple surfaces, update all connected files in the same pass.
- Keep tests small and targeted, then broaden only if needed.

## Validation Checklist

Run the smallest useful validation for the area changed:
- frontend: `npm run build`
- backend: `python -m pytest tests -q`
- startup: run backend and confirm `/health`

If UI flows are changed, verify:
- login page renders
- protected routes redirect properly
- dashboard loads after auth

If upload/search flows are changed, verify:
- form submits correctly
- file uploads use multipart form data
- search results render with type-safe data

## Suggested Next Tasks

### Backend cleanup
- Align README and env examples with the SQLite local-dev path.
- Review any remaining Postgres-specific startup assumptions.
- Ensure search code clearly separates local-dev behavior from production pgvector behavior.

### Frontend polish
- Replace any remaining `unknown`-typed API usage with explicit types.
- Improve error messaging on login, upload, and search failures.
- Ensure pages do not assume data exists before query completion.

### Product flow
- Make the dashboard the landing experience after login.
- Add a clear case creation/upload path.
- Add a clear search results page with similarity scores and metadata.

### Tooling
- Keep tests current with the API contract.
- Add or update fixtures only when required by behavior changes.

## Definition of Done
A feature is done only when:
- it works in local dev without containers,
- it does not break the frontend build,
- relevant tests pass,
- and the behavior is reflected in the docs if the user would need to know about it.

## Notes for Future Agents

- Treat this repo as a live implementation, not a greenfield rewrite.
- Existing code may be partially complete or inconsistent; fix the actual breakage instead of assuming the architecture is wrong.
- When uncertain, favor the simplest working path that preserves the project goal.
