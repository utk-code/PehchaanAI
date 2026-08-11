# TODO List for AI Coding Agent
## Missing Child Identification AI System

**Project:** Project Ace - Missing Child Identification AI  
**Status:** In Progress  
**Current Date:** 2026-08-11  
**Target Launch:** 2026-08-18 (7 days from start)

---

## 🎯 Current Status

- [x] Planning phase complete
- [x] All documentation created
- [x] Phase 1, Day 1 - Environment Setup complete
- [ ] **NEXT ACTION:** Begin Day 2: Authentication & Basic Backend

---

## 📅 1-Week Accelerated Sprint

### Day 1: Environment Setup & Database 
- [x] Create project root directory structure
- [x] Initialize Git repository
- [x] Create `.gitignore` file
- [x] Create `docker-compose.yml` file
- [x] Create README with setup instructions
- [x] Test Docker Compose config

### Day 2: Authentication & Basic Backend ⏳ NEXT
- [ ] Initialize FastAPI project in `backend/` directory
- [ ] Create `requirements.txt` with dependencies (FastAPI, SQLAlchemy, Passlib, etc.)
- [ ] Add PostgreSQL + pgvector to docker-compose.yml
- [ ] Create `backend/database/models.py` (Users table)
- [ ] Implement JWT authentication (login/register endpoints)
- [ ] Initialize React + TypeScript project with Vite in `frontend/`

### Day 3: Face Detection Pipeline & Case Management
- [ ] Create Case model in SQLAlchemy (with `face_embedding` VECTOR)
- [ ] Integrate OpenCV & InsightFace in backend
- [ ] Implement face detection and alignment pipeline
- [ ] Create photo upload endpoint returning 512-d embeddings
- [ ] Create Case creation endpoints

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

**NEXT TASK:** Day 2: Authentication & Basic Backend

**Steps:**
1. Create `backend/requirements.txt`
2. Create basic FastAPI setup (`main.py`)
3. Set up Database models (`models.py`)
4. Create Auth routes

**Good luck! 🚀 Let's build something that helps bring missing children home in a week!**
