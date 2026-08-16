# Architecture Decision Records (ADR)
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## ADR-001: Use PostgreSQL with pgvector

**Date:** 2026-08-01  
**Status:** Accepted

**Decision:** Use PostgreSQL with pgvector extension for vector storage.

**Rationale:**
- Single database for all data (simpler architecture)
- Performance acceptable for MVP scale (< 100K candidates)
- Team familiar with PostgreSQL
- Easy migration to dedicated vector DB if needed

**Consequences:**
- May need to migrate to Milvus/Qdrant for large-scale deployment
- Limited advanced vector search features

---

## ADR-002: Use Pretrained ArcFace Model

**Date:** 2026-08-02  
**Status:** Accepted

**Decision:** Use pretrained ArcFace (InsightFace) without fine-tuning.

**Rationale:**
- 98%+ accuracy on benchmarks
- No training infrastructure needed
- MVP timeline doesn't allow training
- Ready to use immediately

**Consequences:**
- Cannot customize embedding dimensions
- Dependent on external model updates

---

## ADR-003: React + FastAPI Stack

**Date:** 2026-08-03  
**Status:** Accepted

**Decision:** React (TypeScript) frontend, FastAPI (Python) backend.

**Rationale:**
- React: Mature ecosystem, TypeScript for safety
- FastAPI: Fast development, Python for ML integrations
- Monorepo for easier development

**Consequences:**
- Need to manage two build processes

---

## ADR-004: JWT Authentication

**Date:** 2026-08-04  
**Status:** Accepted

**Decision:** Use JWT tokens for authentication.

**Rationale:**
- Stateless (no server-side sessions)
- Scalable across multiple servers
- Standard approach for modern APIs

**Consequences:**
- Tokens cannot be revoked before expiration

---

## ADR-005: External API for Age Progression

**Date:** 2026-08-05  
**Status:** Accepted

**Decision:** Use external commercial API for age progression.

**Rationale:**
- No GPU infrastructure required
- Pay-per-use cost model
- Immediate availability

**Consequences:**
- Dependency on external service
- Ongoing API costs

---

## ADR-006: OpenAI GPT-4 for Reports

**Date:** 2026-08-06  
**Status:** Accepted

**Decision:** Use GPT-4 with strict safety prompts.

**Rationale:**
- Best language quality
- 100% adherence to safety constraints
- Cost acceptable ($0.025 per report)

**Consequences:**
- Dependency on OpenAI API
- Ongoing costs

---

## ADR-007: Local Development Setup

**Date:** 2026-08-07  
**Status:** Superseded

**Decision:** Use native local development tooling only.

**Rationale:**
- Local development is simpler and faster without container orchestration
- The backend and frontend boot cleanly as standalone apps
- The project no longer needs a container runtime for onboarding

**Consequences:**
- Setup relies on native Python and Node tooling
- Deployment packaging is out of scope for this repo

---

## ADR-008: Tailwind CSS

**Date:** 2026-08-08  
**Status:** Accepted

**Decision:** Use Tailwind CSS for styling.

**Rationale:**
- Fast development
- Consistent design system
- Small bundle size

**Consequences:**
- Learning curve for unfamiliar team members

---

## ADR-009: Soft Delete for Cases

**Date:** 2026-08-09  
**Status:** Accepted

**Decision:** Soft delete with permanent deletion after 30 days.

**Rationale:**
- Allows data recovery
- Maintains audit trail
- Complies with data retention

**Consequences:**
- Need cleanup job for old records

---

## ADR-010: No Mobile App for MVP

**Date:** 2026-08-10  
**Status:** Accepted

**Decision:** Web-only with responsive design.

**Rationale:**
- MVP timeline doesn't allow mobile development
- Web works on mobile browsers
- Most work done on desktops

**Consequences:**
- Limited mobile experience
- Can add native app post-MVP

---

**Document Owner:** Architecture Team  
**Last Updated:** August 10, 2026
