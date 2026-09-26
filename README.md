# RAG Document Ingestion Pipeline

A production-grade document ingestion system that answers FastAPI questions by searching official documentation and generating contextual answers.

Live Demo: 
Hit Rate: 70.6% @ top-k=15

## What is This?
This RAG system:
1. Ingests FastAPI documentation (155 markdown files)
2. Chunks documents into semantic pieces (600 chars each)
3. Embeds using sentence transformers (all-MiniLM-L6-v2)
4. Retrieves relevant sources for any question related to FastAPI
5. Generated answers using Ollama

## Example Q&A
Q: "How do I add authentication to my FastAPI app?"
Retrieved Sources:
- tutorial/security/first-steps.md
- docs/advanced/security/oauth2-scopes.md
- docs/advanced/security/index.md

**Generated Answer**

A: "According to [Source 8] tutorial/security/first-steps.md, to add authentication to your FastAPI app, you can use FastAPI's OAuth2 tool. Specifically, you can use the OAuth2PasswordBearer class to handle authentication using a username and password.

You can add authentication to your FastAPI app by creating an instance of OAuth2PasswordBearer and passing it to the auth argument of the FastAPI app.

Here's an example:"
```python
from fastapi import FastAPI, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    # Implement your login logic here
    pass
```

## Architecture

The RAG system has two main phases:

**Ingestion (one-time):** Documents are split into 600 char chunks, embedded using sentence-transformers (all-MiniLM-L6-v2) and stored in Chroma's vector database.

**Query (per-request):** The user's question is embedded using the same model, semantically searched against the vector store and the top-k results are combined with the query to generate an answer via Ollama.

**RAG system architecture diagram:**

```
            ┌─────────────────────────────────────────┐
            │         FastAPI Docs (155 files)        │
            └──────────────────┬──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Chunk Documents     │
                    │  (600 chars each)    │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Embed Chunks        │
                    │  (all-MiniLM-L6-v2)  │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Vector Store        │
                    │  (Chroma DB)         │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐    
                    │  Retrieve            │    
                    │  Top-15              │      
                    └──────────────────────┘
                               │          
                               ▼
                    ┌──────────────────────┐
                    │  Generate Answer     │
                    │  (Ollama)            │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Return to User      │
                    │  (Sources + Answer)  │
                    └──────────────────────┘
```

## Installation

Pre-requisites
- Python 3.8+
- pip
- Ollama (already running on your computer)

## Setup
1. **Clone the repository**

```bash
git clone https://github.com/vanesa-eliza/rag-documentation-assistant
cd RAG_project
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate # On windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Ingest documentation** (one-time)
```bash
python3 my_ingestor.py
```

This will:
- Download FastAPI docs (if not present)
- Split into chunks(600 chars)
- Generate embeddings using sentence-transformers
- Store in Chroma vector DB

5. **Run Streamlit app**
```bash
streamlit run streamlit_app.py
```

Opens at http://localhost:8501

## Usage

1. Type your question in the search box from the sreamlit app
2. Adjust top-k results slider (open the sidebar)
3. View retrieved sources and generated answer

## Performance

### Evaluation Results

```bash
|      Metric       | Value |
|-------------------|-------|
| SourceHitRate@15  | 70.6% |
| Perfect answers   | 6/15  |
| Partial answers   | 8/15  |
| Incorrect answers | 1/15  |
| Retrieval latency | <100ms|
| Generation latency| 2-4s  |
|___________________|_______|
```

### System Ceiling
- Max theoretical hit rate: 81.1% (with top-k=200)
- To exceed 80%: Requires better embedding model or hybrid search
- See [EVALUATION.md] for detailed breakdown

## Known Limitations

1. **Single source:** Only searches FastAPI documentation
2. **Embedding quality:** all-MiniLM works well but isn't specialised
3. **Ranking gaps:** Top-k=15 misses ~30% of questions
4. **Latency:** Ollama local inference adds 2-4s per response
5. **Missing topics:** Some advanced features may be incomplete

**Last Update:** 2026-09-26

*This is a learning project. The goal is understanding how RAG systems work.