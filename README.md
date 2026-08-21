# PehchaanAI: Cross-Age Face Recognition for Missing Child Identification

A research prototype evaluating whether face recognition can retrieve the same
person across significant age gaps — motivated by missing-child identification
scenarios.

**Status:** Core system complete (days 1-5) — case flow, corpus ingestion,
cross-age evaluation, real reports, and quality-warning search all working.
Age progression uses **weighted filter-based search** (see below).

---

## Core Technical Question

> Can a face-recognition system retrieve the same person from a database when
> the query photograph and database photograph are separated by a significant
> age gap?

Example: Person A has a photo at age 7 and another at age 18. The system
receives only the age-7 photo and should retrieve Person A's age-18 photo in
the top-K results.

We use public research datasets (FG-NET, etc.), not real missing-child
records. This is a **research prototype**, not a production law-enforcement
system: it does not connect to CCTV, Aadhaar, social media, or police
databases.

---

## Tech Stack

- **Backend:** Python 3.11+ · FastAPI · SQLAlchemy 2.0 · InsightFace
  (ArcFace, `buffalo_s` by default) · OpenCV · SQLite (local dev)
- **Frontend:** React 18 + TypeScript · Vite · Tailwind CSS v4 · React Router ·
  TanStack Query · Framer Motion
- **Auth:** JWT (Argon2 password hashing via `pwdlib`)
- **Search:** pure cosine similarity over stored 512-d face embeddings

---

## Project Structure

```
PehchaanAI/
├── backend/
│   ├── auth/          # JWT auth + password hashing
│   ├── cases/         # Query case CRUD + photo upload
│   ├── database/      # SQLAlchemy models (User, Case, FaceRecord)
│   ├── face/          # InsightFace detection + ArcFace embedding pipeline
│   ├── reports/       # Rule-based investigation reports
│   ├── search/        # Cosine similarity search + ranking
│   ├── main.py        # FastAPI app (static mounts /uploads, /ref-images)
│   └── requirements.txt
├── frontend/          # React + TypeScript (Vite)
├── scripts/
│   ├── ingest_dataset.py      # Ingest FG-NET into face_records
│   ├── evaluate_cross_age.py  # Cross-age recognition evaluation
│   └── smoke_search.py        # Live end-to-end model + search smoke test
├── tests/             # pytest suite (unit + API + integration)
├── pehchaanai.db      # SQLite database (gitignored)
└── docs: TODO.md, PROGRESS.md, API.md, for_user.md, Architecture.md
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+ (frontend uses Vite 8)
- No container runtime required; InsightFace runs on CPU (`ctx_id=-1`)

### 1. Backend

```powershell
# PowerShell (Windows)
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r backend/requirements.txt

copy backend/.env.example backend/.env
# DB defaults to sqlite+pysqlite:///./pehchaanai.db at the repo root.
# Set JWT_SECRET_KEY to something long; FACE_MODEL_NAME=buffalo_s is fine for CPU.

uvicorn backend.main:app --reload --port 8000
```

On first use InsightFace downloads its model pack to
`~/.insightface/models/` automatically.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev          # http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000` (see
`frontend/vite.config.ts`). The API base is relative (`/api`), so the app
works from localhost and any LAN device without CORS issues.

### 3. Dataset ingestion

Populate the searchable corpus from the FG-NET dataset:

```powershell
# Requires FG-NET images in FGNET/images/ (folder is gitignored)
python scripts/ingest_dataset.py --images-root FGNET/images --dataset FGNET
```

The checked-in `pehchaanai.db` is gitignored; a freshly ingested corpus
contains ~609 usable FG-NET records across 82 persons (ages 0-69).

### 4. Age Progression

The system supports **cross-age matching** using weighted filter-based search:

1. **Upload a photo** on the Search page.
2. **Select a target age group** (Child, Teen, Adult, Senior, or Custom Age).
3. **Search** — the system filters corpus records by age ranges and ranks
   results using weighted similarity scores.

