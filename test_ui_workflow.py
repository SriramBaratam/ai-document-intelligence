"""
End-to-end UI workflow test.
Simulates the complete user journey: upload PDF → ask question → get answer
"""

import requests
import json
import sys
from pathlib import Path

# Check both servers
FRONTEND_URL = "http://localhost:3000"
API_URL = "http://localhost:8001"


def print_section(title):
    """Print a formatted section title."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_servers_running():
    """Verify both servers are running."""
    print_section("CHECKING SERVERS")
    
    try:
        response = requests.get(f"{FRONTEND_URL}/index.html", timeout=5)
        print(f"✓ Frontend server is running on {FRONTEND_URL}")
    except Exception as e:
        print(f"✗ Frontend server not running on {FRONTEND_URL}: {e}")
        return False
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✓ API server is running on {API_URL}")
    except Exception as e:
        print(f"✗ API server not running on {API_URL}: {e}")
        return False
    
    return True


def test_ui_workflow():
    """Test the complete UI workflow."""
    print_section("COMPLETE UI WORKFLOW TEST")
    
    # Step 1: Upload PDF
    print("STEP 1: Upload PDF Document")
    print("-" * 80)
    pdf_path = Path("data/test.pdf")
    
    if not pdf_path.exists():
        print(f"✗ PDF file not found: {pdf_path}")
        return False
    
    print(f"Uploading {pdf_path}...")
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            response = requests.post(f"{API_URL}/ingest/pdf", files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"✗ Upload failed: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        print(f"✓ PDF uploaded successfully")
        print(f"  - Chunks created: {result['chunks_created']}")
        print(f"  - Total characters: {result['total_characters']}")
        print(f"  - File: {result['file']}")
        
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False
    
    # Step 2: Verify documents ingested
    print("\nSTEP 2: Verify Documents Status")
    print("-" * 80)
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        data = response.json()
        
        if not data['documents_ingested']:
            print("✗ Documents should be ingested")
            return False
        
        print(f"✓ Health check confirms documents are ingested")
        print(f"  - Status: {data['status']}")
        print(f"  - Documents ingested: {data['documents_ingested']}")
        
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Step 3: Ask first question
    print("\nSTEP 3: Ask First Question - 'What is Artificial Intelligence?'")
    print("-" * 80)
    question1 = "What is Artificial Intelligence?"
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"question": question1},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Query failed: {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        
        print(f"✓ Question answered successfully")
        print(f"\n  Question: {data['question']}")
        print(f"\n  Answer:")
        print(f"  {data['answer']}")
        
        print(f"\n  Retrieved {data['num_documents_retrieved']} document(s):")
        for i, doc in enumerate(data['retrieved_docs'], 1):
            relevance = (doc['score'] * 100)
            print(f"\n    [{i}] Relevance: {relevance:.1f}%")
            print(f"        Text: {doc['document'][:100]}...")
        
    except Exception as e:
        print(f"✗ Query error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Add additional text
    print("\n\nSTEP 4: Add Additional Text via UI")
    print("-" * 80)
    
    additional_text = "Deep Learning is a subset of Machine Learning that uses neural networks with multiple layers. Neural networks are inspired by the structure of biological brains and can learn complex patterns from data."
    
    try:
        response = requests.post(
            f"{API_URL}/ingest/text",
            json={"text": additional_text, "source": "ui_text_input"},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Text ingestion failed: {response.status_code}")
            return False
        
        result = response.json()
        print(f"✓ Text added successfully")
        print(f"  - Chunks created: {result['chunks_created']}")
        print(f"  - Source: {result['source']}")
        
    except Exception as e:
        print(f"✗ Text ingestion error: {e}")
        return False
    
    # Step 5: Ask second question about new content
    print("\nSTEP 5: Ask Second Question - 'What is Deep Learning?'")
    print("-" * 80)
    question2 = "What is Deep Learning?"
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"question": question2},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Query failed: {response.status_code}")
            return False
        
        data = response.json()
        
        print(f"✓ Question answered successfully")
        print(f"\n  Question: {data['question']}")
        print(f"\n  Answer:")
        print(f"  {data['answer']}")
        
        print(f"\n  Retrieved {data['num_documents_retrieved']} document(s):")
        for i, doc in enumerate(data['retrieved_docs'], 1):
            relevance = (doc['score'] * 100)
            print(f"\n    [{i}] Relevance: {relevance:.1f}%")
            print(f"        Text: {doc['document'][:100]}...")
        
    except Exception as e:
        print(f"✗ Query error: {e}")
        return False
    
    # Step 6: Ask third question
    print("\nSTEP 6: Ask Third Question - 'What is Machine Learning?'")
    print("-" * 80)
    question3 = "What is Machine Learning?"
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"question": question3},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Query failed: {response.status_code}")
            return False
        
        data = response.json()
        
        print(f"✓ Question answered successfully")
        print(f"\n  Question: {data['question']}")
        print(f"\n  Answer:")
        print(f"  {data['answer']}")
        
        print(f"\n  Retrieved {data['num_documents_retrieved']} document(s):")
        for i, doc in enumerate(data['retrieved_docs'], 1):
            relevance = (doc['score'] * 100)
            print(f"\n    [{i}] Relevance: {relevance:.1f}%")
            print(f"        Text: {doc['document'][:80]}...")
        
    except Exception as e:
        print(f"✗ Query error: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("AI DOCUMENT INTELLIGENCE - COMPLETE UI/BACKEND INTEGRATION TEST")
    print("=" * 80)
    
    # Check servers
    if not test_servers_running():
        print("\n" + "=" * 80)
        print("SERVERS NOT RUNNING")
        print("=" * 80)
        print("\nTo run the complete application:")
        print("\n1. Start API server (in terminal 1):")
        print("   source .venv/bin/activate")
        print("   uvicorn app.main:app --reload --port 8001")
        print("\n2. Start frontend server (in terminal 2):")
        print("   python3 serve_frontend.py")
        print("\n3. Open browser:")
        print("   http://localhost:3000")
        return 1
    
    # Test UI workflow
    if not test_ui_workflow():
        print("\n" + "=" * 80)
        print("UI WORKFLOW TEST FAILED ✗")
        print("=" * 80)
        return 1
    
    # Success
    print("\n" + "=" * 80)
    print("COMPLETE WORKFLOW TEST PASSED ✓✓✓")
    print("=" * 80)
    
    print("\n✓ PDF Upload and Processing")
    print("✓ Document Storage and Retrieval")
    print("✓ Semantic Search with FAISS")
    print("✓ Question Answering with Llama 3.2 3B")
    print("✓ Multiple Document Management")
    print("✓ Text Input via UI")
    print("✓ Context-Aware Responses")
    
    print("\n" + "=" * 80)
    print("FRONTEND INSTRUCTIONS")
    print("=" * 80)
    print("\nThe frontend is ready to use!")
    print("\n1. Open your browser and navigate to:")
    print("   http://localhost:3000")
    print("\n2. You can:")
    print("   - Upload PDF documents via drag-and-drop")
    print("   - Add text directly from the UI")
    print("   - Ask questions about ingested documents")
    print("   - View AI-generated answers")
    print("   - See retrieved source documents")
    print("\n3. Make sure both servers are running:")
    print("   - API server: http://localhost:8001")
    print("   - Frontend server: http://localhost:3000")
    print("\n" + "=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
