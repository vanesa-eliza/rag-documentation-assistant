# RAG System Optimisation Experiments

## Baseline Performance
**Configuration:**
- Chunk size: 600 char
- Top-k retrieval: 3
- Expected sources: Original keywords (e.g., 'installation', 'error-handling', 'path_parameters')
- Embedding model: all-MiniLM-L6-v2 (384-dim)

**Results:**
```
Overall SourceHitRate@3: 37.8%
Questions answered perfectly: 2 / 15
Questions answered partially: 8 / 15
Questions answered incorrectly: 5 / 15
```

**Key insight:** Baseline established. Low hit rate suggests ranking quality is the bottleneck, not data availabiltiy.

---

## Experiment 1: Increase Chunk Size (600 -> 800 chars)

**Hypothesis:** Larger chunks provide more context per retrieval, improving semantic relevance matching.

**Results:** Hit rate decreased to **33.3%**

```
Overall SourceHitRate@3: 33.3%
Questions answered perfectly: 2 / 15
Questions answered partially: 6 / 15
Questions answered incorrectly: 7 / 15
```

**Analysis:**
- Chunk size increase diluted semantic signals
- Embeddings became less focused on specific questions
- More noise in retrieved chunks
- Bigger chunks != better retrieval. Optimal chunking is context-dependent.

**Decision:** Revert to 600-char chunks.

---

## Experiment 2: Fix expected sources keywords

**Problem discovered:** Test questions used incorect keywords
- Expected: 'installation', 'error_handling', 'path_parameters' (underscores)
- Actual files: 'first-steps', 'handling-errors', 'path-params' (hyphens)
- Substring matching was failling due to mismatch

**Results with fixed keywords:**
```
Overall SourceHitRate@3: 40.6% which bacomes the new baseline.
```

**Leson:** Evaluation metrics are only as good as the test data. Proper keyword alignment is crutial for meaningful metrics.

## Experiment 3: Increase top-k parameter (3 -> 5, 10, 15, 20, etc.)

**Hypothesis:** Current issue is ranking, not data. Retrieving more chunks increases chances of finding expected sources.

### Results at different k values:

| top-k | Hit rate | Perfect | Partial | Incorrect | Δ from baseline |
|-------|----------|---------|---------|-----------|-----------------|
| 3     | 40.6%    | 2       | 8       | 5         | baseline        |
| 5     | 50.6%    | 3       | 9       | 3         | + 10%           |
| 10    | 67.2%    | 6       | 7       | 2         | + 26.6%         |
| 15    | 70.6%    | 6       | 8       | 1         | + 30%           |
| 20    | 70.6%    | 6       | 8       | 1         | + 30% (plateau) |
| 50    | 76.1%    | 8       | 6       | 1         | + 35.5%         |
| 100   | 77.8%    | 9       | 5       | 1         | + 37.2%         |
| 200   | 81.1%    | 9       | 6       | 0         | + 40.5%         |
| 300   | 81.1%    | 9       | 6       | 0         | ceiling         |
|_______|__________|_________|_________|___________|_________________| 

**Key insights:**
1. **Linear improvement 3 -> 15:** Each +k increment adds ~ 10% improvement
2. **Plateau at k=20:** No difference between top-20 and top-15
3. **Diminishing returns after k=20:** k=100 adds only 7.2%, k=200 adds only 10%
4. **Ceiling found:** 81.1% at k=200-300

**Why top-k works:**
- Sources are in database, just ranked lower than positions 3-5
- Semantic search ranking quality needs major improvements
- Trade-off: more results shown to users vs higher hit rate

**Decision:** Using top-k = 15 for production untill semantic search ranking is improved (70.6% is a sweet spot)

---

## Conclusion

1. **Chunk size optimisation is non-obvious**
    - Intuition (bigger = more context) was wrong
    - Optimal size depends on embedding model, query complexity,etc.
    - Default 600 chars was already well-tuned

2. **Ranking quality is the bottleneck, not retrieval**
    - Sources exist in databse but ranked poorly
    - Increasing top-k is a quick win (80/20 rule)
    - Better embedding would be the next improvment step

3. **Evaluation metrics must match implementation**
    - Wrong expected_sources masked real performance
    - Proper keyword alignment is critical for benchmarking
    - Always validate evaluation test data against actual system

4. **Diminishing returns are real**
    - 37.8% -> 70.6%: massive +33% gain
    - 70.6% -> 81.1%: only +10.5% gain for a big jump from top-k=15 to top-k=200
    - Sweet spot exists between effort and benefit