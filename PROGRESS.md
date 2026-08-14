# Progress

## 2026-08-12 - Day 2: Authentication & Basic Backend

Completed:
- Initialized FastAPI backend in `backend/`.
- Added SQLAlchemy database session wiring and a `users` table model.
- Implemented JWT auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /auth/me`
- Added Argon2 password hashing via `pwdlib`.
- Added isolated auth API tests using SQLite overrides.
- Initialized Vite React TypeScript frontend in `frontend/`.
- Updated Docker Compose to use PostgreSQL with pgvector.
- Fixed backend and frontend Dockerfiles for service-local build contexts.

Verified:
- `python -m pytest tests -v`
- `python -m black --check backend tests`
- `python -m flake8 backend tests`
- `npm run build`
- `npm audit`
- `docker compose config`
- `docker compose build --progress plain`

Next:
- Day 3: Case model, face detection pipeline, photo upload endpoint, and embedding generation.
