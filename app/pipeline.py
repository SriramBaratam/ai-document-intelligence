"""
RAG Pipeline - Integrates ingestion, retrieval, and generation components.
"""

from app.ingestion.pdf_processor import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.retrieval.embedder import Embedder
from app.retrieval.vector_store import VectorStore
from app.generation.rag import LlamaGenerator, create_qa_prompt


class RAGPipeline:
    """
    Simple RAG (Retrieval-Augmented Generation) pipeline.
    
    Flow: PDF/text → chunks → embeddings → FAISS retrieval → Llama → answer
    """
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        llama_model: str = "llama3.2:3b",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k: int = 3,
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            embedding_model: SentenceTransformer model name
            llama_model: Ollama model name (default: llama2)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            top_k: Number of documents to retrieve
        """
        self.embedder = Embedder(model_name=embedding_model)
        self.generator = LlamaGenerator(model=llama_model)
        self.vector_store = VectorStore(dimension=384)  # all-MiniLM-L6-v2 produces 384-dim embeddings
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        
        self.documents_ingested = False
    
    def ingest_pdf(self, file_path: str) -> dict:
        """
        Ingest a PDF file into the RAG pipeline.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with ingestion results
        """
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Chunk the text
        chunks = chunk_text(text, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        
        # Generate embeddings for chunks
        embeddings = self.embedder.encode(chunks)
        
        # Add to vector store
        self.vector_store.add(embeddings, chunks)
        
        self.documents_ingested = True
        
        return {
            "status": "success",
            "file": file_path,
            "chunks_created": len(chunks),
            "total_characters": len(text),
        }
    
    def ingest_text(self, text: str, source: str = "unknown") -> dict:
        """
        Ingest raw text into the RAG pipeline.
        
        Args:
            text: The text to ingest
            source: Source identifier for the text
            
        Returns:
            Dictionary with ingestion results
        """
        # Chunk the text
        chunks = chunk_text(text, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        
        # Generate embeddings for chunks
        embeddings = self.embedder.encode(chunks)
        
        # Add to vector store
        self.vector_store.add(embeddings, chunks)
        
        self.documents_ingested = True
        
        return {
            "status": "success",
            "source": source,
            "chunks_created": len(chunks),
            "total_characters": len(text),
        }
    
    def query(self, question: str) -> dict:
        """
        Ask a question to the RAG pipeline.
        
        Args:
            question: The question to ask
            
        Returns:
            Dictionary with answer and retrieved documents
        """
        if not self.documents_ingested:
            return {
                "error": "No documents ingested yet. Please ingest a PDF or text first.",
                "answer": None,
                "retrieved_docs": [],
            }
        
        # Generate embedding for the question
        question_embedding = self.embedder.encode(question)
        
        # Retrieve relevant documents
        retrieved_docs = self.vector_store.search(question_embedding, top_k=self.top_k)
        
        # Combine retrieved documents as context
        context = "\n\n".join([doc["document"] for doc in retrieved_docs])
        
        # Generate answer using Llama
        prompt = create_qa_prompt(context, question)
        answer = self.generator.generate(prompt)
        
        return {
            "question": question,
            "answer": answer,
            "retrieved_docs": retrieved_docs,
            "num_documents_retrieved": len(retrieved_docs),
        }
    
    def clear_documents(self) -> dict:
        """
        Clear all ingested documents from the vector store.
        
        Returns:
            Dictionary confirming the clear operation
        """
        self.vector_store.clear()
        self.documents_ingested = False
        return {
            "status": "success",
            "message": "All documents cleared",
        }
