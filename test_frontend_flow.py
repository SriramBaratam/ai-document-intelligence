#!/usr/bin/env python3
"""
Complete frontend flow test - simulates the exact workflow
"""

import requests
import json
import time
import os
from pathlib import Path

API_URL = 'http://localhost:8001'
FRONTEND_URL = 'http://localhost:3000'

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_api_health():
    """Test 1: Check if API is running"""
    print_section("TEST 1: API Health Check")
    try:
        response = requests.get(f'{API_URL}/health', timeout=5)
        if response.ok:
            data = response.json()
            print(f"✅ API is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Documents ingested: {data.get('documents_ingested')}")
            return True
        else:
            print(f"❌ API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_frontend_server():
    """Test 2: Check if frontend server is running"""
    print_section("TEST 2: Frontend Server Check")
    try:
        response = requests.get(f'{FRONTEND_URL}/index.html', timeout=5)
        if response.ok and 'AI Document Intelligence' in response.text:
            print(f"✅ Frontend server is running")
            print(f"   HTML loaded successfully (contains title)")
            return True
        else:
            print(f"❌ Frontend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to frontend: {e}")
        return False

def test_pdf_upload():
    """Test 3: Upload PDF (simulating frontend POST /ingest/pdf)"""
    print_section("TEST 3: PDF Upload Flow")
    
    pdf_path = Path('/Users/baratamsriram/Downloads/ai-document-intelligence/data/test.pdf')
    
    if not pdf_path.exists():
        print(f"❌ Test PDF not found at {pdf_path}")
        return False
    
    print(f"📄 Uploading PDF: {pdf_path.name}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            response = requests.post(f'{API_URL}/ingest/pdf', files=files, timeout=30)
        
        if response.ok:
            data = response.json()
            print(f"✅ PDF uploaded successfully!")
            print(f"   Chunks created: {data.get('chunks_created')}")
            print(f"   Total characters: {data.get('total_characters')}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading PDF: {e}")
        return False

def test_query_flow():
    """Test 4: Query the document (simulating frontend POST /query)"""
    print_section("TEST 4: Query Flow")
    
    questions = [
        "What is Artificial Intelligence?",
        "What is Machine Learning?",
        "What is Deep Learning?"
    ]
    
    for question in questions:
        print(f"❓ Asking: {question}")
        
        try:
            response = requests.post(
                f'{API_URL}/query',
                json={'question': question},
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.ok:
                data = response.json()
                print(f"✅ Query successful!")
                print(f"   Answer: {data.get('answer')[:100]}...")
                print(f"   Retrieved documents: {len(data.get('retrieved_docs', []))}")
                
                # Print retrieved docs
                for i, doc in enumerate(data.get('retrieved_docs', []), 1):
                    score = (doc.get('score', 0) * 100)
                    print(f"   📚 Source {i}: {doc.get('document')[:60]}... (Relevance: {score:.1f}%)")
                
                return True
            else:
                print(f"❌ Query failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error querying: {e}")
            return False
        
        time.sleep(1)  # Add delay between queries
    
    return True

def test_text_input_flow():
    """Test 5: Add text directly (simulating frontend POST /ingest/text)"""
    print_section("TEST 5: Text Input Flow")
    
    text = "Artificial Intelligence (AI) is a rapidly growing field that enables computers to learn and perform tasks that typically require human intelligence."
    
    print(f"📝 Adding text: {text[:50]}...")
    
    try:
        response = requests.post(
            f'{API_URL}/ingest/text',
            json={'text': text, 'source': 'frontend_test'},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.ok:
            data = response.json()
            print(f"✅ Text added successfully!")
            print(f"   Chunks created: {data.get('chunks_created')}")
            return True
        else:
            print(f"❌ Text ingestion failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error adding text: {e}")
        return False

def test_complete_workflow():
    """Test 6: Complete workflow - upload → query → verify"""
    print_section("TEST 6: Complete Frontend Workflow")
    
    print("STEP 1️⃣: Upload PDF")
    pdf_path = Path('/Users/baratamsriram/Downloads/ai-document-intelligence/data/test.pdf')
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            response = requests.post(f'{API_URL}/ingest/pdf', files=files, timeout=30)
        
        if not response.ok:
            print(f"❌ PDF upload failed")
            return False
        
        data = response.json()
        print(f"✅ PDF uploaded: {data.get('chunks_created')} chunks")
        
    except Exception as e:
        print(f"❌ Error in step 1: {e}")
        return False
    
    time.sleep(1)
    
    print("\nSTEP 2️⃣: Verify document is stored")
    try:
        response = requests.get(f'{API_URL}/health', timeout=5)
        data = response.json()
        if data.get('documents_ingested'):
            print(f"✅ Documents verified as ingested")
        else:
            print(f"⚠️  Documents not ingested in health check")
    except Exception as e:
        print(f"❌ Error checking health: {e}")
    
    print("\nSTEP 3️⃣: Ask first question")
    try:
        response = requests.post(
            f'{API_URL}/query',
            json={'question': 'What is Artificial Intelligence?'},
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if not response.ok:
            print(f"❌ Query failed")
            return False
        
        data = response.json()
        answer = data.get('answer', '')
        docs_count = len(data.get('retrieved_docs', []))
        
        print(f"✅ Question answered")
        print(f"   Answer: {answer[:80]}...")
        print(f"   Retrieved sources: {docs_count}")
        
    except Exception as e:
        print(f"❌ Error in step 3: {e}")
        return False
    
    time.sleep(1)
    
    print("\nSTEP 4️⃣: Add supplementary text")
    try:
        response = requests.post(
            f'{API_URL}/ingest/text',
            json={'text': 'Machine Learning is a subset of AI', 'source': 'workflow_test'},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if not response.ok:
            print(f"❌ Text ingestion failed")
            return False
        
        data = response.json()
        print(f"✅ Text added: {data.get('chunks_created')} chunks")
        
    except Exception as e:
        print(f"❌ Error in step 4: {e}")
        return False
    
    time.sleep(1)
    
    print("\nSTEP 5️⃣: Ask second question (multi-document search)")
    try:
        response = requests.post(
            f'{API_URL}/query',
            json={'question': 'What is Machine Learning?'},
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if not response.ok:
            print(f"❌ Query failed")
            return False
        
        data = response.json()
        answer = data.get('answer', '')
        docs_count = len(data.get('retrieved_docs', []))
        
        print(f"✅ Question answered")
        print(f"   Answer: {answer[:80]}...")
        print(f"   Retrieved sources: {docs_count}")
        
        if docs_count >= 1:
            print(f"✅ Multi-document search working!")
        
    except Exception as e:
        print(f"❌ Error in step 5: {e}")
        return False
    
    print("\n" + "="*80)
    print("  ✅ COMPLETE WORKFLOW TEST PASSED")
    print("="*80 + "\n")
    
    return True

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  FRONTEND FLOW TEST - Complete Workflow Verification".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run all tests
    results = {
        'API Health': test_api_health(),
        'Frontend Server': test_frontend_server(),
        'PDF Upload': test_pdf_upload(),
        'Query Flow': test_query_flow(),
        'Text Input': test_text_input_flow(),
        'Complete Workflow': test_complete_workflow(),
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Frontend flow is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
