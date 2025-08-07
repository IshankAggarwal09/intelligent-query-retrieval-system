# test_client.py
import requests
import json
import os
import time

BASE_URL = "http://localhost:8000"

def check_server_availability():
    """Check if the server is available before running tests"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False

def test_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print("Health Check:", response.json())
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to the server")
        print("Make sure your FastAPI server is running on http://localhost:8000")
        print("Run: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_upload_document(file_path, domain="insurance"):
    """Test document upload"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'domain': domain}
            
            response = requests.post(f"{BASE_URL}/upload-document/", files=files, data=data, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ Document uploaded successfully!")
            print(f"Document ID: {result['document_id']}")
            print(f"File Size: {result.get('file_size', 'Unknown')} bytes")
            return result['document_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error during upload")
        return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def query_document_interactive(domain=None, max_results=5):
    """Interactive query function"""
    while True:
        print("\n" + "="*60)
        print("INTERACTIVE QUERY MODE")
        print("="*60)
        
        # Get user input
        query_text = input("\nEnter your query (or 'quit' to exit): ").strip()
        
        if query_text.lower() in ['quit', 'exit', 'q']:
            print("Exiting interactive mode...")
            break
        
        if not query_text:
            print("Please enter a valid query.")
            continue
        
        # Prepare query data
        query_data = {
            "query": query_text,
            "domain": domain,
            "max_results": max_results,
            "include_explanation": True
        }
        
        try:
            print(f"\n🔍 Processing query: '{query_text}'...")
            response = requests.post(f"{BASE_URL}/query/", json=query_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                display_query_result(result)
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error during query")
        except Exception as e:
            print(f"❌ Query error: {e}")

def display_query_result(result):
    """Display query results in a formatted way"""
    print("\n" + "="*50)
    print(f"QUERY: {result['query']}")
    print("="*50)
    print(f"✅ ANSWER: {result['answer']}")
    
    # Decision rationale
    rationale = result['decision_rationale']
    print(f"\n📊 CONFIDENCE: {rationale['confidence_score']:.2f}")
    print(f"🧠 REASONING: {rationale['reasoning']}")
    
    if rationale['supporting_evidence']:
        print(f"\n📋 SUPPORTING EVIDENCE:")
        for i, evidence in enumerate(rationale['supporting_evidence'], 1):
            print(f"  {i}. {evidence}")
    
    if rationale['conditions']:
        print(f"\n⚠️  CONDITIONS:")
        for i, condition in enumerate(rationale['conditions'], 1):
            print(f"  {i}. {condition}")
    
    if rationale['limitations']:
        print(f"\n⚠️  LIMITATIONS:")
        for i, limitation in enumerate(rationale['limitations'], 1):
            print(f"  {i}. {limitation}")
    
    # Retrieved chunks info
    chunks = result['retrieved_chunks']
    print(f"\n📄 RETRIEVED CHUNKS: {len(chunks)}")
    
    if chunks:
        print("\nTop relevant sections:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n--- Chunk {i} (Relevance: {chunk['relevance_score']:.3f}) ---")
            print(f"Source: {chunk['metadata'].get('filename', 'Unknown')}")
            content_preview = chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content']
            print(f"Content: {content_preview}")
    
    print(f"\n⏱️  Processing Time: {result['processing_time']:.2f} seconds")
    print("="*50)

def get_document_info(document_id):
    """Test getting document information"""
    try:
        response = requests.get(f"{BASE_URL}/document/{document_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📄 Document Info for {document_id}:")
            print(f"  📝 Filename: {result['filename']}")
            print(f"  🏷️  Domain: {result['domain']}")
            print(f"  ✅ Processed: {result['processed']}")
            print(f"  📅 Upload Time: {result['upload_timestamp']}")
            print(f"  📊 File Size: {result.get('file_size', 'Unknown')} bytes")
            return result
        else:
            print(f"❌ Failed to get document info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting document info: {e}")
        return None

def main_menu():
    """Main interactive menu"""
    print("\n" + "="*60)
    print("🏥 INTELLIGENT QUERY-RETRIEVAL SYSTEM")
    print("="*60)
    
    # Check server availability
    print("🔍 Checking server availability...")
    if not check_server_availability():
        print("❌ Server is not running or not accessible")
        print("Please ensure your FastAPI server is running:")
        print("  1. cd app")
        print("  2. uvicorn main:app --reload")
        print("  3. Wait for 'Uvicorn running on http://127.0.0.1:8000'")
        return
    
    print("✅ Server is available")
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed.")
        return
    
    while True:
        print("\n" + "-"*40)
        print("📋 MAIN MENU")
        print("-"*40)
        print("1. 📤 Upload Document")
        print("2. 🔍 Interactive Query Mode")
        print("3. 📄 Get Document Info")
        print("4. 🏥 Health Check")
        print("5. 🚪 Exit")
        print("-"*40)
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            # Upload document
            file_path = input("\nEnter file path: ").strip()
            domain = input("Enter domain (insurance/legal/hr/compliance): ").strip() or "insurance"
            
            if file_path:
                document_id = test_upload_document(file_path, domain)
                if document_id:
                    print(f"\n✅ Document uploaded with ID: {document_id}")
                    
                    # Ask if user wants to query immediately
                    query_now = input("\nDo you want to query this document now? (y/n): ").strip().lower()
                    if query_now in ['y', 'yes']:
                        query_document_interactive(domain)
            else:
                print("❌ Please provide a valid file path")
        
        elif choice == '2':
            # Interactive query mode
            domain = input("\nEnter domain filter (insurance/legal/hr/compliance or press Enter for all): ").strip()
            domain = domain if domain else None
            query_document_interactive(domain)
        
        elif choice == '3':
            # Get document info
            doc_id = input("\nEnter document ID: ").strip()
            if doc_id:
                get_document_info(doc_id)
            else:
                print("❌ Please provide a valid document ID")
        
        elif choice == '4':
            # Health check
            test_health()
        
        elif choice == '5':
            # Exit
            print("👋 Thank you for using the Intelligent Query-Retrieval System!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-5.")

def quick_test_mode():
    """Quick test with predefined queries - for development/testing"""
    print("\n🧪 QUICK TEST MODE")
    print("Testing with sample queries...")
    
    sample_queries = [
        "Does this policy cover knee surgery, and what are the conditions?",
        "What are the limitations for orthopedic procedures?", 
        "What is the annual limit for surgical procedures?",
        "Are experimental procedures covered?"
    ]
    
    for query in sample_queries:
        query_data = {
            "query": query,
            "domain": "insurance",
            "max_results": 5,
            "include_explanation": True
        }
        
        try:
            print(f"\n🔍 Testing: {query}")
            response = requests.post(f"{BASE_URL}/query/", json=query_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query successful - {len(result['retrieved_chunks'])} chunks retrieved")
                if result['retrieved_chunks']:
                    print(f"📊 Confidence: {result['decision_rationale']['confidence_score']}")
                else:
                    print("⚠️  No chunks retrieved - check document processing")
            else:
                print(f"❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🏥 Welcome to Intelligent Query-Retrieval System")
    
    # Ask user for mode
    mode = input("\nChoose mode:\n1. Interactive Mode (recommended)\n2. Quick Test Mode\nEnter choice (1/2): ").strip()
    
    if mode == '2':
        quick_test_mode()
    else:
        main_menu()
