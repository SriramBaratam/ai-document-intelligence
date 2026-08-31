from fastapi import FastAPI

app = FastAPI(
    title="AI Document Intelligence Platform",
    description="An AI-powered document analysis and RAG platform.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Document Intelligence API is running",
        "status": "success",
    }