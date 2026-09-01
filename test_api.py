"""
Quick API endpoint test script.
Tests the FastAPI endpoints without starting the server (direct imports).
"""

import sys
from fastapi.testclient import TestClient
from app.main import app


def test_api_endpoints():
    """Test API endpoints using TestClient."""
    print("\n" + "=" * 60)
    print("API ENDPOINT TEST")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Test 1: Health check
    print("\n1. Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Status: {data['status']}")
    print(f"   ✓ Documents ingested: {data['documents_ingested']}")
    
    # Test 2: Root endpoint
    print("\n2. Testing / endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Message: {data['message']}")
    
    # Test 3: Ingest text
    print("\n3. Testing /ingest/text endpoint...")
    response = client.post("/ingest/text", json={
        "text": """
        Artificial Intelligence is transforming industries.
        Machine learning enables computers to learn from data.
        Deep learning uses neural networks for complex tasks.
        Natural language processing helps machines understand text.
        Computer vision enables machines to interpret images.
        """ * 3,
        "source": "test_source"
    })
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Status: {data['status']}")
    print(f"   ✓ Chunks created: {data['chunks_created']}")
    print(f"   ✓ Characters: {data['total_characters']}")
    
    # Test 4: Query endpoint
    print("\n4. Testing /query endpoint...")
    response = client.post("/query", json={
        "question": "What is machine learning?"
    })
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Question: {data['question']}")
    print(f"   ✓ Answer: {data['answer'][:100]}...")
    print(f"   ✓ Documents retrieved: {data['num_documents_retrieved']}")
    
    # Test 5: Query without ingesting (should fail gracefully)
    print("\n5. Testing /query without prior ingestion (new instance)...")
    # Create a new client to test error handling
    from app.main import RAGPipeline
    # Note: The current implementation uses a shared instance, so we can't easily test this
    # without modifying the code. This is a design note for future improvement.
    print("   ℹ Note: Shared pipeline instance means this test would need code changes")
    
    # Test 6: PDF ingestion (empty file test)
    print("\n6. Testing /ingest/pdf with invalid file type...")
    response = client.post("/ingest/pdf", files={
        "file": ("test.txt", b"This is not a PDF", "text/plain")
    })
    assert response.status_code == 400
    print(f"   ✓ Correctly rejected non-PDF file")
    
    return True


def main():
    """Run API tests."""
    print("\n" + "=" * 60)
    print("FASTAPI ENDPOINT TEST SUITE")
    print("=" * 60)
    
    try:
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("ALL API TESTS PASSED ✓")
        print("=" * 60)
        
        print("\nThe API is ready to use!")
        print("\nStart the server with:")
        print("  uvicorn app.main:app --reload")
        print("\nThen use the interactive docs at:")
        print("  http://localhost:8000/docs")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ ASSERTION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
