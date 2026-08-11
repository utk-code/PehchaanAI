# Agent Loop & Workflow
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. Agent Operational Loop

```
1. UNDERSTAND CONTEXT
   ↓
2. PLAN APPROACH
   ↓
3. IMPLEMENT
   ↓
4. TEST
   ↓
5. VERIFY
   ↓
6. DOCUMENT
   ↓
7. NEXT TASK (return to step 1)
```

---

## 2. Decision Tree

### Task Selection
```
Start work session
    ↓
Current task in progress?
    ├─ YES → Continue task
    └─ NO → Check project phase
        ├─ Phase 1 incomplete? → Pick Phase 1 task
        ├─ Phase 2 incomplete? → Pick Phase 2 task
        ├─ Phase 3 incomplete? → Pick Phase 3 task
        └─ Phase 4 incomplete? → Pick Phase 4 task
```

### Implementation Approach
```
Receive task
    ↓
Similar code exists?
    ├─ YES → Match existing patterns
    └─ NO → Follow best practices
        ↓
High-risk task?
    ├─ YES → Extra validation
    └─ NO → Proceed
        ↓
Break into smaller steps?
    ├─ YES → Implement incrementally
    └─ NO → Implement as single unit
```

---

## 3. Code Generation Patterns

### Backend (FastAPI)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.post("/", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new case."""
    # Implementation
    pass
```

### Frontend (React)
```typescript
import React from 'react';
import { useQuery } from '@tanstack/react-query';

export const CaseList: React.FC = () => {
  const { data, isLoading } = useQuery(['cases'], fetchCases);
  
  if (isLoading) return <LoadingSpinner />;
  
  return <div>{/* Component JSX */}</div>;
};
```

---

## 4. Quality Gates

**Before Committing:**
- [ ] Code follows style guide
- [ ] Type hints/interfaces present
- [ ] Unit tests written and passing
- [ ] No hardcoded secrets
- [ ] Error handling implemented
- [ ] Meets acceptance criteria

**Before Moving to Next Phase:**
- [ ] All phase tasks complete
- [ ] Integration tests passing
- [ ] Performance targets met
- [ ] Documentation updated

---

## 5. Error Recovery

### When Tests Fail
1. Read error message carefully
2. Identify root cause
3. Check typos, imports, dependencies
4. Add debug logging if needed
5. Fix and re-test
6. If stuck after 3 attempts, try different approach

---

## 6. Progress Communication

**Updates:**
```
"Completed: [Task name]
• Implemented [feature]
• Tests passing: [X/Y]
• Performance: [metric]

Next: [Next task]"
```

**Blockers:**
```
"Blocker: [Issue]
• Attempted: [Solutions]
• Root cause: [Analysis]
• Proposed solution: [Approach]"
```

---

**Document Owner:** AI Agent Team  
**Last Updated:** August 10, 2026
