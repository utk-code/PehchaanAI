# Context Management Guide
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. Context Prioritization

### Essential Context (Always Load)
1. Current task and acceptance criteria
2. Related code files
3. Dependencies (external libraries, APIs)
4. Error messages (if debugging)

### Important Context (Load When Relevant)
1. Architecture.md (for structural decisions)
2. Rules.md (when writing new code)
3. Database schema (for data models)
4. Test files (when testing)

### Reference Context (Load As Needed)
1. PRD.md (clarifying requirements)
2. Design.md (building UI)
3. Phases.md (planning next steps)

### Avoid Loading
- Generated files (node_modules, __pycache__)
- Binary files (images, models)
- Unrelated modules
- Deprecated code

---

## 2. Context Window Management

### Typical Budget
- System Prompt: ~2000 tokens
- Task Description: ~500 tokens
- Code Files (3-5 files): ~10000 tokens
- Working Memory: ~2000 tokens
- Output: ~2000 tokens
- Buffer: ~3500 tokens

### When Context is Full
1. Commit code
2. Update PROGRESS.md
3. Start fresh with current task only
4. Reference committed code

---

## 3. File Reading Strategy

### Starting New Task
```
Read (in order):
1. Task description from Planner.md
2. Acceptance criteria
3. Related existing code (2-3 key files)
4. Relevant Architecture.md section
```

### Implementing Backend
```
Read:
1. Similar endpoint (for patterns)
2. Database models
3. Request/response schemas
4. Auth dependencies (if protected)
```

### Implementing Frontend
```
Read:
1. Similar component (for patterns)
2. API service functions
3. Type definitions
4. Shared UI components
```

---

## 4. Documentation Strategy

### Inline Documentation
```python
def search_similar_faces(embedding: np.ndarray, limit: int = 10):
    """
    Search for faces similar to the given embedding.
    
    Uses cosine similarity with IVFFlat index.
    
    Args:
        embedding: 512-d face embedding
        limit: Max results to return
        
    Returns:
        List of Candidate objects with scores
        
    Performance: ~2-5 seconds for 10K database
    """
    # Implementation
```

---

## 5. State Tracking

### PROGRESS.md Template
```markdown
# Progress Tracker

## Current Phase: Phase 2
## Current Task: Week 4, Day 2

## Completed
- [x] Phase 1: Foundation
- [x] Week 3: Face Detection

## In Progress
- [ ] Week 4 Day 2: Candidate Model
  - [x] Create model
  - [ ] Populate database

## Next Up
- [ ] Week 4 Day 3: Vector Search

## Blockers
None

## Notes
- Using ArcFace 512-d embeddings
- Need 100+ test candidates
```

---

## 6. Context Refresh Triggers

### When to Start Fresh
1. Phase change (Phase 1 → Phase 2)
2. Major task change (Frontend → Backend)
3. Context window 80% full
4. After debugging complete
5. Starting new session

### How to Refresh
1. Commit all current work
2. Update PROGRESS.md
3. Clear conversation/context
4. Load fresh context for new task

---

## 7. Context-Saving Techniques

### Use Code References
Instead of including full files:
```
"Reference: backend/database/models.py - User model"
```

### Use Summaries
Instead of full file content:
```
"CaseForm component:
- Uses React Hook Form
- Uploads via FileUpload component
- Calls POST /api/cases
- Redirects on success"
```

---

## 8. Multi-File Strategy

### Sequential Approach
1. Read and modify File A
2. Commit File A
3. Read and modify File B
4. Commit File B

### Batch Approach (for small changes)
1. Read Files A, B, C together
2. Implement all changes
3. Test together
4. Commit all

**Use Sequential for:** Large changes, complex logic
**Use Batch for:** Small changes, tightly coupled files

---

**Document Owner:** Development Team  
**Last Updated:** August 10, 2026
