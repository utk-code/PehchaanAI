# Missing Child Identification AI System

A web-based AI system that helps law enforcement investigators find potential matches for missing children across large age gaps using facial recognition, age progression, and AI-powered analysis.

**Version:** 1.0.0 (MVP)  
**Status:** Planning Phase  
**Target Launch:** End of Week 8

---

## 🎯 Project Overview

This system enables investigators to:
1. Upload a missing child's photo
2. Search a database for visually similar faces
3. View age-progressed images
4. Review AI-generated investigation reports
5. Export results for further investigation

**⚠️ Important:** This system provides suggestions only. All matches require verification through DNA testing or other biometric methods.

---

## 🛠️ Tech Stack

**Frontend:**
- React 18+ with TypeScript
- Tailwind CSS
- React Router
- React Query (TanStack Query)
- Zustand (state management)

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL 15+ with pgvector extension
- SQLAlchemy ORM
- InsightFace (ArcFace face recognition)
- OpenCV (face detection)
- OpenAI GPT-4 (report generation)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- JWT authentication

---

## 📁 Project Structure

```
missing-child-ai/
├── frontend/              # React + TypeScript frontend
├── backend/               # FastAPI backend
├── models/                # Pretrained models
├── data/                  # Test data
├── tests/                 # Tests
├── docs/                  # Planning documents
├── docker-compose.yml
└── README.md
```

---

## 📚 Documentation

All planning documents are in the root directory:

- **PRD.md** - Product Requirements Document
- **Architecture.md** - System architecture
- **Rules.md** - Development rules and standards
- **Design.md** - UI/UX design specifications
- **Phases.md** - Development phases
- **API.md** - API documentation
- **DatabaseSchema.md** - Database schema
- **Evaluation.md** - Testing plan
- **Experiments.md** - Research findings
- **ADR.md** - Architecture Decision Records
- And more...

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Git
- OpenAI API key

### Setup

```bash
# Clone repository
git clone <repository-url>
cd missing-child-ai

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Add your API keys to backend/.env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🧪 Running Tests

```bash
# Backend tests
docker-compose exec backend pytest tests/ -v --cov

# Frontend tests
docker-compose exec frontend npm test -- --coverage
```

---

## 📊 Performance Targets

- Face detection: < 2 seconds
- Vector search: < 5 seconds (10K database)
- Page load: < 3 seconds
- Concurrent users: 20 simultaneous
- Face detection accuracy: > 95%

---

## 🔐 Security

- JWT-based authentication (8-hour expiration)
- bcrypt password hashing (cost factor 12)
- HTTPS in production
- File upload validation
- Rate limiting (100 req/min per IP)
- Audit logging

---

## 🔑 Key Features

### ✅ MVP Features
- User authentication
- Case management
- Photo upload with face detection
- Vector similarity search
- Multi-factor ranking
- Age progression images
- AI-generated reports
- Results dashboard
- PDF export

### 🚧 Post-MVP Features
- Mobile app
- Advanced photo enhancement
- External database integration
- Collaborative case sharing
- Advanced analytics

---

## 📈 Development Phases

1. **Phase 1 (Weeks 1-2):** Foundation
2. **Phase 2 (Weeks 3-5):** Core Features
3. **Phase 3 (Weeks 6-7):** Advanced Features
4. **Phase 4 (Week 8):** Testing & Deployment

---

## ⚠️ Ethical Guidelines

This system is designed to **assist** investigators, not replace them:

- Never declare definitive matches
- Always recommend DNA verification
- Include disclaimers on all results
- Respect privacy and data protection
- Maintain audit trails
- Handle sensitive data securely

---

## 📞 Contact

**Project Manager:** [Name/Email]  
**Tech Lead:** [Name/Email]  
**Support:** [Email]

---

## 🙏 Acknowledgments

- InsightFace team for ArcFace model
- OpenAI for GPT-4
- pgvector contributors
- All law enforcement agencies supporting this initiative

---

**Last Updated:** August 10, 2026  
**Document Owner:** Development Team
