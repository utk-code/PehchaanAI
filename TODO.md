# TODO List
## PehchaanAI - Cross-Age Face Recognition for Missing Child Identification

**Project:** PehchaanAI - Cross-Age Face Recognition
**Status:** In Progress  
**Current Date:** 2026-08-16  

---

## 🎯 Current Status

- [x] Planning phase complete
- [x] All documentation created
- [x] Phase 1, Day 1 - Environment Setup complete
- [x] Phase 1, Day 2 - Authentication & Basic Backend complete
- [x] Phase 2, Day 3 - Face Detection Pipeline complete
- [x] Phase 2, Day 4 - Vector Search (revised to pure cosine similarity)
- [x] Day 5 - Frontend Dashboard & Upload UI built (pages, layout, upload, results)
- [x] Dashboard bug fixes (sidebar layout, hidden content, CORS/auth) - done
- [x] Dataset ingestion - FG-NET loaded into face_records (609/1002, all 82 persons, ages 0-69)
- [x] **End-to-end search flow test** (create case -> upload -> search -> results) - 13 E2E API tests, 97 total
- [ ] Day 6 - Documentation & polish

---

## 📅 Development Sprint

### Day 1: Environment Setup & Database 
- [x] Create project root directory structure
- [x] Initialize Git repository
- [x] Create `.gitignore` file
- [x] Create local development setup files
- [x] Create README with setup instructions
- [x] Test backend/frontend local startup

### Day 2: Authentication & Basic Backend
- [x] Initialize FastAPI project in `backend/` directory
- [x] Create `requirements.txt` with dependencies
- [x] Add PostgreSQL + pgvector support to backend search path
- [x] Create `backend/database/models.py` (Users table)
- [x] Implement JWT authentication (login/register endpoints)
- [x] Initialize React + TypeScript project with Vite in `frontend/`

### Day 3: Face Detection Pipeline
- [x] Integrate InsightFace in backend
- [x] Implement face detection and alignment pipeline
- [x] Create photo upload endpoint returning 512-d ArcFace embeddings
- [x] Create Case model for query scenarios

### Day 4: Vector Search (Revised)
- [x] Create FaceRecord model (searchable corpus with person_id, age, dataset)
- [x] Implement IVFFlat index on `face_embedding`
- [x] Implement pure cosine similarity search (removed arbitrary multi-factor ranking)
- [x] Create Search endpoints (`POST /search`, `GET /search/case/{id}`, `POST /search/photo`)
- [x] Add dataset ingestion pipeline (`scripts/ingest_dataset.py`)
- [x] Add cross-age evaluation script (`scripts/evaluate_cross_age.py`)

### Day 5: Frontend Dashboard & Upload UI
- [x] Create Dashboard Layout (sidebar, header, mobile drawer)
- [x] Create PhotoUpload drag & drop component in React
- [x] Create Query form UI
- [x] Create Result Card components showing retrieved photos + similarity scores
- [x] Fix /dashboard broken layout + invisible content (Playwright verified desktop/mobile)
- [x] Fix auth/register "Failed to fetch" (CORS allowlist for LAN + 127.0.0.1)
- [x] Test End-to-End search flow (97 backend tests, 99% coverage)

### Day 6: Documentation & Polish
- [x] Complete README with usage instructions (rewrote: stack, structure, quickstart, testing, eval, perf)
- [x] Add API documentation (rewrote API.md to match the real backend routes)
- [x] Performance testing and optimization (vectorized search, targets met — see PROGRESS.md)
- [x] UI polish (dark glassmorphism redesign; Playwright-verified desktop/mobile)
- [x] Update for_user.md to reflect the finished core system

---

## 🔬 Core Technical Question

**"Can a face-recognition system retrieve the same person from a database when the query photograph and database photograph are separated by a significant age gap?"**

Example scenario:
- Person A has a photo at age 7 and another at age 18
- System receives ONLY the age-7 photo as query
- System should ideally retrieve Person A's age-18 photo among Top-K results

This simulates missing-child identification without using real missing-child records.

---

## 📊 Evaluation Metrics

The `scripts/evaluate_cross_age.py` script measures:
- **Rank-1 accuracy**: Is the same person's other photo at rank 1?
- **Rank-5/10 accuracy**: Is any same-person photo in top 5/10?
- **Mean Reciprocal Rank (MRR)**
- **CMC Curve**: Cumulative Match Characteristic

---

## 📁 Project Structure

```
backend/
├── database/models.py    # User, Case, FaceRecord models
├── face/pipeline.py      # InsightFace detection + ArcFace embedding
├── search/
│   ├── service.py        # Pure cosine similarity search
│   ├── routes.py         # Search API endpoints
│   └── schemas.py        # Request/response schemas
└── cases/                # Query case management

scripts/
├── ingest_dataset.py     # Ingest research datasets (MORPH, CACD, etc.)
└── evaluate_cross_age.py # Cross-age recognition evaluation

frontend/                 # React + TypeScript (Vite)
```

---

## 🎯 Success Criteria

- Query image → Top-K results in < 5 seconds
- Rank-10 accuracy > 70% for age gaps of 5+ years
- Clean, professional UI for query → results workflow
- Documented API and evaluation methodology
