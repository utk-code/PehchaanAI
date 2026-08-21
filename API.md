# API Documentation
## PehchaanAI — Missing Child Identification AI System

**Version:** 0.1.0
**Base URL (backend):** `http://127.0.0.1:8000`

The React frontend calls the same routes through a relative `/api` prefix that
the Vite dev server rewrites (`/api/auth/login` → `/auth/login`). Set
`VITE_API_BASE_URL` to override.

---

## Authentication

All endpoints except `POST /auth/register`, `POST /auth/login`, and `GET /health`
require a JWT bearer token.

```
Authorization: Bearer <jwt_token>
```

**Token expiration:** 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

---

## Endpoints

### System

#### GET /health
Liveness check.

**Response (200):**
```json
{ "status": "ok" }
```

---

### Authentication

#### POST /auth/register
Register a new user account.

**Request body:**
```json
{
  "email": "jones@agency.gov",
  "password": "SecurePassword123!",
  "full_name": "Investigator Jones"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:** `409` email already registered, `422` validation.

---

#### POST /auth/login
Authenticate and receive a JWT token. Uses OAuth2 password form encoding.

**Request (form-urlencoded):** `username`, `password`

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

#### GET /auth/me
Fetch the current user's profile.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "jones@agency.gov",
  "full_name": "Investigator Jones",
  "is_active": true
}
```

---

### Case Photo Processing

#### POST /cases/photo/embedding
Upload a photo and return its 512-d ArcFace embedding. Does **not** store a
case; useful for previews/testing.

**Request (multipart/form-data):** `file` (JPG/PNG, max 10 MB)

**Response (200):**
```json
{
  "embedding": [0.001, 0.02, "... 512 numbers"],
  "det_score": 0.98,
  "bbox": [56.1, 72.3, 91.7, 118.4],
  "quality_pass": true,
  "num_faces": 1
}
```

**Errors:**
- `400` no face found (`NoFaceFoundError`)
- `400` face quality check failed (`LowQualityFaceError`)
- `400` face processing failed (`FaceDetectionError`)
- `415` file is not an image

---

#### POST /cases/photo/upload
Upload a photo, process it, and **optionally** create a case.

**Request (multipart/form-data):** `file`
**Query parameters:**
- `create_case`: `true|false` — when true, `query_name` is required and a Case is created
- `query_name`: string (required if `create_case=true`)
- `query_age`: integer 0-100 (optional)
- `query_date`: date `YYYY-MM-DD` (optional)
- `query_location`: string (optional)
- `notes`: string (optional)

**Response (200):** same as `/cases/photo/embedding` plus:
```json
{
  "case_id": "uuid"   // present when create_case=true
}
```

---

### Cases

#### POST /cases
Create a case with a pre-computed face embedding (see
`/cases/photo/embedding` first).

**Request body (CaseCreate):**
```json
{
  "query_name": "Aarav - 2020",
  "query_age": 8,
  "query_date": "2020-03-15",
  "query_location": "Delhi",
  "notes": "Last seen near school",
  "face_embedding": ["512 numbers"],
  "photo_path": "uploads/<uuid>.jpg"
}
```

**Response (201):** full case object:
```json
{
  "id": "uuid",
  "investigator_id": "uuid",
  "query_name": "Aarav - 2020",
  "query_age": 8,
  "query_date": "2020-03-15T00:00:00Z",
  "query_location": "Delhi",
  "notes": "Last seen near school",
  "photo_path": "http://127.0.0.1:8000/uploads/<uuid>.jpg",
  "face_embedding": ["512 numbers"],
  "status": "active",
  "created_at": "2026-08-16T10:00:00Z",
  "updated_at": "2026-08-16T10:00:00Z",
  "deleted_at": null
}
```

---

#### GET /cases
List cases for the authenticated user (newest first).

**Query parameters:**
- `status_filter` (optional): `active` | `archived`
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

**Response (200):**
```json
[
  {
    "id": "uuid",
    "query_name": "Aarav - 2020",
    "query_age": 8,
    "query_date": "2020-03-15T00:00:00Z",
    "status": "active",
    "created_at": "2026-08-16T10:00:00Z"
  }
]
```

