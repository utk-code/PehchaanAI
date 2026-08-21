# Memory & Context Management
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. Overview

This document describes how the system manages memory, state, and context.

---

## 2. Application State Management

### 2.1 Frontend State (React)

**Global State (Zustand):**
```typescript
interface AppState {
  user: User | null;
  currentCase: Case | null;
  searchResults: SearchResult[];
  setUser: (user: User | null) => void;
  setCurrentCase: (case: Case) => void;
}
```

**Server State (React Query):**
- Cases list, candidate details, search history
- Cache duration: 5 minutes
- Stale-while-revalidate strategy

### 2.2 Backend State

**Stateless Design:**
- No server-side session storage
- All state in JWT tokens and database
- Request-scoped dependency injection

---

## 3. Caching Strategy

### 3.1 Frontend Caching

**React Query Cache:**
- Stale time: 5 minutes
- Cache time: 10 minutes
- No refetch on window focus

**Browser Storage:**
- localStorage: JWT token, user preferences
- sessionStorage: Temporary form data

### 3.2 Backend Caching (Future)

**Redis Cache (Post-MVP):**
- Cache embeddings: 1 hour TTL
- Cache search results: 5 minutes TTL

---

## 4. Session Management

**JWT Token Structure:**
```json
{
  "sub": "user_id",
  "username": "investigator",
  "role": "investigator",
  "exp": 1691683200
}
```

**Lifecycle:**
- Issued on login
- Expires after 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Stored by the client and sent as an Authorization: Bearer header

---

## 5. Data Retention

**Active Cases:** Retained indefinitely
**Closed Cases:** Retained for 7 years
**Archived Cases:** Compressed after 7 years
**Deleted Cases:** Soft delete, permanent after 30 days

**Temporary Data:**
- Uploaded images: Deleted after processing (< 5 min)
- Age-progressed images: Cached for 24 hours
- Search results: Retained for 90 days

---

## 6. Memory Optimization

### 6.1 Image Processing

```python
def process_image(image_path: str):
    img = cv2.imread(image_path)
    # Resize to max 1920px
    if max(img.shape) > 1920:
        scale = 1920 / max(img.shape)
        img = cv2.resize(img, None, fx=scale, fy=scale)
    # Process...
    del img  # Free memory
```

**Limits:**
- Max image size: 10MB
- Max resolution: 4096x4096
- Process 1 image at a time

### 6.2 Vector Search

```sql
CREATE INDEX idx_candidates_embedding 
ON candidates 
USING ivfflat (face_embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## 7. Database Concurrency

**Connection Pooling:**
- Pool size: 10
- Max overflow: 20
- Pre-ping enabled

**Transaction Isolation:**
- Default: READ COMMITTED
- Optimistic locking (future)

---

## 8. LLM Context Management

**Token Budget:**
- System prompt: ~500 tokens
- Case data: ~200 tokens
- Top-5 candidates: ~800 tokens
- Output limit: 1000 tokens
- Total cost per report: ~$0.02 (GPT-4)

**Context Pruning:**
- Include only Top-5 candidates
- Essential metadata only
- Remove verbose descriptions

---

**Document Owner:** Engineering Team  
**Last Updated:** August 10, 2026
