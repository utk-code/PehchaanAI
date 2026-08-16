# System Architecture Document
## PehchaanAI - Cross-Age Face Recognition for Missing Child Identification

**Version:** 2.0  
**Date:** August 14, 2026  
**Status:** Implementation Phase (Days 1-4 complete)

---

## 1. Architecture Overview

The system is a **research prototype** for cross-age face recognition. It evaluates whether a face recognition system can retrieve the same person from a database when the query photograph and database photograph are separated by a significant age gap.

```
��─────────────────────────────────────────────────────────────��
│                      Client Layer (React)                    │
│  ��──────────────��  ��──────────────��  ��──────────────��      │
│  │ Query Form   │  │ Results Grid │  │ Admin/Upload │      │
│  └──────────────��  └──────────────��  └──────────────��      │
��────────────────────────────��────────────────────────────────��
                             │ HTTPS/REST API
��────────────────────────────��────────────────────────────────��
│                   Application Layer (FastAPI)                │
│  ��──────────────��  ��──────────────��  ��──────────────��      │
│  │ Auth Service │  │ Case Service │  │ Face Service │      │
│  └──────────────��  └──────────────��  └──────────────��      │
│  ��──────────────��                                          │
│  │Search Service│  (Pure cosine similarity)                │
│  └──────────────��                                          │
��────────────────────────────��────────────────────────────────��
                             │
��────────────────────────────��────────────────────────────────��
│                     Data & Storage Layer                     │
│  ��──────────────��  ��──────────────��  ��──────────────��      │
│  │ PostgreSQL   │  │ File Storage │  │ Research     │      │
│  │ + pgvector   │  │  (Images)    │  │ Datasets     │      │
│  └──────────────��  └──────────────��  └──────────────��      │
��─────────────────────────────────────────────────────────────��
```

---

## 2. Component Architecture

### 2.1 Frontend Layer (React + TypeScript + Vite)

**Technology Stack:**
- React 18+ with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication
- React Query / TanStack Query for server state

**Key Components:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/           (LoginForm, RegisterForm)
│   │   ├── query/          (QueryForm, PhotoUploader)
│   │   ├── results/        (ResultGrid, ResultCard, SimilarityBadge)
│   │   └── common/         (Header, LoadingSpinner, ErrorToast)
│   ├── pages/
│   │   ├── Home.tsx        (Landing / Query form)
│   │   ├── Results.tsx     (Search results display)
│   │   ├── Admin.tsx       (Dataset upload / management)
│   │   └── Login.tsx
│   ├── services/
│   │   ├── api.ts          (Axios instance + endpoints)
│   │   └── auth.ts
│   └── hooks/
```

### 2.2 Backend Layer (FastAPI)

**Technology Stack:**
- Python 3.11+
- FastAPI framework
- Pydantic v2 for data validation
- SQLAlchemy 2.0 ORM
- JWT authentication (python-jose + pwdlib/argon2)

**Directory Structure:**
```
backend/
├── auth/              (JWT auth, password hashing)
├── cases/             (Query case CRUD + photo upload)
├── database/          (SQLAlchemy models, session)
├── face/              (InsightFace detection + ArcFace embedding)
│   ├── detector.py
│   ├── embedder.py
│   ├── pipeline.py
│   └── exceptions.py
├── search/            (Pure cosine similarity search)
│   ├── service.py
│   ├── routes.py
│   └── schemas.py
├── config.py
├── main.py
��── requirements.txt
```

---

## 3. Database Schema (PostgreSQL + pgvector)

### Core Tables:

#### `users` - Authentication
```sql
id (UUID PK)
email (unique, indexed)
full_name
hashed_password
is_active
created_at, updated_at
```

#### `cases` - Query scenarios (childhood photo uploaded for search)
```sql
id (UUID PK)
investigator_id (FK → users.id)
query_name, query_age, query_date, query_location, notes
photo_path (stored image path)
face_embedding (VECTOR(512))  -- ArcFace embedding of query image
status (active/archived)
created_at, updated_at, deleted_at (soft delete)
```

#### `face_records` - Searchable corpus (research dataset photos)
```sql
id (UUID PK)
person_id (INDEXED)           -- Same person_id = same identity across ages
age                           -- Age at time of this photo
capture_year (nullable)       -- Year photo was taken
dataset                       -- Source dataset name (MORPH, CACD, FG-NET, etc.)
metadata_json (nullable)      -- Additional metadata
photo_path                    -- Path to image file
face_embedding (VECTOR(512))  -- ArcFace embedding
created_at

INDEX: IVFFlat on face_embedding (vector_cosine_ops)
INDEX: person_id
INDEX: dataset
```

---

## 4. Data Flow

### 4.1 Ingestion Pipeline (Offline / Admin)
```
Research Dataset (MORPH/CACD/FG-NET)
         │
         ��
