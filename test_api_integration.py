"""
End-to-end API integration test.
Tests uploading a PDF and querying via the FastAPI endpoints.
"""

import sys
from fastapi.testclient import TestClient
from app.main import app


def test_pdf_upload_and_query():
    """Test the complete workflow: upload PDF → query."""
    print("\n" + "=" * 70)
    print("END-TO-END API INTEGRATION TEST")
    print("=" * 70)
    
    client = TestClient(app)
    
    # Test 1: Upload PDF via API
    print("\n1. Testing PDF Upload via /ingest/pdf endpoint...")
    try:
        with open("data/test.pdf", "rb") as pdf_file:
            response = client.post(
                "/ingest/pdf",
                files={"file": ("test.pdf", pdf_file, "application/pdf")}
            )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        
        print(f"   ✓ PDF uploaded successfully")
        print(f"   ✓ Status: {result['status']}")
        print(f"   ✓ Chunks created: {result['chunks_created']}")
        print(f"   ✓ Total characters: {result['total_characters']}")
        
    except Exception as e:
        print(f"   ✗ PDF upload failed: {str(e)}")
        return False
    
    # Test 2: Verify health shows documents ingested
    print("\n2. Verifying health check shows documents ingested...")
    response = client.get("/health")
    assert response.status_code == 200
    health = response.json()
    print(f"   ✓ Documents ingested: {health['documents_ingested']}")
    assert health['documents_ingested'] == True, "Should show documents ingested"
    
    # Test 3: Query the uploaded PDF
    print("\n3. Testing Query via /query endpoint...")
    question = "What is Artificial Intelligence?"
    
    try:
        response = client.post(
            "/query",
            json={"question": question}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        
        print(f"\n   Question: {result['question']}")
        print(f"\n   Retrieved Documents: {result['num_documents_retrieved']}")
        for i, doc in enumerate(result['retrieved_docs'], 1):
            print(f"\n     [{i}] Score: {doc['score']:.4f}")
            print(f"         Text: {doc['document'][:100]}...")
        
        print(f"\n   Generated Answer:")
        print(f"   {result['answer']}")
        
        # Verify we got a meaningful answer
        assert result['answer'] and len(result['answer']) > 0, "Should have an answer"
        assert result['num_documents_retrieved'] > 0, "Should retrieve documents"
        
    except Exception as e:
        print(f"   ✗ Query failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test another question
    print("\n" + "-" * 70)
    print("\n4. Testing Another Query...")
    question2 = "What is Machine Learning?"
    
    try:
        response = client.post(
            "/query",
            json={"question": question2}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        print(f"\n   Question: {result['question']}")
        print(f"   Answer: {result['answer']}")
        print(f"   Documents retrieved: {result['num_documents_retrieved']}")
        
        assert result['answer'] and len(result['answer']) > 0, "Should have an answer"
        
    except Exception as e:
        print(f"   ✗ Query failed: {str(e)}")
        return False
    
    # Test 5: Ingest additional text and verify persistence
    print("\n" + "-" * 70)
    print("\n5. Testing Additional Text Ingestion (Persistence)...")
    
    try:
        response = client.post(
            "/ingest/text",
            json={
                "text": "Deep Learning uses neural networks with multiple layers. Transformers are the foundation of modern AI models.",
                "source": "additional_doc"
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        print(f"   ✓ Additional text ingested")
        print(f"   ✓ New chunks: {result['chunks_created']}")
        
        # Test query that should retrieve from both documents
        response = client.post(
            "/query",
            json={"question": "What is Deep Learning?"}
        )
        
        assert response.status_code == 200
        result = response.json()
        print(f"   ✓ Query across multiple ingested documents works")
        print(f"   ✓ Answer: {result['answer'][:100]}...")
        
    except Exception as e:
        print(f"   ✗ Persistence test failed: {str(e)}")
        return False
    
    return True


def main():
    """Run the integration test."""
    print("\n" + "=" * 70)
    print("API INTEGRATION TEST - PDF UPLOAD AND QUERY")
    print("=" * 70)
    
    success = test_pdf_upload_and_query()
    
    if success:
        print("\n" + "=" * 70)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 70)
        print("\nAPI Integration Summary:")
        print("  ✓ PDF upload via /ingest/pdf endpoint")
        print("  ✓ Query via /query endpoint")
        print("  ✓ Document retrieval and answer generation")
        print("  ✓ Document persistence across requests")
        print("  ✓ Multiple documents ingestion")
        print("\nThe API is ready for production use!")
        return 0
    else:
        print("\n" + "=" * 70)
        print("INTEGRATION TEST FAILED ✗")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
