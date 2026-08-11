# Database Schema
## Missing Child Identification AI System

**Version:** 1.0  
**Database:** PostgreSQL 15+ with pgvector extension

---

## Core Tables

### 1. users
User accounts (investigators, admins)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'investigator')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 2. cases
Missing child cases with face embeddings

```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigator_id UUID NOT NULL REFERENCES users(id),
    child_name_encrypted TEXT,
    age_at_disappearance INTEGER NOT NULL CHECK (age_at_disappearance BETWEEN 0 AND 18),
    date_missing DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    notes TEXT,
    photo_path VARCHAR(500) NOT NULL,
    face_embedding VECTOR(512) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'archived')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_cases_investigator ON cases(investigator_id);
CREATE INDEX idx_cases_embedding ON cases USING ivfflat (face_embedding vector_cosine_ops) WITH (lists = 100);
```

---

### 3. candidates
Database of found individuals

```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_path VARCHAR(500) NOT NULL,
    face_embedding VECTOR(512) NOT NULL,
    current_age INTEGER CHECK (current_age BETWEEN 0 AND 100),
    date_found DATE,
    location_found VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_candidates_embedding ON candidates USING ivfflat (face_embedding vector_cosine_ops) WITH (lists = 100);
```

---

### 4. search_results
Search history with scores

```sql
CREATE TABLE search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(id),
    similarity_score FLOAT NOT NULL,
    age_score FLOAT NOT NULL,
    date_score FLOAT NOT NULL,
    location_score FLOAT NOT NULL,
    composite_score FLOAT NOT NULL,
    search_date TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_search_results_case ON search_results(case_id);
```

---

### 5. age_progressions
Generated age-progressed images

```sql
CREATE TABLE age_progressions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    target_age INTEGER NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 6. ai_reports
LLM-generated investigation reports

```sql
CREATE TABLE ai_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    report_text TEXT NOT NULL,
    model_used VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Vector Search Queries

### Find Similar Faces
```sql
SELECT 
    id,
    photo_path,
    1 - (face_embedding <=> $1::vector) AS similarity
FROM candidates
ORDER BY face_embedding <=> $1::vector
LIMIT 10;
```

### With Filters
```sql
SELECT 
    c.id,
    1 - (c.face_embedding <=> $1::vector) AS similarity
FROM candidates c
WHERE c.current_age BETWEEN $2 AND $3
  AND c.date_found >= $4
ORDER BY c.face_embedding <=> $1::vector
LIMIT 10;
```

---

## Relationships

```
users (1) ──── (many) cases
cases (1) ──── (many) search_results
cases (1) ──── (many) age_progressions
cases (1) ──── (many) ai_reports
candidates (1) ──── (many) search_results
```

---

**Document Owner:** Database Team  
**Last Updated:** August 10, 2026
