# Logging and Evaluation

## Overview 
Evaluation of the RAG system on a 15-question test set using SourceHitRate@3 metric.

## Methodology

### SourceHitRate@k
Measures: **What % of expected relevant sources appear in top-k retrieved chunks?**

For each question:
1. Retrieved top-3 chunks via semantic search
2. Check if ecpected source keywords appear in retrieved sources
3. Calculate hit rate: (matches / expected_sources) x 100%

### Test Set (15 Questions)
| # | Questions | Expected Sources |
|---|-----------|------------------|
| 1 |'How do I install FastAPI?'| tutorial, installation, first-steps |
| 2 | ... | ... |

---

## Baseline Results (37.8%)

### Overall Metrics
- **SourceHitRate@3: 37.8%**
- Perfect (100% hit): 2/15 (13%)
- Partial (0 - 100% hit): 8/15 (53%)
- Failed (0% hit): 5/15 (33%)

### Performance by Category
| Category             | Questions | Hit Rate |
|----------------------|-----------|----------|
| Core concepts        |     1     |   100%   |
| Setup / Installation |     3     |    0%    |
| Advanced Features    |     4     |   50%    |
| Deployment           |     2     |   33%    |
| Testing              |     1     |    0%    |
|______________________|___________|__________|

## Logging Implementation

### Log Format (JSONL)
Each interaction logged with"
```json
{
    "timestamp": " 2026-09-25T11:48:00",
    "question": "How do I install FastAPI?",
    "retrieved_sources": [
        {"source": "file.md", "section": "Title", "similarity": 0.857}
    ],
    "answer": "..."
}
```

### Location
`logs/interactions.jsonl` - All user interactions logged here

---

## Artifacts Generated

| File | Purpose |
|------|---------|
|`evaluation_results.jsonl` | Automated evaluation results |
|`logs/interactions.jsonl` | User interaction logs |
|`EVALUATION.md` | This report |

---

Date: 25/09/26