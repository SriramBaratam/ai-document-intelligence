# AI Document Intelligence - RAG Pipeline

A simple Retrieval-Augmented Generation (RAG) application built with FastAPI, FAISS, and Llama.

## Architecture

```
PDF/Text Input
    ↓
Text Extraction & Chunking
    ↓
Embeddings (SentenceTransformer)
    ↓
FAISS Vector Store
    ↓
Query Processing
    ↓
Retrieval (top-k similar documents)
    ↓
Context + Question
    ↓
Llama 3.2 3B (via Ollama)
    ↓
Answer
```

## Components

### Ingestion
- **PDF Processor** (`app/ingestion/pdf_processor.py`) - Extract text from PDFs
- **Chunker** (`app/ingestion/chunker.py`) - Split text into overlapping chunks

### Retrieval
- **Embedder** (`app/retrieval/embedder.py`) - Convert text to embeddings using SentenceTransformer
- **Vector Store** (`app/retrieval/vector_store.py`) - Store and search embeddings with FAISS

### Generation
- **Llama Generator** (`app/generation/rag.py`) - Generate answers using Ollama/Llama 3.2 3B

### Pipeline
- **RAG Pipeline** (`app/pipeline.py`) - Orchestrates all components
- **API** (`app/main.py`) - FastAPI endpoints for ingestion and queries

## Requirements

- Python 3.7+
- Ollama running locally with Llama 3.2 3B model
- Dependencies: FastAPI, FAISS, SentenceTransformer, PyPDF, requests

## Setup

1. **Install dependencies** (already done):
   ```bash
   pip install fastapi uvicorn faiss-cpu sentence-transformers pypdf python-multipart requests
   ```

2. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```

3. **Ensure Llama 3.2 3B is installed**:
   ```bash
   ollama pull llama3.2:3b
   ```

## Usage

### Start the API Server
```bash
cd /Users/baratamsriram/Downloads/ai-document-intelligence
source .venv/bin/activate
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### API Endpoints

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Ingest Text
```bash
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here...",
    "source": "document_name"
  }'
```

#### 3. Ingest PDF
```bash
curl -X POST http://localhost:8000/ingest/pdf \
  -F "file=@/path/to/document.pdf"
```

#### 4. Query (Ask Question)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the document about?"
  }'
```

### Example Usage

```python
from app.pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Ingest document
pipeline.ingest_text("Your document text here", source="example")

# Ask question
result = pipeline.query("What is the main topic?")
print(result["answer"])
print(result["retrieved_docs"])
```

## Testing

### Unit & Component Tests
```bash
python test_pipeline.py
```

### End-to-End Integration Test
```bash
python test_integration.py
```

## Configuration

Customize the pipeline in `app/pipeline.py`:
```python
pipeline = RAGPipeline(
    embedding_model="all-MiniLM-L6-v2",  # SentenceTransformer model
    llama_model="llama3.2:3b",            # Ollama model
    chunk_size=500,                       # Characters per chunk
    chunk_overlap=50,                     # Overlap between chunks
    top_k=3,                              # Documents to retrieve
)
```

## Current Limitations

- In-memory vector store (not persistent across restarts)
- No document persistence
- Basic error handling
- No authentication

## Next Steps (Not Implemented Yet)

- [ ] Persistent vector store (e.g., Chroma, Weaviate)
- [ ] Document management (CRUD operations)
- [ ] Multiple document types (docx, txt, etc.)
- [ ] Web frontend
- [ ] Advanced retrieval strategies
- [ ] Hybrid search (keyword + semantic)
- [ ] Query expansion and re-ranking
- [ ] Caching and performance optimization

## Project Structure

```
ai-document-intelligence/
├── app/
│   ├── main.py                    # FastAPI app and endpoints
│   ├── pipeline.py                # RAG pipeline orchestration
│   ├── generation/
│   │   └── rag.py                 # Ollama/Llama integration
│   ├── ingestion/
│   │   ├── pdf_processor.py       # PDF text extraction
│   │   └── chunker.py             # Text chunking
│   └── retrieval/
│       ├── embedder.py            # SentenceTransformer embeddings
│       └── vector_store.py        # FAISS vector store
├── test_pipeline.py               # Component and integration tests
├── test_integration.py            # End-to-end test with Ollama
├── data/                          # Sample data
└── tests/                         # Additional tests (future)
```
