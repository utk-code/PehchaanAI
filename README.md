# PehchaanAI: Cross-Age Face Recognition for Missing Child Identification

A research prototype evaluating whether face recognition can retrieve the same person across significant age gaps — motivated by missing child identification scenarios.

**Version:** 2.0 (Revised Scope)  
**Status:** Implementation Phase (Days 1-4 complete)  

---

## ��� Project Overview

**Core Technical Question:**
> "Can a face-recognition system retrieve the same person from a database when the query photograph and database photograph are separated by a significant age gap?"

**Example:**
- Person A has a photo at age 7 and another at age 18
- System receives ONLY the age-7 photo as query
- System should ideally retrieve Person A's age-18 photo among Top-K results

This simulates a missing-child identification scenario **without using real missing-child records**. We use public research face datasets (MORPH, CACD, FG-NET, AgeDB) containing people photographed at different ages.

**Important:** This is a **research prototype**, not a production police/NGO system. It does NOT connect to CCTV, Aadhaar, social media, or law-enforcement databases.

---

## ������ Tech Stack

**Frontend:** React 18+ (TypeScript), Vite, Tailwind CSS, React Router, Axios, TanStack Query  
**Backend:** Python 3.11+ (FastAPI), SQLite for local dev or PostgreSQL 15+ (pgvector) for full vector search, SQLAlchemy 2.0, InsightFace (ArcFace), OpenCV  
**Infrastructure:** JWT auth, local development only  

---

## ��� Project Structure

```
PehchaanAI/
├── backend/
│   ├── auth/              # JWT auth + password hashing
│   ├── cases/             # Query case CRUD + photo upload
│   ├── database/          # SQLAlchemy models (User, Case, FaceRecord)
│   ├── face/              # InsightFace detection + ArcFace embedding
│   ├── search/            # Pure cosine similarity search
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/              # React + TypeScript (Vite)
├── scripts/
│   ├── ingest_dataset.py     # Ingest research datasets into face_records
│   └── evaluate_cross_age.py # Cross-age recognition evaluation
├── tests/                 # Unit tests (pytest)
├── TODO.md
├── PROGRESS.md
├── Architecture.md
��── README.md
```

---

## ��� Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 24+
- No container runtime required
- (Optional) GPU for InsightFace acceleration

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # PowerShell Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
copy backend/.env.example backend/.env  # Windows
# cp backend/.env.example backend/.env  # Linux/macOS

# Edit backend/.env with your DATABASE_URL and JWT_SECRET_KEY
# DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/pehchaanai

# Run database migrations (tables created on app startup)
# Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173 (proxies API to backend:8000)
```

## ��� Dataset Ingestion

To populate the searchable corpus with research datasets (MORPH, CACD, FG-NET, etc.):

### Option A: From CSV Metadata
```bash
# CSV columns: image_path, person_id, age, capture_year, dataset
python scripts/ingest_dataset.py \
  --csv /path/to/metadata.csv \
  --images-root /path/to/images \
  --dataset-name MORPH
```

### Option B: From Directory Structure
```
dataset_root/
├── person_001/
│   ├── 7.jpg      # age 7
│   ├── 18_2010.jpg # age 18, year 2010
├── person_002/
│   ├── 5.png
```

```bash
python scripts/ingest_dataset.py \
  --dataset-dir /path/to/dataset_root \
  --dataset-name FG-NET
```

---

## ��� Cross-Age Evaluation

Measure how well the system retrieves same-person matches across age gaps:

```bash
python scripts/evaluate_cross_age.py \
  --dataset MORPH \
  --top-k 20 \
  --min-age-gap 5 \
  --output results.json
```

**Outputs:**
- Rank-1 / Rank-5 / Rank-10 accuracy
- Mean Reciprocal Rank (MRR)
- CMC Curve (Cumulative Match Characteristic)

---

## ��� API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new investigator |
| POST | `/auth/login` | Get JWT access token |
| GET | `/auth/me` | Get current user info |

### Cases (Query Management)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/cases/photo/embedding` | Extract face embedding from photo (preview) |
| POST | `/cases/photo/upload` | Upload photo + optionally create case |
| POST | `/cases` | Create case with pre-computed embedding |
| GET | `/cases` | List investigator's cases |
| GET | `/cases/{id}` | Get case details |
| PATCH | `/cases/{id}` | Update case |
| DELETE | `/cases/{id}` | Soft delete case |

### Search (Face Corpus)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search` | Search with explicit 512-d embedding |
| GET | `/search/case/{case_id}` | Search using stored case embedding |
| POST | `/search/photo` | Upload photo → extract embedding → search |

---

## ��� Testing

```bash
# Run all tests
python -m pytest tests -v

# Check code style
python -m black --check backend tests
python -m flake8 backend tests
```

---

## ��� Current Status (Day 4 Complete)

| Component | Status |
|-----------|--------|
| Auth (JWT) | �� Done |
| Face Detection + ArcFace Embedding | �� Done |
| Case Management (CRUD + Photo Upload) | �� Done |
| FaceRecord Corpus Model | �� Done |
| IVFFlat Index + Cosine Search | �� Done |
| Search API (3 endpoints) | �� Done |
| Dataset Ingestion Pipeline | �� Done |
| Cross-Age Evaluation Script | �� Done |
| Frontend Dashboard | ��� Day 5 |

---

## ��� Ethics & Scope

- **No real missing child data** — uses only public research datasets
- **No surveillance capabilities** — single-image query → corpus search only
- **Investigative leads only** — all matches require human review + formal verification (DNA, etc.)
- **Access controlled** — JWT auth, users only see their own queries
- **Audit logging** — planned

---

## ��� Documentation

- `TODO.md` — Task tracking and sprint plan
- `PROGRESS.md` — Daily progress log
- `Architecture.md` — System architecture and design decisions
- `PRD.md` — Product Requirements Document
- `ADR.md` — Architecture Decision Records

---

## ��� Contributing

This is a college prototype. Issues/PRs welcome for:
- Dataset ingestion improvements
- Evaluation methodology
- Frontend UX
- Performance optimization
- Documentation

---

## ��� License

MIT License — for research and educational purposes.
