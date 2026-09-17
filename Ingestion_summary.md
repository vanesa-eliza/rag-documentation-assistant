# Document Ingestion

## Subproject
- **Source:** FastAPI Documentation
- **Repository:** https://github.com/toanglo/fastapi
- **Location:** `.docs/en/docs`

## Collection
- **Total files:** 155 markdown files
- **Total source text:** ~1.3MB

## Ingestion Results
- **Total chunks generated:** 3219
- **Average chunk size:** 406 characters (101 tokens)
- **Median chunk size:** 456 characters
- **Min chunk size:** 1 character
- **Max chunk size:** 3578 characters
- **Largest file:** 1550 chunks

## Chunking Strategy

### Primary: Header-Based Splitting
- Splits by markdown headers (# ## ###)
- Preserves document structure
- Stores section titles as metadata
- Skips headers inside code blocks

### Fallback: Fixed-Size Splitting
- When section > 600 characters
- Splits by sentence boundaries
- Respects sentence integrity
- Labels parts as "(part0)", "(part1)", etc.

### Thresholds
- Minimum chunk size: 80 characters
- Maximum section size: 600 characters
- Token estimate: characters / 4

## Metadata Preserved
Each chunk contains:
- `source`: File path (relative)
- `section`: Header title
- `chunk_index`: Global chunk index
- `text`: Actual content
- `char_count`: Length in characters
- `token_estimate`: Approximate token count

## Output Files

### output/chunks.jsonl (1.8 MB)
- **Format:** JSONL (one JSON object per line)
- **Count:** 3219 chunks
- **Usage:** Load for embedding, RAG, fine-tuning

### output/stats.json (170 B)
- **Format:** JSON
- **Contents:** Summary statistics
- **Usage:** Benchmarking, reporting

## Quality Metrics
- **Processing errors:** 0
- **Files with 0 chunks:** ~5 (mostly empty index files)
- **Metadata completeness:** 100%
- **Processing time:** < 30s

## Learning Outcomes
Through building this project, I learned:
- File discovery and recursion (`.rglob()`)
- Sorting files for consistent processing
- Regular expressions for header detection: `r'^(#{1,6})\s+(.+)$'`
- Removing anchor syntax: `r'\s*\{.*\}$'`
- Text processing and string manipulation
- Data structures (dataclasses)
- JSON serialisation (JSONL format)
- File I/O
- Code block detection to avoid false positives
- Chunking strategies (header-based + fixed-size fallback)

## Code Structure
- `Chunk`dataclass: Data structure for one chunk
- `find_md_files()`: Discover markdown files
- `read_file()`: Read and decode files
- `extract_headers()`: Parse markdown structure
- `create_chunks()`: Convert sections to chunks with intellingent splitting
- `ingest_all()`: Orchestrate entire pipeline
- `save_chunks_jsonl()`: Export chunks
- `save_stats()`: Export statistics

---
**Status:** Complete
**Date:** 15.09.26
