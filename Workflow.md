# Workflow Documentation
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. User Workflows

### 1.1 Investigator Registration & Login
1. Navigate to application URL
2. Click "Register" or "Login"
3. Enter credentials
4. Submit form
5. Redirect to dashboard

**Time:** < 2 minutes

---

### 1.2 Create Missing Child Case
1. Click "Create New Case"
2. Fill out form (name, age, date, location, notes)
3. Upload child's photo (drag & drop)
4. System validates photo and detects face
5. Preview detected face
6. Click "Create Case & Search"
7. System processes and searches database
8. Redirect to results dashboard

**Time:** 5-10 minutes

---

### 1.3 Review Search Results
1. View dashboard with:
   - Original photo
   - Age-progressed images
   - Top-10 candidates
   - Similarity scores
   - AI investigation report

2. Review each candidate
3. Read AI report
4. Export results as PDF

**Time:** 10-30 minutes

---

## 2. System Workflows

### 2.1 Photo Upload & Face Processing
```
Upload → Validation → Face Detection → Alignment
    → Quality Check → Embedding Generation → Return
```

**Performance:** < 2 seconds

---

### 2.2 Vector Similarity Search
```
Receive embedding → Query pgvector → Calculate scores
    → Rank by composite score → Store results → Return
```

**Performance:** < 5 seconds

---

### 2.3 Age Progression
```
For each target age (+5, +10, +15):
    Call API → Generate image → Save → Store path
```

**Performance:** < 10 seconds total

---

### 2.4 AI Report Generation
```
Prepare context → Call LLM API → Validate report
    → Store → Return
```

**Performance:** < 10 seconds

---

## 3. Data Workflows

### Case Data Flow
```
Create Case → Generate Embedding → Search
    → Store Results → Generate Age Progressions
    → Generate Report → Display Dashboard
```

### Data Retention
```
Created (active) → Resolved (closed) → 7 years (archived)
    → Deletion requested (soft delete) → 30 days (permanent)
```

---

## 4. Error Handling

### Face Detection Failure
```
No face detected → Log error → Return HTTP 400
    → Display user-friendly message → User retries
```

### Search Timeout
```
Timeout → Cancel query → Log → Return HTTP 504
    → User retries → Admin investigates
```

### External API Failure
```
API error → Retry once → If fails: continue without
    → Display notice → Log for later retry
```

---

## 5. Development Workflow

### Feature Development
1. Pick task from Planner.md
2. Read documentation
3. Review similar code
4. Implement
5. Write tests
6. Manual testing
7. Document
8. Commit
9. Mark complete

### Bug Fix
1. Reproduce bug
2. Write failing test
3. Debug root cause
4. Implement fix
5. Verify test passes
6. Commit

---

## 6. Deployment Workflow

### Dev to Production
```
Development → Feature Branch → Develop Branch
    → Staging → Testing → Production → Monitor
```

### Rollback
```
Issue detected → Assess severity → Rollback if critical
    → Investigate → Fix → Re-deploy
```

---

## 7. Monitoring

### Health Checks
```
Every 1 minute: Check API, database, disk space
    → If fails: Alert admin → Auto-recovery attempt
```

### Performance Monitoring
```
Track: Response times, query times, search latency, errors
    → If exceeds threshold: Alert → Investigate
```

---

## 8. Backup & Recovery

### Automated Backups
```
Daily: Backup database and images → Verify integrity
    → Retain 30 days → Weekly retained 1 year
```

### Disaster Recovery
```
Failure → Assess → Stop services → Restore from backup
    → Verify → Restart → Test → Resume operations
```

---

**Document Owner:** Operations Team  
**Last Updated:** August 10, 2026
