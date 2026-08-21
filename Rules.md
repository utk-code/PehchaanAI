# Development Rules & Guidelines
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. Core Principles

### 1.1 Safety First
- **Never declare definitive matches** - System provides suggestions only
- All reports must include disclaimers
- Age-progressed images labeled as "estimates"
- No automated actions without human review

### 1.2 Privacy & Security
- Encrypt sensitive data at rest
- All communications over HTTPS
- Audit log all access to case data
- No data sharing outside system

### 1.3 Accuracy & Transparency
- Clearly display confidence scores
- Explain ranking factors
- Never hide limitations

---

## 2. Code Standards

### 2.1 Python (Backend)
**Style Guide:** PEP 8
- Use type hints for all functions
- Docstrings for all public functions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`

### 2.2 TypeScript (Frontend)
**Style Guide:** Airbnb + TypeScript
- Use interfaces for objects
- Functional components only
- Components: `PascalCase`
- Functions: `camelCase`

---

## 3. Testing Requirements

**Coverage Target:** 80% minimum

**Unit Tests:**
- pytest for backend
- Jest + React Testing Library for frontend

**Integration Tests:**
- Test API endpoints end-to-end
- Test database operations

---

## 4. Git Workflow

### 4.1 Branch Strategy
```
main              (production-ready)
  ├── develop     (integration branch)
      ├── feature/case-management
      ├── feature/face-detection
      └── bugfix/search-timeout
```

### 4.2 Commit Messages
```
feat: add age progression API integration
fix: resolve face detection timeout issue
docs: update API documentation
test: add unit tests for ranking algorithm
```

---

## 5. API Design Rules

### 5.1 REST Conventions
```
GET    /api/cases              # List cases
POST   /api/cases              # Create case
GET    /api/cases/{id}         # Get case details
PUT    /api/cases/{id}         # Update case
DELETE /api/cases/{id}         # Delete case
POST   /api/cases/{id}/search  # Trigger search
```

### 5.2 Response Format
**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Case created successfully"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "FACE_NOT_DETECTED",
    "message": "No face detected in image"
  }
}
```

### 5.3 Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

---

## 6. Security Rules

### 6.1 Authentication
- All endpoints except `/auth/login` and `/auth/register` require JWT
- Tokens expire after 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

### 6.2 File Upload Rules
- Allowed formats: JPG, PNG only
- Max size: 10MB
- Validate MIME type (not just extension)
- Store outside web root

---

## 7. Performance Rules

### 7.1 API Response Times
- Simple queries: < 1 second
- Face detection: < 2 seconds
- Vector search: < 5 seconds
- Report generation: < 10 seconds

### 7.2 Image Optimization
- Resize to max 1920px before storage
- Generate thumbnails (256px) for lists
- Use lazy loading in UI

---

## 8. Ethical Guidelines

### 8.1 AI Report Generation

**Always use:**
- "potential match", "suggests", "may indicate"
- Include confidence scores
- Recommend human verification

**Never use:**
- "This is definitely..."
- "We confirm..."
- "Proven match"

### 8.2 Age Progression
- Always include disclaimer: "Computer-generated estimate only"
- Never claim accuracy

### 8.3 Data Usage
- No training on case data without consent
- No sharing with third parties

---

## 9. MVP Constraints

### 9.1 Out of Scope
- ❌ Training custom models
- ❌ Mobile apps
- ❌ Real-time video processing
- ❌ Multi-language support

### 9.2 Must Haves
- ✅ Working face detection and matching
- ✅ Functional dashboard
- ✅ Secure authentication
- ✅ Database with vector search
- ✅ Basic age progression
- ✅ AI report generation

---

## 10. Code Review Checklist

**Before Submitting PR:**
- [ ] Code follows style guide
- [ ] Unit tests added/updated
- [ ] Tests pass locally
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] No console.log or debug prints

**Reviewer Checks:**
- [ ] Code is readable and maintainable
- [ ] Logic is correct
- [ ] Security best practices followed
- [ ] Tests are meaningful

---

## 11. AI Agent & Documentation Rules

### 11.1 Single Source of Truth
- **Phase Status:** Edit `Phases.md` only for phase completions and high-level milestones.
- **Task Tracking:** `TODO.md` is the active scratchpad. Keep tasks granular.
- **System Architecture:** `Architecture.md`, `API.md`, and `DatabaseSchema.md` are primary technical references. Avoid repeating schema/architecture details in planning docs.

### 11.2 Context & File Maintenance
- **`TODO.md` Update Cadence:** Update `TODO.md` (checking off completed items) and `PROGRESS.md` at the end of every completed major feature or at the start of a new "Day" phase. This ensures accurate tracking while minimizing constant file-write overhead.
- **`TODO.md` Budgeting:** Keep `TODO.md` under ~15 KB. Archive completed task blocks to `TODO_ARCHIVE.md` to prevent agent context bloat.
- **Selective Loading:** When invoking sub-agents, load only the specific files required for the sub-task (e.g. `Rules.md` + `Tools.md` + relevant domain doc).
- **No Desynchronization:** If an agent updates a feature specification, verify and update the corresponding entry in `API.md` or `DatabaseSchema.md` to maintain consistency.

---

**Document Owner:** Development Team  
**Last Updated:** August 10, 2026

