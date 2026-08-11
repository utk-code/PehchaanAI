# System Architecture Document
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026  
**Status:** Planning Phase

---

## 1. Architecture Overview

The system follows a modern three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer (React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Case Mgmt UI │  │ Dashboard UI │  │  Admin UI    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS/REST API
┌────────────────────────────┴────────────────────────────────┐
│                   Application Layer (FastAPI)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ API Gateway  │  │  Auth Service│  │ Case Service │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Face Service │  │Search Service│  │ Report Svc   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                     Data & Storage Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │ File Storage │  │ External APIs│      │
│  │ + pgvector   │  │  (Images)    │  │ (LLM, Age)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Layer (React + Tailwind CSS)

**Technology Stack:**
- React 18+ with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication
- React Query for state management
- Zustand for global state

**Directory Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/           (LoginForm, RegisterForm)
│   │   ├── cases/          (CaseForm, CaseList, CaseDetails)
│   │   ├── dashboard/      (MatchDashboard, CandidateList)
│   │   ├── upload/         (PhotoUpload, FacePreview)
│   │   └── common/         (Header, Sidebar, LoadingSpinner)
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   └── types/
```

### 2.2 Backend Layer (FastAPI)

**Technology Stack:**
- Python 3.11+
- FastAPI framework
- Pydantic for data validation
- SQLAlchemy ORM
- JWT authentication

**Directory Structure:**
```
backend/
├── api/              (routes: auth, cases, search, reports)
├── face/             (detector, aligner, embedder, quality)
├── matching/         (vector_search, ranker, filters)
├── aging/            (progression API wrapper)
├── reports/          (LLM report generation)
├── database/         (models, repositories)
├── core/             (config, security, exceptions)
└── utils/            (file_storage, validators)
```

---

## 3. Database Schema (PostgreSQL + pgvector)

**Core Tables:**

1. **users** - Authentication and user management
   - id (UUID), username, email, password_hash, role

2. **cases** - Missing child cases with embeddings
   - id (UUID), child_name_encrypted, age_at_disappearance
   - date_missing, location, photo_path
   - face_embedding (VECTOR 512), status

3. **candidates** - Database of found individuals
   - id (UUID), photo_path, face_embedding (VECTOR 512)
   - current_age, date_found, location_found

4. **search_results** - Search history and scores
   - case_id, candidate_id, similarity_score
   - age_score, date_score, location_score, composite_score

5. **age_progressions** - Generated images
   - case_id, target_age, image_path

6. **ai_reports** - LLM-generated reports
   - case_id, report_text, model_used

**Indexes:**
- IVFFlat index on face_embedding for fast vector search

---

## 4. Integration Points

### 4.1 Face Recognition (InsightFace/ArcFace)
- Input: Aligned face image (112x112)
- Output: 512-dimensional embedding vector
- Pretrained model, no training required

### 4.2 Age Progression
- External API or pretrained StyleGAN model
- Generate images at +5, +10, +15 years

### 4.3 LLM Report Generation (OpenAI/Gemini)
- Structured prompt with case + candidate data
- Temperature: 0.3 (factual)
- Output: Markdown report

### 4.4 Vector Search (pgvector)
- Cosine similarity metric
- Returns Top-10 candidates in < 5 seconds

---

## 5. Security Architecture

- HTTPS/TLS 1.3 transport encryption
- JWT authentication with RS256
- bcrypt password hashing (cost 12)
- Rate limiting: 100 req/min per IP
- Audit logging for all searches

---

## 6. Deployment (Docker)

```yaml
services:
  frontend:    # React app (port 3000)
  backend:     # FastAPI app (port 8000)
  postgres:    # PostgreSQL with pgvector
  nginx:       # Reverse proxy & SSL
```

---

## 7. Performance Targets

- Search response: < 5 seconds (10K database)
- Face embedding: < 2 seconds per image
- Page load: < 3 seconds
- Concurrent users: 20 simultaneous

---

**Document Owner:** Architecture Team  
**Last Updated:** August 10, 2026
