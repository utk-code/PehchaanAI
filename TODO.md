# TODO List for AI Coding Agent
## Missing Child Identification AI System

**Project:** PehchaanAI - Missing Child Identification AI
**Status:** In Progress  
**Current Date:** 2026-08-11  
**Target Launch:** 2026-08-18 (7 days from start)

---

## 🎯 Current Status

- [x] Planning phase complete
- [x] All documentation created
- [x] Phase 1, Day 1 - Environment Setup complete
- [x] Phase 1, Day 2 - Authentication & Basic Backend complete
- [x] **NEXT ACTION:** Begin Day 3: Face Detection Pipeline & Case Management
- [ ] **NEXT ACTION:** Begin Day 4: Vector Search & Multi-Factor Ranking

---

## 📅 1-Week Accelerated Sprint

### Day 1: Environment Setup & Database 
- [x] Create project root directory structure
- [x] Initialize Git repository
- [x] Create `.gitignore` file
- [x] Create `docker-compose.yml` file
- [x] Create README with setup instructions
- [x] Test Docker Compose config

### Day 2: Authentication & Basic Backend
- [x] Initialize FastAPI project in `backend/` directory
- [x] Create `requirements.txt` with dependencies (FastAPI, SQLAlchemy, JWT, password hashing, etc.)
- [x] Add PostgreSQL + pgvector to docker-compose.yml
- [x] Create `backend/database/models.py` (Users table)
- [x] Implement JWT authentication (login/register endpoints)
- [x] Initialize React + TypeScript project with Vite in `frontend/`

### Day 3: Face Detection Pipeline & Case Management
- [x] Create Case model in SQLAlchemy (with `face_embedding` VECTOR)
- [x] Integrate OpenCV & InsightFace in backend
- [x] Implement face detection and alignment pipeline
- [x] Create photo upload endpoint returning 512-d embeddings
- [x] Create Case creation endpoints

### Day 4: Vector Search & Multi-Factor Ranking
- [ ] Populate database with test candidates and embeddings
- [ ] Implement IVFFlat index on `face_embedding`
- [ ] Implement cosine similarity vector search query
- [ ] Implement multi-factor ranking (weighing age, location, date, face similarity)
- [ ] Create Search Results endpoint

### Day 5: Frontend Dashboard & Upload UI
- [ ] Create PhotoUpload drag & drop component in React
- [ ] Create Case Creation form UI
- [ ] Create Dashboard Layout
- [ ] Build Candidate Card components to show results and similarity scores
- [ ] Test End-to-End search flow

### Day 6: Age Progression Integration & AI Reports
- [ ] Integrate Age Progression API (async image generation +5, +10, +15 years)
- [ ] Display age-progressed images in Dashboard
- [ ] Integrate OpenAI/Gemini API for investigation reports
- [ ] Add AI report generation endpoint with safety constraints
- [ ] Display AI report in Dashboard

### Day 7: Testing, Bug Fixes & Deployment
- [ ] Run complete end-to-end integration tests
- [ ] Optimize slow queries and fix bugs
- [ ] Polish UI/UX issues
- [ ] Set up production Docker builds
- [ ] Final documentation update
- [ ] **🚀 LAUNCH!**

---

## 📝 Notes for AI Coding Agent

### Before Starting Each Task:
1. Read task description and acceptance criteria
2. Review related code files (if any exist)
3. Check relevant documentation (Architecture.md, Rules.md)
4. Plan approach and identify dependencies

### While Implementing:
1. Follow coding standards (PEP 8 for Python, Airbnb for TypeScript)
2. Use type hints (Python) and TypeScript types
3. Write docstrings and comments
4. Handle errors gracefully

### After Completing Each Task:
1. Write unit tests (aim for 80% coverage)
2. Run tests and verify they pass
3. Update documentation
4. Commit with clear message
5. **CRITICAL RULE**: Update this `TODO.md` (check off completed items) and `PROGRESS.md` at the end of each major task/day.

---

## 🎯 Current Action (Start Here!)

**NEXT TASK:** Day 3: Face Detection Pipeline & Case Management

**Steps:**
1. Create Case model in SQLAlchemy
2. Integrate OpenCV and InsightFace
3. Implement face detection and alignment pipeline
4. Create photo upload endpoint returning embeddings
5. Create Case creation endpoints

**Good luck! 🚀 Let's build something that helps bring missing children home in a week!**
