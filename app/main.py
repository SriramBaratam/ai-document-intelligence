from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os

from app.pipeline import RAGPipeline

app = FastAPI(
    title="AI Document Intelligence Platform",
    description="An AI-powered document analysis and RAG platform.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_pipeline = RAGPipeline()


class TextIngestionRequest(BaseModel):
    text: str
    source: str = "direct_input"


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "AI Document Intelligence API is running", "status": "success"}


@app.get("/health")
def health():
    return {"status": "healthy", "documents_ingested": rag_pipeline.documents_ingested}


@app.post("/ingest/text")
def ingest_text(request: TextIngestionRequest):
    try:
        return rag_pipeline.ingest_text(request.text, source=request.source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    """Ingest a PDF while preserving its original filename for citations."""
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    tmp_file_path = None
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name

        return rag_pipeline.ingest_pdf(tmp_file_path, source_name=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@app.post("/query")
def query(request: QueryRequest):
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
    try:
        return rag_pipeline.clear_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))