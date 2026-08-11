# Tools & Technologies
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. Frontend Development

**Core:**
- React 18.2+ with TypeScript 5.0+
- Vite for build tooling
- Node.js 18+ LTS

**UI & Styling:**
- Tailwind CSS 3.3+
- HeadlessUI (accessible components)
- Heroicons (icon library)

**State Management:**
- Zustand 4.3+ (global state)
- React Query / TanStack Query 4.0+ (server state)

**Other:**
- React Router 6.14+
- React Hook Form 7.45+
- Zod (validation)
- Axios 1.4+

**Testing:**
- Jest 29+
- React Testing Library 14+

---

## 2. Backend Development

**Core:**
- Python 3.11+
- FastAPI 0.100+
- Uvicorn (ASGI server)

**Database:**
- SQLAlchemy 2.0+ (ORM)
- Alembic (migrations)
- psycopg2-binary (PostgreSQL driver)
- pgvector (vector extension)

**Authentication:**
- python-jose (JWT)
- passlib with bcrypt

**Face Recognition:**
- OpenCV 4.8+ (cv2)
- InsightFace 0.7+ (ArcFace model)
- onnxruntime (model inference)
- NumPy 1.24+
- Pillow 10.0+

**AI/ML:**
- OpenAI Python SDK 0.27+ (GPT-4)
- Google Generative AI SDK (Gemini)

**Testing:**
- pytest 7.4+
- pytest-asyncio
- pytest-cov (coverage)
- httpx (async client for testing)

---

## 3. Database

**Primary Database:**
- PostgreSQL 15+
- pgvector extension 0.5+

**Vector Index:**
- IVFFlat (for MVP)
- HNSW (for production scale)

---

## 4. DevOps & Deployment

**Containerization:**
- Docker 24+
- Docker Compose 2.20+

**Web Server:**
- Nginx (reverse proxy, SSL termination)

**Cloud Providers (Options):**
- AWS (ECS, RDS, S3)
- Azure (Container Apps, PostgreSQL, Blob Storage)
- GCP (Cloud Run, Cloud SQL, Cloud Storage)

**Monitoring:**
- Prometheus + Grafana (metrics)
- ELK Stack or CloudWatch (logs)

---

## 5. AI/ML Models & APIs

### Face Recognition
**InsightFace (Primary)**
- Model: ArcFace ResNet100
- Output: 512-dimensional embedding
- Framework: ONNX Runtime
- Installation: `pip install insightface onnxruntime`

### Age Progression
**Options:**
- StyleGAN-based APIs (commercial)
- SAM (Style-based Age Manipulation)
- Third-party API service (recommended for MVP)

### LLM for Reports
**OpenAI GPT-4**
- Model: `gpt-4` or `gpt-4-turbo`
- Cost: ~$0.03 per 1K tokens
- Installation: `pip install openai`

**Google Gemini Pro**
- Model: `gemini-pro`
- Free tier available
- Installation: `pip install google-generativeai`

---

## 6. Development Environment

**Prerequisites:**
- Git 2.40+
- Docker Desktop
- Node.js 18+ LTS
- Python 3.11+
- VS Code (recommended)

**Environment Variables:**

Backend (.env):
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/missingchild
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...
AGE_PROGRESSION_API_URL=https://...
MAX_UPLOAD_SIZE_MB=10
```

Frontend (.env):
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Missing Child ID System
```

---

## 7. Package Management

### Backend (requirements.txt)
```
fastapi==0.100.0
uvicorn[standard]==0.23.0
sqlalchemy==2.0.19
alembic==1.11.1
psycopg2-binary==2.9.6
pgvector==0.2.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
opencv-python==4.8.0
insightface==0.7.3
onnxruntime==1.15.1
numpy==1.24.3
Pillow==10.0.0
openai==0.27.8
pydantic==2.0.3
pytest==7.4.0
```

### Frontend (package.json - key dependencies)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.0",
    "axios": "^1.4.0",
    "@tanstack/react-query": "^4.32.0",
    "zustand": "^4.3.9",
    "react-hook-form": "^7.45.0"
  }
}
```

---

## 8. Testing Tools

**Backend:**
```bash
pytest tests/ -v --cov=backend --cov-report=html
```

**Frontend:**
```bash
npm test -- --coverage
```

**E2E (Optional):**
- Playwright or Cypress

---

## 9. Monitoring & Logging

**Prometheus (Metrics):**
- Scrape FastAPI metrics
- Custom dashboards in Grafana

**Logging:**
```python
import structlog
logger = structlog.get_logger()
logger.info("case_created", case_id=case.id)
```

---

## 10. Recommended VS Code Extensions

- Python (Microsoft)
- Pylance (Microsoft)
- ESLint (Microsoft)
- Prettier - Code formatter
- Tailwind CSS IntelliSense
- Docker (Microsoft)
- PostgreSQL
- GitLens
- Thunder Client

---

**Document Owner:** DevOps Team  
**Last Updated:** August 10, 2026
