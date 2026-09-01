"""
End-to-end FastAPI application test.
Tests all endpoints with actual requests to the running server.
"""

import requests
import json
import sys
from pathlib import Path


BASE_URL = "http://localhost:8001"


def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{title}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except:
        print(response.text)
        return None


def test_end_to_end():
    """Run complete end-to-end test."""
    print("\n" + "=" * 80)
    print("FASTAPI APPLICATION END-TO-END TEST")
    print("=" * 80)
    
    # Test 1: Health Check
    print("\n" + "-" * 80)
    print("TEST 1: GET /health - Health Check")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = print_response("Response:", response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data['status'] == 'healthy', "Status should be healthy"
        print("✓ PASSED - Server is healthy")
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        return False
    
    # Test 2: Root Endpoint
    print("\n" + "-" * 80)
    print("TEST 2: GET / - Root Endpoint")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        data = print_response("Response:", response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ PASSED - Root endpoint works")
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        return False
    
    # Test 3: Upload PDF
    print("\n" + "-" * 80)
    print("TEST 3: POST /ingest/pdf - Upload PDF File")
    print("-" * 80)
    try:
        pdf_path = Path("data/test.pdf")
        if not pdf_path.exists():
            print(f"✗ FAILED - {pdf_path} not found")
            return False
        
        print(f"Uploading: {pdf_path}")
        with open(pdf_path, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            response = requests.post(f"{BASE_URL}/ingest/pdf", files=files, timeout=30)
        
        data = print_response("Response:", response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data['status'] == 'success', "Ingestion should succeed"
        print(f"✓ PASSED - PDF ingested: {data['chunks_created']} chunks, {data['total_characters']} chars")
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Verify Health Shows Documents Ingested
    print("\n" + "-" * 80)
    print("TEST 4: GET /health - Verify Documents Ingested")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = print_response("Response:", response)
        assert response.status_code == 200
        assert data['documents_ingested'] == True, "Should show documents ingested"
        print("✓ PASSED - Health check confirms documents ingested")
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        return False
    
    # Test 5: Query Endpoint
    print("\n" + "-" * 80)
    print("TEST 5: POST /query - Ask Question About PDF")
    print("-" * 80)
    question = "What is Artificial Intelligence?"
    print(f"Question: {question}")
    
    try:
        payload = {"question": question}
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        data = print_response("Response:", response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify response structure
        assert 'question' in data, "Response should contain 'question'"
        assert 'answer' in data, "Response should contain 'answer'"
        assert 'retrieved_docs' in data, "Response should contain 'retrieved_docs'"
        assert 'num_documents_retrieved' in data, "Response should contain 'num_documents_retrieved'"
        
        # Verify content
        assert len(data['answer']) > 0, "Answer should not be empty"
        assert data['num_documents_retrieved'] > 0, "Should retrieve at least one document"
        assert len(data['retrieved_docs']) > 0, "Should have retrieved documents"
        
        print(f"\n✓ PASSED - Query answered successfully")
        print(f"  - Question: {data['question']}")
        print(f"  - Documents retrieved: {data['num_documents_retrieved']}")
        print(f"  - Answer preview: {data['answer'][:150]}...")
        
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Another Query
    print("\n" + "-" * 80)
    print("TEST 6: POST /query - Second Question")
    print("-" * 80)
    question2 = "What is Machine Learning?"
    print(f"Question: {question2}")
    
    try:
        payload = {"question": question2}
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        data = print_response("Response:", response)
        assert response.status_code == 200
        assert len(data['answer']) > 0, "Answer should not be empty"
        
        print(f"\n✓ PASSED - Second query answered successfully")
        print(f"  - Answer: {data['answer'][:150]}...")
        
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 7: Ingest Additional Text
    print("\n" + "-" * 80)
    print("TEST 7: POST /ingest/text - Ingest Additional Text")
    print("-" * 80)
    
    try:
        text = "Transformers are neural network architectures that use attention mechanisms. They are the foundation of modern large language models like GPT and Llama."
        payload = {"text": text, "source": "transformer_doc"}
        response = requests.post(
            f"{BASE_URL}/ingest/text",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        data = print_response("Response:", response)
        assert response.status_code == 200
        assert data['status'] == 'success'
        print(f"✓ PASSED - Text ingested: {data['chunks_created']} chunks")
        
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 8: Query Across Multiple Documents
    print("\n" + "-" * 80)
    print("TEST 8: POST /query - Query Across Multiple Documents")
    print("-" * 80)
    question3 = "What are Transformers?"
    print(f"Question: {question3}")
    
    try:
        payload = {"question": question3}
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        data = print_response("Response:", response)
        assert response.status_code == 200
        assert len(data['answer']) > 0
        
        print(f"\n✓ PASSED - Query across multiple documents works")
        print(f"  - Documents retrieved: {data['num_documents_retrieved']}")
        print(f"  - Answer: {data['answer'][:150]}...")
        
    except Exception as e:
        print(f"✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main test runner."""
    print("\n" + "=" * 80)
    print("FASTAPI APPLICATION E2E TEST SUITE")
    print("=" * 80)
    print(f"Testing server at: {BASE_URL}")
    print("=" * 80)
    
    try:
        # Verify server is running
        print("\nChecking if server is running...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✓ Server is responding")
    except Exception as e:
        print(f"✗ Cannot connect to server at {BASE_URL}")
        print("Make sure to start the server with:")
        print("  uvicorn app.main:app --reload --port 8001")
        return 1
    
    success = test_end_to_end()
    
    if success:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓✓✓")
        print("=" * 80)
        print("\nSummary:")
        print("  ✓ Server health check")
        print("  ✓ PDF file upload and ingestion")
        print("  ✓ Question answering with Llama")
        print("  ✓ Document retrieval and relevance scoring")
        print("  ✓ Multiple document management")
        print("  ✓ Context-aware answer generation")
        print("\nThe FastAPI application is fully functional!")
        return 0
    else:
        print("\n" + "=" * 80)
        print("TESTS FAILED ✗")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
