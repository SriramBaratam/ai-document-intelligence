"""
Test script for RAG Pipeline - verifies all components work together.
"""

import sys
from app.pipeline import RAGPipeline
from app.ingestion.chunker import chunk_text
from app.retrieval.embedder import Embedder
from app.retrieval.vector_store import VectorStore


def test_individual_components():
    """Test each component individually."""
    print("=" * 60)
    print("Testing Individual Components")
    print("=" * 60)
    
    # Test 1: Chunker
    print("\n1. Testing Text Chunker...")
    test_text = "This is a test document. " * 50  # ~1400 chars
    chunks = chunk_text(test_text, chunk_size=200, overlap=20)
    print(f"   ✓ Text chunked into {len(chunks)} chunks")
    print(f"   ✓ First chunk length: {len(chunks[0])} chars")
    
    # Test 2: Embedder
    print("\n2. Testing Embedder...")
    embedder = Embedder(model_name="all-MiniLM-L6-v2")
    embeddings = embedder.encode(chunks)
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    print(f"   ✓ Embedding dimension: {len(embeddings[0])}")
    
    # Test 3: Vector Store
    print("\n3. Testing Vector Store...")
    vector_store = VectorStore(dimension=384)
    vector_store.add(embeddings, chunks)
    print(f"   ✓ Added {len(chunks)} documents to vector store")
    
    # Test search
    query_embedding = embedder.encode("test document")
    results = vector_store.search(query_embedding, top_k=2)
    print(f"   ✓ Retrieved {len(results)} documents from vector store")
    print(f"   ✓ Top result score: {results[0]['score']:.4f}")
    
    return True


def test_pipeline_ingestion():
    """Test RAG pipeline ingestion without Ollama."""
    print("\n" + "=" * 60)
    print("Testing RAG Pipeline Ingestion")
    print("=" * 60)
    
    pipeline = RAGPipeline()
    
    # Test ingesting text
    print("\n1. Testing text ingestion...")
    sample_text = """
    The quick brown fox jumps over the lazy dog.
    Artificial intelligence is transforming the world.
    Machine learning enables computers to learn from data.
    Natural language processing helps understand human language.
    Vector databases store and retrieve embeddings efficiently.
    """ * 5  # Repeat to make it longer
    
    result = pipeline.ingest_text(sample_text, source="test")
    print(f"   ✓ Text ingested successfully")
    print(f"   ✓ Chunks created: {result['chunks_created']}")
    print(f"   ✓ Total characters: {result['total_characters']}")
    print(f"   ✓ Documents ingested flag: {pipeline.documents_ingested}")
    
    return True


def test_pipeline_retrieval():
    """Test RAG pipeline retrieval (without generation)."""
    print("\n" + "=" * 60)
    print("Testing RAG Pipeline Retrieval")
    print("=" * 60)
    
    pipeline = RAGPipeline()
    
    # Ingest sample data
    sample_text = """
    Python is a popular programming language.
    Python is used for web development, data science, and machine learning.
    FastAPI is a modern web framework for building APIs.
    RAG stands for Retrieval-Augmented Generation.
    LLMs are large language models that can understand and generate text.
    """ * 3
    
    pipeline.ingest_text(sample_text, source="test")
    
    # Test retrieval
    print("\n1. Testing retrieval with a question...")
    question = "What is Python used for?"
    question_embedding = pipeline.embedder.encode(question)
    retrieved = pipeline.vector_store.search(question_embedding, top_k=3)
    
    print(f"   ✓ Retrieved {len(retrieved)} documents")
    for i, doc in enumerate(retrieved, 1):
        print(f"   ✓ Doc {i} score: {doc['score']:.4f}")
        print(f"      Text: {doc['document'][:80]}...")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAG PIPELINE TEST SUITE")
    print("=" * 60)
    
    try:
        # Test individual components
        test_individual_components()
        
        # Test pipeline ingestion
        test_pipeline_ingestion()
        
        # Test pipeline retrieval
        test_pipeline_retrieval()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Ensure Ollama is running (ollama serve)")
        print("2. Ensure Llama 3.2 3B model is available (ollama pull llama2)")
        print("3. Start the FastAPI server: uvicorn app.main:app --reload")
        print("4. Test endpoints with curl or Postman")
        print("\nExample API calls:")
        print("  POST /ingest/text")
        print("  POST /query")
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
