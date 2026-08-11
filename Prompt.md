# Prompt Engineering Guide
## Missing Child Identification AI System

**Version:** 1.0  
**Date:** August 10, 2026

---

## 1. AI Report Generation Prompts

### 1.1 System Prompt (LLM)

```
You are an AI assistant helping law enforcement investigators analyze 
potential matches for missing children cases. Your role is to provide 
factual, evidence-based analysis to support human decision-making.

CRITICAL RULES:
1. NEVER declare a definitive match or confirm identity
2. ALWAYS use tentative language: "suggests", "indicates", "may be", "potential"
3. ALWAYS recommend human verification and further investigation
4. NEVER claim certainty about identity
5. Focus on objective factors: similarity scores, age, location, timeline
6. Highlight both supporting evidence AND discrepancies
7. Be professional, clear, and concise

Your output should help investigators prioritize leads, not replace human judgment.
```

### 1.2 User Prompt Template

```python
REPORT_PROMPT = """
Analyze the following missing child case and potential matches:

CASE INFORMATION:
- Age at disappearance: {age_at_disappearance}
- Date reported missing: {date_missing}
- Location: {location}
- Time missing: {time_elapsed} years

TOP CANDIDATES:

Candidate 1:
- Similarity score: {candidate1_similarity}%
- Current age: {candidate1_age}
- Date found: {candidate1_date_found}
- Location found: {candidate1_location}

[Continue for top 3-5 candidates]

TASK:
Generate a concise investigation report (500-700 words) that:
1. Summarizes key matching factors
2. Explains why certain candidates rank higher
3. Highlights concerning discrepancies
4. Suggests next steps for investigation
5. Reminds that DNA verification is required

Use clear, professional language suitable for law enforcement.
"""
```

### 1.3 Example Good Output

```
INVESTIGATION REPORT

This analysis identifies several potential leads based on facial similarity 
and contextual factors.

Candidate #789 presents the strongest potential match with an 87% facial 
similarity score. The individual's current age (15) aligns closely with the 
expected age progression. Located in Chicago, IL, approximately 280 miles 
from the last known location.

Candidate #456 shows an 82% facial similarity score with a slight age 
discrepancy that warrants attention.

RECOMMENDED NEXT STEPS:
1. Prioritize DNA testing for Candidate #789
2. Review case files for additional context
3. Consult with forensic specialists

IMPORTANT DISCLAIMER:
This analysis should NOT be considered definitive proof of identity. 
All matches require verification through DNA testing or other biometric methods.
```

### 1.4 Example Bad Output (FORBIDDEN)

```
❌ NEVER WRITE:
"This is definitely the missing child. Candidate #789 is a confirmed match.
The facial features prove beyond doubt that this is the same person."
```

---

## 2. Age Progression Disclaimer

```
⚠️ COMPUTER-GENERATED ESTIMATE

These images are computer-generated estimates based on age progression 
algorithms. They represent possible appearances and should NOT be considered 
accurate predictions. Actual appearance may differ significantly.

Use these images as general reference only, not as definitive likenesses.
```

---

## 3. Face Detection Error Messages

**No Face Detected:**
```
"No face detected in the uploaded image. Please ensure:
- The child's face is clearly visible
- The image is well-lit
- The face is not obscured
- The image is not blurry

Try uploading a different photo with a clear, front-facing view."
```

**Multiple Faces Detected:**
```
"Multiple faces detected. Please upload an image containing only 
the missing child's face."
```

**Image Quality Too Low:**
```
"The uploaded image quality is too low for accurate face detection. 
Please upload a higher resolution image (minimum 640x640 pixels)."
```

---

## 4. Search Status Messages

**During Search:**
```
"Analyzing uploaded photo..."
"Detecting and extracting face..."
"Generating facial recognition signature..."
"Searching database for similar faces..."
"Calculating similarity scores..."
"Generating age progression images..."
"Preparing investigation report..."
"Complete!"
```

**Matches Found:**
```
"Found 10 potential candidates matching the search criteria.
Results are ranked by composite score."
```

**No Matches Found:**
```
"No candidates found matching the search criteria.

You may:
- Adjust search parameters (age range, date range, location)
- Try a different photo
- Contact database administrators"
```

---

## 5. Prompt Engineering Best Practices

### 5.1 For AI Report Generation

**DO:**
- Provide structured, labeled data
- Use consistent formatting
- Include clear instructions
- Set appropriate temperature (0.2-0.4)
- Specify output length

**DON'T:**
- Include raw user inputs without sanitization
- Use high temperature (>0.7) for factual reports
- Allow open-ended generation without constraints

### 5.2 Token Management

**Typical Token Usage:**
- System prompt: ~400 tokens
- Case data: ~150 tokens
- Top 5 candidates: ~700 tokens
- Output (report): ~500-800 tokens
- **Total: ~1800-2000 tokens**
- **Cost (GPT-4): ~$0.02-0.03 per report**

### 5.3 Fallback Strategy

If LLM API fails, generate template-based report:

```
"INVESTIGATION REPORT

Based on facial recognition analysis, the following candidates 
show potential matches:

1. Candidate #{id} - Similarity: {score}%
2. Candidate #{id} - Similarity: {score}%

These results require verification through DNA testing.

Note: Detailed AI analysis temporarily unavailable."
```

---

**Document Owner:** AI/ML Team  
**Last Updated:** August 10, 2026