---

#### GET /cases/{case_id}
Get a single case (author-only). Returns the full `CaseRead` object, with
`photo_path` rewritten to an absolute URL.

**Errors:** `404` not found / `403` not your case.

---

#### PATCH /cases/{case_id}
Update a case. Any subset of fields is accepted.

**Request body (CaseUpdate):**
```json
{
  "query_name": "Aarav - updated",
  "query_age": 9,
  "query_location": "Mumbai",
  "status": "active"
}
```

**Response (200):** full case object.

---

#### DELETE /cases/{case_id}
Soft-delete a case (sets `deleted_at` and `status=archived`).

**Response:** `204 No Content`.

---

### Search

#### POST /search
Search the corpus with a 512-d face embedding.

**Request body (SearchRequest):**
```json
{
  "face_embedding": ["512 numbers"],
  "top_k": 20,
  "min_similarity": 0.3
}
```

**Response (200):**
```json
{
  "query_id": null,
  "total_records": 609,
  "quality_warning": null,
  "results": [
    {
      "record_id": "uuid",
      "person_id": "001",
      "age": 7,
      "capture_year": 1996,
      "dataset": "FGNET",
      "photo_path": "http://127.0.0.1:8000/ref-images/images/001A02.JPG",
      "face_similarity": 0.87
    }
  ]
}
```

---

#### GET /search/case/{case_id}
Search using an existing case's stored embedding (author-only).

**Query parameters:** `top_k` (default 20), `min_similarity` (default 0.3)

**Response (200):** same `SearchResponse` as `POST /search`, with `query_id`
set to the case id.

---

#### POST /search/photo
Upload a photo, extract its embedding, and search in one call. Uses the
**soft** quality pipeline: a detected-but-low-quality face still runs the
search and returns a `quality_warning` instead of a 400. A photo with no face
(or an undecodable image) is rejected with `400`.

**Request (multipart/form-data):** `file`; `top_k` and `min_similarity` are
**query parameters** (e.g. `POST /search/photo?top_k=20&min_similarity=0.3`).

**Response (200):**
```json
{
  "query_id": null,
  "total_records": 609,
  "quality_warning": "face too small (33x39px)",
  "results": [ "... ranked candidates ..." ]
}
```

---

### Reports

#### GET /reports/{case_id}
Deterministically generate a rule-based investigation report for a case
(author-only). No LLM or API key required — the report runs the case's live
search and bucket candidates by similarity (high ≥ 0.6, medium 0.4-0.6, low
0.3-0.4).

**Response (200):**
```json
{
  "case_id": "uuid",
  "query_name": "Aarav - 2020",
  "query_age": 8,
  "query_location": "Delhi",
  "query_date": "2020-03-15T00:00:00Z",
  "generated_at": "2026-08-16T10:00:00Z",
  "total_records": 609,
  "total_candidates": 20,
  "top_match_similarity": 1.0,
  "high_confidence": 1,
  "medium_confidence": 13,
  "low_confidence": 6,
  "summary": "text summary",
  "findings": ["..."],
  "candidates": [
    {
      "rank": 1,
      "record_id": "uuid",
      "person_id": "001",
      "age": 7,
      "dataset": "FGNET",
      "face_similarity": 1.0,
      "photo_path": "http://127.0.0.1:8000/ref-images/images/001A02.JPG"
    }
  ],
  "recommendations": ["..."],
  "next_steps": ["..."]
}
```

**Errors:** `404` case not found (or foreign case).

---

## Error Codes

Errors are JSON with FastAPI's standard shape:
```json
{ "detail": "No face detected above confidence threshold" }
```

| Status | Meaning |
|--------|---------|
| 400 | Bad input: no face, low-quality face, invalid embedding length |
| 401 | Missing/invalid token |
| 403 | Not the case owner |
| 404 | Case/report not found |
| 409 | Email already registered |
| 415 | Uploaded file is not an image |
| 422 | Validation error (request body/form) |

---

## Interactive Docs

FastAPI auto-generates OpenAPI docs at:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`

---

**Document Owner:** Development Team
**Last Updated:** August 16, 2026