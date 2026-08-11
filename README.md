# Missing Child Identification AI System (Project Ace)

A web-based AI system to help investigators find potential matches for missing children using facial recognition, age progression, and AI-powered analysis.

**Version:** 1.0.0 (MVP)
**Status:** Planning Phase
**Target Launch:** End of Week 8

---

## 🎯 Project Overview

This system enables investigators to:
1. Upload a missing child's photo
2. Search a database for visually similar faces
3. View age-progressed and enhanced images
4. Review AI-generated investigation reports
5. Export and share results with secure audit trails

Important: system outputs are investigative leads only. All matches require human review and formal verification (DNA or other biometrics).

---

## 🛠️ Tech Stack

Frontend: React 18+ (TypeScript), Tailwind CSS, React Router, TanStack Query

Backend: Python 3.11+ (FastAPI), PostgreSQL 15+ (pgvector), SQLAlchemy, InsightFace, OpenCV, OpenAI GPT-4

Infrastructure: Docker Compose, Nginx, JWT auth, optional Kubernetes deployment

---

## 📁 Project Structure (high level)

```
missing-child-ai/
├── frontend/         # React + TypeScript
├── backend/          # FastAPI backend
├── models/           # Pretrained model artifacts
├── data/             # Sample/test images and datasets
├── tests/            # Unit & integration tests
├── docs/             # Design docs, PRD, ADRs
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start (local without Docker)

1. Install Python 3.11+ and Node.js 18+.
2. Backend:
   - python -m venv .venv
   - .venv\Scripts\Activate.ps1  # PowerShell
   - pip install -r backend/requirements.txt
   - cp backend/.env.example backend/.env
3. Frontend:
   - cd frontend
   - npm install
   - npm run dev
4. Run backend locally:
   - uvicorn backend.main:app --reload --port 8000

Access frontend at http://localhost:3000 and API docs at http://localhost:8000/docs

Docker (recommended for parity): docker-compose up -d

---

## 🧪 Running Tests

Backend (local):

python -m pytest tests/ -v --maxfail=1

Frontend:

cd frontend && npm test -- --watchAll=false

CI: workflows run pytest and frontend tests inside containers (see .github/workflows)

---

## 📦 Releases & Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH). Use changelogs and release notes in the releases page.

---

## 🤝 Contributing

Contributions are welcome. Please follow these steps:

1. Open an issue describing the change or feature.
2. Create a branch: feature/short-description or fix/short-description
3. Add tests for new behavior.
4. Open a pull request against main with a clear description and testing notes.

Before merging: ensure CI passes, include changelog entry if applicable, and get at least one approving review from the core team.

Code style: use Black (Python) and Prettier (JS/TS). Run linters before committing.

---

## 📝 Code of Conduct

Be respectful and professional. Report violations to the maintainers.

---

## ⚖️ License

This repository is released under the MIT License. See LICENSE.md for details.

---

## 🔐 Security & Privacy

- Treat all uploaded images as sensitive data.
- Store only the minimum required PII and use encryption at rest and in transit.
- Log access and changes with an audit trail.
- Provide opt-out/deletion procedures for data subjects where required by law.

---

## 🛠️ Operational Notes

- Default local ports: frontend 3000, backend 8000
- Add service health checks and readiness probes in deployment manifests
- Backups and data retention policies are mandatory for production

---

## 📞 Contact & Maintainers

Project Manager: [Name/Email]
Tech Lead: [Name/Email]
Security Contact: security@example.org

---

## 🙏 Acknowledgments

Thanks to InsightFace, OpenAI, pgvector contributors, and research partners.

---

**Last Updated:** August 11, 2026
**Document Owner:** Development Team
