"""
End-to-end RAG test using data/test.pdf
Tests the complete pipeline: ingest PDF → retrieve → generate answer
"""

import sys
from app.pipeline import RAGPipeline


def test_rag_with_pdf():
    """Test the RAG pipeline with the actual test.pdf file."""
    print("\n" + "=" * 70)
    print("END-TO-END RAG TEST WITH data/test.pdf")
    print("=" * 70)
    
    # Initialize pipeline
    print("\n1. Initializing RAG Pipeline...")
    pipeline = RAGPipeline(llama_model="llama3.2:3b")
    print("   ✓ Pipeline initialized")
    
    # Ingest the PDF
    print("\n2. Ingesting data/test.pdf...")
    try:
        result = pipeline.ingest_pdf("data/test.pdf")
        print(f"   ✓ PDF ingested successfully")
        print(f"   ✓ Chunks created: {result['chunks_created']}")
        print(f"   ✓ Total characters: {result['total_characters']}")
    except Exception as e:
        print(f"   ✗ Failed to ingest PDF: {str(e)}")
        return False
    
    # Show ingested chunks
    print("\n3. Ingested document chunks:")
    for i, doc in enumerate(pipeline.vector_store.documents, 1):
        print(f"   Chunk {i}: {doc[:100]}...")
    
    # Test query 1
    print("\n4. Testing Query 1: 'What is Artificial Intelligence?'")
    print("-" * 70)
    question1 = "What is Artificial Intelligence?"
    try:
        result1 = pipeline.query(question1)
        
        print(f"\n   Question: {result1['question']}")
        print(f"\n   Retrieved Documents ({result1['num_documents_retrieved']}):")
        for i, doc in enumerate(result1['retrieved_docs'], 1):
            print(f"\n     [{i}] Score: {doc['score']:.4f}")
            print(f"         Text: {doc['document']}")
        
        print(f"\n   Generated Answer:")
        print(f"   {result1['answer']}")
        
    except Exception as e:
        print(f"   ✗ Query failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test query 2
    print("\n" + "-" * 70)
    print("\n5. Testing Query 2: 'What is Machine Learning?'")
    print("-" * 70)
    question2 = "What is Machine Learning?"
    try:
        result2 = pipeline.query(question2)
        
        print(f"\n   Question: {result2['question']}")
        print(f"\n   Retrieved Documents ({result2['num_documents_retrieved']}):")
        for i, doc in enumerate(result2['retrieved_docs'], 1):
            print(f"\n     [{i}] Score: {doc['score']:.4f}")
            print(f"         Text: {doc['document']}")
        
        print(f"\n   Generated Answer:")
        print(f"   {result2['answer']}")
        
    except Exception as e:
        print(f"   ✗ Query failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run the end-to-end test."""
    print("\n" + "=" * 70)
    print("RAG PIPELINE E2E TEST WITH ACTUAL PDF")
    print("=" * 70)
    
    success = test_rag_with_pdf()
    
    if success:
        print("\n" + "=" * 70)
        print("E2E TEST PASSED ✓")
        print("=" * 70)
        print("\nRAG Pipeline successfully:")
        print("  1. Ingested PDF (data/test.pdf)")
        print("  2. Created document chunks")
        print("  3. Generated embeddings")
        print("  4. Retrieved relevant context using FAISS")
        print("  5. Generated answers using Llama 3.2 3B")
        return 0
    else:
        print("\n" + "=" * 70)
        print("E2E TEST FAILED ✗")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