**How it works:**
- Each age range carries a relevance weight (0.6–1.0).
- Results are combined and sorted by `similarity × weight`.
- Higher weight = closer to target age = higher priority in results.

**Limitations:**
- No visual age progression (transforming faces to look older/younger).
- Filter-based approach is less precise than model-based age progression.
- See `LIMITATIONS.md` for details on why visual models were not used.

---

## Testing

```powershell
# Full unit + API suite (mocked face pipeline; 107 tests)
python -m pytest tests -q

# Real-model integration tests (auto-skipped unless requested)
python -m pytest tests -m integration -q

# Lint / format
python -m black --check backend tests
python -m flake8 backend tests --max-line-length=88

# Frontend build (type-checks + bundles)
cd frontend; npm run build
```

---

## Evaluation & Verification

```powershell
# Cross-age recognition over the full corpus (607 queries, 82 persons)
python scripts/evaluate_cross_age.py --database-url "sqlite:///pehchaanai.db"

# Live smoke test: auth -> real model -> /search/photo -> same-person rank 1
python scripts/smoke_search.py
```

Baseline results (2026-08-16, FG-NET corpus, self-exclusion protocol):
Rank-1 23% · Rank-5 80% · **Rank-10 89.5%** · MRR 0.46. The Day-7 success
criterion of Rank-10 > 70% is met.

## Performance (2026-08-16, CPU, 609-record corpus)

| Operation | Avg | Day-7 bar | Result |
|---|---|---|---|
| Face detection + embedding | 0.23s | < 2s | PASS |
| Full search (detect+embed+scan) | 0.50s | < 5s | PASS |
| Pure cosine scan | 0.28s | — | PASS |

Search is vectorized (single numpy matmul over all corpus embeddings).

> **Note:** on some Windows machines `http://localhost:5173` / `:8000` can add
> ~2s per request due to IPv6 (`::1`) loopback throttling. If the UI feels
> slow, open `http://127.0.0.1:5173` instead — the code itself is fast.

---

## API Reference

All routes are under `/api` from the frontend (proxy) or at the backend root
directly. Auth via `Authorization: Bearer <token>`.

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account, returns JWT |
| POST | `/auth/login` | Form login (`username`/`password`), returns JWT |
| GET | `/auth/me` | Current user |
| GET | `/health` | Liveness check |
| GET | `/cases` | List own cases |
| POST | `/cases` | Create case (requires 512-d `face_embedding` + `photo_path`) |
| GET | `/cases/{id}` | Case detail |
| PATCH | `/cases/{id}` | Update case |
| DELETE | `/cases/{id}` | Soft-delete case |
| POST | `/cases/photo/embedding` | Extract embedding only (strict quality) |
| POST | `/cases/photo/upload` | Upload photo, optionally create case (`create_case=true` + `query_name`) |
| POST | `/search` | Search by embedding (JSON body) |
| GET | `/search/case/{id}` | Search by stored case embedding |
| POST | `/search/photo` | Upload photo + search (**soft quality**: low-quality faces warn, don't 400) |
| GET | `/reports/{case_id}` | Generate a rule-based investigation report |
| GET | `/uploads/{file}` | Served case query photos |
| GET | `/ref-images/{file}` | Served corpus reference images |

Search responses include `total_records`, ranked `results`, and an optional
`quality_warning` (set when a detected face failed the quality checks).

---

## Behavioral Notes

- **Case creation is strict**: photos whose faces are missing, too small, or
  low-confidence are rejected with a 400 so a bad embedding never becomes a
  permanent case query. `/search/photo` is lenient — it returns results with a
  `quality_warning` instead.
- **Age progression uses weighted filter-based search**: When a target age group
  is selected, the system filters corpus records by age ranges and ranks
  results using weighted similarity scores. See the "Dataset ingestion" section
  above for details. Visual age progression (generating aged faces) is not
  implemented — see `LIMITATIONS.md`.
- Reports are rule-based, not LLM-generated.
- Interactive API docs are available at `http://localhost:8000/docs`.
