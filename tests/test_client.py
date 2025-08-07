# test_client.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_upload_document():
    """Test document upload"""
    files = {'file': open('sample_policy.pdf', 'rb')}
    data = {'domain': 'insurance'}
    
    response = requests.post(f"{BASE_URL}/upload-document/", files=files, data=data)
    return response.json()

def test_query():
    """Test query processing"""
    query_data = {
        "query": "Does this policy cover knee surgery, and what are the conditions?",
        "domain": "insurance",
        "max_results": 5,
        "include_explanation": True
    }
    
    response = requests.post(f"{BASE_URL}/query/", json=query_data)
    return response.json()

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

if __name__ == "__main__":
    # Test health
    print("Health check:", test_health())
    
    # Test query (assuming documents are already uploaded)
    print("\nQuery test:")
    query_result = test_query()
    print(json.dumps(query_result, indent=2, default=str))
