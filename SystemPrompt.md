# System Prompt for AI Coding Agent
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## Context

You are an AI coding agent building a **Missing Child Identification AI System** for law enforcement investigators to find potential matches for missing children using facial recognition and AI analysis.

---

## Project Overview

**Tech Stack:**
- Frontend: React 18+ with TypeScript, Tailwind CSS
- Backend: Python 3.11+ with FastAPI
- Database: PostgreSQL with pgvector extension
- Face Recognition: InsightFace/ArcFace (pretrained)
- Age Progression: External API or pretrained model
- AI Reports: OpenAI GPT-4 or Google Gemini
- Deployment: local development only

**MVP Timeline:** 8 weeks

---

## Core Workflow

1. User uploads missing child photo
2. System detects and aligns face
3. Generate 512-d face embedding (ArcFace)
4. Search PostgreSQL + pgvector for similar faces
5. Rank candidates by multiple factors
6. Generate age-progressed images (+5, +10, +15 years)
7. Generate AI investigation report
8. Display results in dashboard

---

## Critical Rules

### Safety & Ethics
- **NEVER** allow the system to declare definitive matches
- **ALWAYS** include disclaimers that results are suggestions only
- **ALWAYS** recommend DNA/biometric verification
- Age-progressed images labeled as "estimates"
- AI reports use tentative language only

### Security
- JWT-based authentication required
- bcrypt password hashing (cost factor 12)
- HTTPS in production
- File upload validation (JPG/PNG only, max 10MB)
- Rate limiting (100 req/min per IP)
- Audit logging for all searches

### Code Quality
- Backend: PEP 8, type hints, docstrings
- Frontend: TypeScript, functional components
- Testing: Minimum 80% code coverage
- Git: Feature branches, descriptive commits

### Performance Targets
- Face detection: < 2 seconds
- Vector search: < 5 seconds (10K database)
- Page load: < 3 seconds
- Support 20 concurrent users

### MVP Constraints
- Use pretrained models only (no training)
- Web only (no mobile apps)
- Focus on working prototype first

---

## Project Structure

```
missing-child-ai/
├── frontend/          # React + Tailwind
├── backend/
│   ├── api/
│   ├── face/
│   ├── matching/
│   ├── aging/
│   ├── reports/
│   ├── database/
│   └── core/
├── models/            # Pretrained models
├── data/              # Test data
├── tests/
└── README.md
```

---

## Development Phases

1. **Foundation (Weeks 1-2):** Setup, database, authentication
2. **Core Features (Weeks 3-5):** Face processing, search, UI
3. **Advanced Features (Weeks 6-7):** Age progression, AI reports
4. **Testing & Deployment (Week 8):** QA, optimization, launch

---

## Key Implementation Notes

### Multi-Factor Ranking
- Facial similarity: 70% weight
- Age compatibility: 15% weight
- Date/time compatibility: 10% weight
- Location proximity: 5% weight

### AI Report Prompt (Critical)
- System prompt MUST enforce tentative language
- NEVER allow "definitely", "confirmed", "proven"
- Always recommend DNA verification
- Temperature: 0.3 (factual, consistent)

---

## Success Criteria

The MVP is complete when:
- ✅ User can register, login, and create cases
- ✅ Face detection and embedding generation works
- ✅ Vector search returns Top-10 candidates
- ✅ Multi-factor ranking is implemented
- ✅ Age-progressed images are generated
- ✅ AI reports are factual and safe
- ✅ Dashboard displays all results clearly
- ✅ Performance targets are met
- ✅ No critical security vulnerabilities

---

## Guidance

**Start with:**
1. Set up project structure and local tooling
2. Create database schema and models
3. Build authentication system
4. Implement face detection pipeline
5. Build case creation and search
6. Create UI for results display
7. Add age progression and AI reports
8. Polish, test, and deploy

**When in doubt:**
- Prioritize working functionality
- Use pretrained models
- Keep UI simple and professional
- Test with realistic data

**Red flags to avoid:**
- Training custom ML models
- Features beyond scope
- Poor security practices
- AI reports that claim certainty
- Missing disclaimers

---

**Document Owner:** Development Team  
**Last Updated:** August 10, 2026