scripts/ingest_dataset.py
         │
         ├── Parse metadata (CSV or directory structure)
         ├── Extract face embedding (InsightFace ArcFace)
         ├── Store FaceRecord in PostgreSQL + pgvector
         └── IVFFlat index enables fast cosine search
```

### 4.2 Query Pipeline (Online / User)
```
User uploads childhood photo
         │
         ��
POST /cases/photo/upload  →  FacePipeline (detect → align → embed)
         │
         ��
POST /search/photo  →  pgvector cosine similarity (<=> operator)
         │
         ��
Top-K FaceRecords ranked by similarity
         │
         ��
Frontend displays: thumbnail + person_id + age + dataset + similarity score
```

### 4.3 Evaluation Pipeline (Offline / Research)
```
scripts/evaluate_cross_age.py
         │
         ├── For each person_id with ≥2 photos:
         │     For each photo as query:
         │         Search corpus
         │         Check rank of other same-person photos
         │         (with min age gap filter)
         │
         ├── Outputs:
         │     Rank-1/5/10 accuracy
         │     Mean Reciprocal Rank (MRR)
         │     CMC Curve (Cumulative Match Characteristic)
```

---

## 5. Key Design Decisions

### 5.1 Pure Cosine Similarity (No Multi-Factor Ranking)
- **Removed**: Arbitrary weights for age/location/date scoring
- **Reason**: Unvalidated heuristics; biometric similarity is the only scientifically grounded signal
- **Future**: If multimodal model is validated, can be added

### 5.2 Case vs FaceRecord Separation
- **Case** = Query scenario (user uploads a childhood photo to search)
- **FaceRecord** = Corpus entry (one photo of a person at a specific age from research dataset)
- Same `person_id` across multiple FaceRecords enables cross-age evaluation

### 5.3 IVFFlat Index
- PostgreSQL pgvector IVFFlat with `vector_cosine_ops`
- Lists parameter tuned for dataset size (default 100)
- Enables sub-5-second search on 10K+ records

### 5.4 ArcFace (InsightFace) Embedding
- 512-dimensional, L2-normalized
- Trained on MS1M, robust to pose/illumination
- Standard choice for cross-age research

---

## 6. API Endpoints

### Auth
- `POST /auth/register` - Register investigator
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Current user info

### Cases (Query Management)
- `POST /cases/photo/embedding` - Extract embedding only (preview)
- `POST /cases/photo/upload` - Upload + extract + optional case creation
- `POST /cases` - Create case with pre-computed embedding
- `GET /cases` - List investigator's cases
- `GET /cases/{id}` - Get case details
- `PATCH /cases/{id}` - Update case
- `DELETE /cases/{id}` - Soft delete

### Search
- `POST /search` - Search with explicit embedding
- `GET /search/case/{case_id}` - Search using stored case
- `POST /search/photo` - Upload photo → extract embedding → search

---

## 7. Evaluation Methodology

The `scripts/evaluate_cross_age.py` implements standard face recognition evaluation:

| Metric | Definition |
|--------|------------|
| Rank-1 Accuracy | % queries where same person (age gap ≥ N) at rank 1 |
| Rank-K Accuracy | % queries where same person in top K |
| MRR | Mean of 1/rank for first correct match |
| CMC Curve | Cumulative Match Characteristic: P(rank ≤ k) vs k |

**Minimum Age Gap**: Default 5 years (configurable) to ensure cross-age challenge.

---

## 8. Future Extensions (Post-MVP)

| Feature | Status | Notes |
|---------|--------|-------|
| Age Progression API | Planned | External API or local GAN (e.g., SAM, StyleGAN) |
| LLM Investigation Report | Planned | Summarize top matches + caveats |
| CCTV/Video Ingestion | Not planned | Out of scope for research prototype |
| Active Learning | Future | Human-in-the-loop label correction |
| Redis Caching | Future | Cache frequent queries |
| Celery Async Tasks | Future | Offload ingestion/embedding |

---

## 9. Security & Ethics

- **No real missing child data**: Uses only public research datasets
- **No surveillance**: Single-image query → corpus search
- **Access control**: JWT auth, users only see their own queries
- **Audit logging**: All searches logged (planned)
- **Data retention**: Soft delete, configurable retention (planned)

---

## 10. Performance Targets

| Metric | Target |
|--------|--------|
| Embedding extraction | < 2 seconds |
| Vector search (10K records) | < 5 seconds |
| End-to-end query → results | < 10 seconds |
| Rank-10 cross-age (5+ year gap) | > 70% |
| Concurrent users | 20+ |
