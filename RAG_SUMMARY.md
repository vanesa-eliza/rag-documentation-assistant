# RAG Pipeline Report

## Build the RAG Answer Generation Pipeline

### What was built
- Semantic search function retrieving top-3 relevant chunks
- Rag prompt with proper source citations [Source N]
- LLM integration using Ollama
- Streamlit web interface with expandable context

### Architecture
User Question
↓
[Embed query with all-MiniLM-L6-v2]
↓
[Search ChromaDB->top 3 chunks]
↓
[Build RAG prompt with citations]
↓
[Call Ollama (llama3.2:3b)]
↓
[Generate answer with [Source N] citations]
↓
[Display in Streamlit UI]

### Results

**Semantic Search:**
- Rettrieves 3 most relevant chunks
- Similarity scores displayed (0.73 - 0.80 typical)
- Metadata preserved (source, section)

**Answer Generation:**
- Uses Ollama (local, no API costs)
- Generates real answers based on context
- Properly cites sources [Source 1], [Source 2], etc.

**User Interface (Streamlit):**
- Question input box
- Real-time answer generation
- Sources listed with similarity scores
- Expandable context viewer
- Settings sidebar

### Key Features

**No API Costs**
- Uses Ollama for free, local LLM
- Runs entirely on your machine

**Proper Citations**
- [Source N] format answers
- Links back to original documents

**Fast Retrieval**
- Semantic search: <100ms
- LLM generation: 5-30 seconds

**User-Friendly**
- Streamlit web interface
- Clean, intuitive design
- Expandable retrieved context

### Performance

- Query embedding: <100ms
- ChromaDB search: <100ms
- Ollama generation: 5-30 seconds
- Total end-to-end: 10-40 seconds

### Files

- `rag_pipeline.py` - Core RAG pipeline (~120 lines)
- `streamlit_app.py` - Web UI (~80 lines)
- `chromadb/` - Vector database
- `embedding_indexer.py` - Indexing script

### How to run

````bash
# Make sure Ollama is running
ollama serve

# In another terminal
streamlit run streamlit_app.py
```

Opens at: `http://localhost:8501`

Date: 24/09/2026
