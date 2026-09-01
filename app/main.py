from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os

from app.pipeline import RAGPipeline

app = FastAPI(
    title="AI Document Intelligence Platform",
    description="An AI-powered document analysis and RAG platform.",
    version="0.1.0",
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the RAG pipeline (shared instance)
rag_pipeline = RAGPipeline()


# Request/Response models
class TextIngestionRequest(BaseModel):
    text: str
    source: str = "direct_input"


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "AI Document Intelligence API is running",
        "status": "success",
    }


@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "documents_ingested": rag_pipeline.documents_ingested,
    }


@app.post("/ingest/text")
def ingest_text(request: TextIngestionRequest):
    """
    Ingest raw text into the RAG pipeline.
    """
    try:
        result = rag_pipeline.ingest_text(request.text, source=request.source)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Ingest a PDF file into the RAG pipeline.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name
        
        # Process the PDF
        result = rag_pipeline.ingest_pdf(tmp_file_path)
        
        # Clean up the temporary file
        os.unlink(tmp_file_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query(request: QueryRequest):
    """
    Ask a question to the RAG pipeline.
    Returns the answer and retrieved documents.
    """
    try:
        result = rag_pipeline.query(request.question)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
def clear_documents():
    """
    Clear all ingested documents from the vector store.
    """
    try:
        result = rag_pipeline.clear_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))