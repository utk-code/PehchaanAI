# API Documentation
## Missing Child Identification AI System

**Version:** 1.0  
**Base URL:** `https://api.missingchild.example.com`

---

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

**Authorization Header:**
```
Authorization: Bearer <jwt_token>
```

**Token Expiration:** 8 hours

---

## Endpoints

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request:**
```json
{
  "username": "investigator_jones",
  "email": "jones@agency.gov",
  "password": "SecurePassword123!",
  "role": "investigator"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "investigator_jones",
    "email": "jones@agency.gov",
    "role": "investigator"
  }
}
```

---

#### POST /api/auth/login
Authenticate and receive JWT token.

**Request:**
```json
{
  "username": "investigator_jones",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 28800
  }
}
```

---

### Cases

#### POST /api/cases
Create a new missing child case.

**Headers:** `Authorization: Bearer <token>`

**Request (multipart/form-data):**
- `photo`: File (JPG/PNG, max 10MB)
- `age_at_disappearance`: Integer
- `date_missing`: Date (YYYY-MM-DD)
- `location`: String
- `notes`: String (optional)

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "age_at_disappearance": 8,
    "date_missing": "2020-03-15",
    "location": "Chicago, IL",
    "face_detected": true,
    "status": "active"
  }
}
```

**Error (400):**
```json
{
  "success": false,
  "error": {
    "code": "FACE_NOT_DETECTED",
    "message": "No face detected in uploaded image"
  }
}
```

---

#### GET /api/cases
List all cases for authenticated user.

**Query Parameters:**
- `status` (optional): "active", "closed", "archived"
- `limit` (optional, default: 20)
- `offset` (optional, default: 0)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "cases": [...],
    "total": 15,
    "limit": 20,
    "offset": 0
  }
}
```

---

#### GET /api/cases/{id}
Get detailed case information including search results.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "case": {...},
    "candidates": [...],
    "age_progressions": [...],
    "report": {...}
  }
}
```

---

#### POST /api/cases/{id}/search
Trigger similarity search for a case.

**Request (optional filters):**
```json
{
  "age_range": [12, 18],
  "limit": 10
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "candidates": [
      {
        "id": "uuid",
        "similarity_score": 87.5,
        "composite_score": 88.2,
        "photo_path": "/uploads/candidates/uuid.jpg"
      }
    ]
  }
}
```

---

### Reports

#### POST /api/cases/{id}/report
Generate AI investigation report.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "text": "# Investigation Report\n\n...",
    "model_used": "gpt-4"
  }
}
```

---

### Export

#### GET /api/cases/{id}/export/pdf
Export case results as PDF.

**Response:** PDF file download

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Invalid token |
| `FORBIDDEN` | 403 | No permission |
| `NOT_FOUND` | 404 | Resource not found |
| `FACE_NOT_DETECTED` | 400 | No face in image |
| `FILE_TOO_LARGE` | 400 | File > 10MB |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

**100 requests per minute** per IP address

---

**Document Owner:** API Team  
**Last Updated:** August 10, 2026
