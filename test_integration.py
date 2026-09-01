"""
End-to-end integration test with Ollama/Llama.
Tests the complete RAG pipeline including generation.
"""

import sys
from app.pipeline import RAGPipeline


def test_complete_rag_pipeline():
    """Test the complete RAG pipeline with generation."""
    print("\n" + "=" * 60)
    print("END-TO-END RAG PIPELINE TEST")
    print("=" * 60)
    
    # Initialize pipeline with Llama 3.2 3B
    print("\n1. Initializing RAG Pipeline with Llama 3.2 3B...")
    pipeline = RAGPipeline(llama_model="llama3.2:3b")
    print("   ✓ Pipeline initialized")
    
    # Ingest sample data
    print("\n2. Ingesting sample documents...")
    sample_text = """
    Python is a versatile programming language widely used in web development, data science, and artificial intelligence.
    
    FastAPI is a modern, fast web framework for building APIs with Python 3.7+. It provides automatic API documentation and validation.
    
    Retrieval-Augmented Generation (RAG) combines information retrieval with generative AI models to provide more accurate and contextual responses.
    
    Large Language Models (LLMs) like Llama are powerful neural networks trained on vast amounts of text data, enabling them to understand and generate human-like text.
    
    Vector databases and embeddings are crucial for efficient similarity search in RAG systems, allowing relevant context to be retrieved quickly.
    """ * 2  # Repeat for more content
    
    result = pipeline.ingest_text(sample_text, source="sample_doc")
    print(f"   ✓ Ingested text with {result['chunks_created']} chunks")
    
    # Test query
    print("\n3. Testing query with generation...")
    question = "What is Python used for?"
    print(f"   Question: '{question}'")
    
    try:
        result = pipeline.query(question)
        
        if "error" in result:
            print(f"   ✗ Error: {result['error']}")
            return False
        
        print(f"\n   Generated Answer:")
        print(f"   {result['answer'][:200]}...")
        print(f"\n   Retrieved {result['num_documents_retrieved']} relevant documents:")
        for i, doc in enumerate(result["retrieved_docs"], 1):
            print(f"   {i}. (score: {doc['score']:.4f}) {doc['document'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error during query: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the integration test."""
    print("\n" + "=" * 60)
    print("RAG PIPELINE INTEGRATION TEST WITH OLLAMA")
    print("=" * 60)
    
    success = test_complete_rag_pipeline()
    
    if success:
        print("\n" + "=" * 60)
        print("INTEGRATION TEST PASSED ✓")
        print("=" * 60)
        print("\nRAG Pipeline is ready to use!")
        print("\nTo start the API server:")
        print("  uvicorn app.main:app --reload")
        return 0
    else:
        print("\n" + "=" * 60)
        print("INTEGRATION TEST FAILED ✗")
        print("=" * 60)
        print("\nPlease check:")
        print("1. Ollama is running (ollama serve)")
        print("2. Llama 3.2 3B model is installed (ollama pull llama3.2:3b)")
        print("3. Ollama is accessible at http://localhost:11434")
        return 1


if __name__ == "__main__":
    sys.exit(main())
