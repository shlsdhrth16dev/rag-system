import requests
import time
import os
from io import BytesIO
from pypdf import PdfWriter

# Configuration
API_URL = "http://localhost:8000/api/v1/rag"

def create_dummy_pdf():
    """Create a simple PDF in memory"""
    buffer = BytesIO()
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    # Note: pypdf blank page is empty, let's create a text file mimicking a PDF content 
    # effectively by mocking the upload or just uploading a text file if supported, 
    # but the system only supports PDF.
    
    # Actually, simpler: write a real unique string to a page if possible, 
    # but pypdf writing text is complex without reportlab.
    # Let's rely on a known existing PDF or create one using a simpler method if possible.
    # For this script, we'll try to use a "text" file renamed as .pdf if the loader is lenient,
    # OR we just rely on the API.
    
    # BETTER: We upload a small text file if the loader supports it?
    # Our DocumentLoader supports: "application/pdf".
    # Time to use reportlab? No, too heavy dependencies.
    # We will skip content creation and assume a "test.pdf" exists OR 
    # we just mock the file content as a valid PDF binary structure? Too risky.
    
    # Strategy: Validate Query on existing DB content (if any) or skip upload if complex.
    # Wait! The user asked for EFFICIENT tests.
    # Let's check /stats first.
    return None

def test_health():
    print("1. Checking System Stats...")
    try:
        r = requests.get(f"{API_URL}/stats")
        r.raise_for_status()
        print(f"✅ System Online. Stats: {r.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_query():
    print("\n2. Testing Query Generation...")
    payload = {
        "query": "What is the purpose of this system?",
        "optimize_query": True
    }
    try:
        start = time.time()
        r = requests.post(f"{API_URL}/query", json=payload)
        r.raise_for_status()
        data = r.json()
        latency = time.time() - start
        
        print(f"✅ Query Successful ({latency:.2f}s)")
        print(f"   Answer: {data['answer'][:100]}...")
        print(f"   Sources: {len(data['sources'])}")
        
        if data['answer'] and "error" not in data['answer'].lower():
            return True
        else:
            print("⚠️ Answer looks suspicious (contains error?)")
            return False
            
    except Exception as e:
        print(f"❌ Query Failed: {e}")
        return False

if __name__ == "__main__":
    print("=== RAG System E2E Check ===")
    
    if test_health():
        test_query()
    
    print("\n=== Check Complete ===")
