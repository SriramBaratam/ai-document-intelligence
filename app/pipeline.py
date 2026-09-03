"""RAG Pipeline - ingestion, retrieval, and grounded generation."""

from pathlib import Path

from app.ingestion.pdf_processor import extract_pages_from_pdf
from app.ingestion.chunker import chunk_text
from app.retrieval.embedder import Embedder
from app.retrieval.vector_store import VectorStore
from app.generation.rag import LlamaGenerator, create_qa_prompt


class RAGPipeline:
    """RAG pipeline: documents -> chunks -> embeddings -> retrieval -> LLM."""

    def __init__(self, embedding_model="all-MiniLM-L6-v2", llama_model="llama3.2:3b", chunk_size=500, chunk_overlap=50, top_k=5):
        self.embedder = Embedder(model_name=embedding_model)
        self.generator = LlamaGenerator(model=llama_model)
        self.vector_store = VectorStore(dimension=384)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.documents_ingested = False

    def ingest_pdf(self, file_path: str, source_name: str | None = None) -> dict:
        """Extract a PDF page-by-page and retain filename/page metadata."""
        pages = extract_pages_from_pdf(file_path)
        source_name = source_name or Path(file_path).name

        all_chunks = []
        metadata = []
        for page in pages:
            chunks = chunk_text(page["text"], chunk_size=self.chunk_size, overlap=self.chunk_overlap)
            all_chunks.extend(chunks)
            metadata.extend({
                "source": source_name,
                "page_number": page["page_number"],
            } for _ in chunks)

        if not all_chunks:
            raise ValueError("No readable text was found in the PDF")

        embeddings = self.embedder.encode(all_chunks)
        self.vector_store.add(embeddings, all_chunks, metadata)
        self.documents_ingested = True

        return {
            "status": "success",
            "file": source_name,
            "chunks_created": len(all_chunks),
            "pages_processed": len(pages),
            "total_characters": sum(len(page["text"]) for page in pages),
        }

    def ingest_text(self, text: str, source: str = "direct_input") -> dict:
        """Chunk and index raw text with a source label."""
        chunks = chunk_text(text, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        if not chunks:
            raise ValueError("No text was provided")

        embeddings = self.embedder.encode(chunks)
        metadata = [{"source": source, "page_number": None} for _ in chunks]
        self.vector_store.add(embeddings, chunks, metadata)
        self.documents_ingested = True

        return {
            "status": "success",
            "source": source,
            "chunks_created": len(chunks),
            "total_characters": len(text),
        }

    def query(self, question: str) -> dict:
        """Retrieve relevant chunks and generate a grounded answer."""
        if not self.documents_ingested:
            return {"error": "No documents ingested yet. Please ingest a PDF or text first.", "answer": None, "retrieved_docs": []}

        question_embedding = self.embedder.encode(question)
        retrieved_docs = self.vector_store.search(question_embedding, top_k=self.top_k)
        context = "\n\n".join(
            f"[Source {i}: {doc.get('source', 'Unknown')}"
            + (f", page {doc['page_number']}]" if doc.get("page_number") else "]")
            + f"\n{doc['document']}"
            for i, doc in enumerate(retrieved_docs, start=1)
        )

        answer = self.generator.generate(create_qa_prompt(context, question))
        return {
            "question": question,
            "answer": answer,
            "retrieved_docs": retrieved_docs,
            "num_documents_retrieved": len(retrieved_docs),
        }

    def clear_documents(self) -> dict:
        self.vector_store.clear()
        self.documents_ingested = False
        return {"status": "success", "message": "All documents cleared"}
