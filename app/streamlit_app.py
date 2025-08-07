# streamlit_app.py
import streamlit as st
import requests
import json
import time
from datetime import datetime
import os

# Configuration
BASE_URL = "http://localhost:8001"  # Your live website URL
LOCAL_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="🏥 Intelligent Query-Retrieval System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    border-bottom: 3px solid #1f77b4;
    padding-bottom: 1rem;
}
.section-header {
    font-size: 1.5rem;
    color: #2e8b57;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.info-box {
    background-color: #f0f8ff;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}
.success-box {
    background-color: #f0fff0;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #32cd32;
    margin: 1rem 0;
}
.error-box {
    background-color: #ffe4e1;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #ff6347;
    margin: 1rem 0;
}
.stAlert {
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = []
if 'current_url' not in st.session_state:
    st.session_state.current_url = BASE_URL

def check_server_availability(url):
    """Check if the server is available"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_health(url):
    """Test server health"""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error: Cannot connect to the server"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def upload_document(file, domain, url):
    """Upload document to the system"""
    try:
        files = {'file': file}
        data = {'domain': domain}
        
        with st.spinner('Uploading document...'):
            response = requests.post(f"{url}/upload-document/", files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            return False, f"Upload failed: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Upload error: {str(e)}"

def query_document(query_text, domain, max_results, include_explanation, url):
    """Query the document system"""
    try:
        query_data = {
            "query": query_text,
            "domain": domain if domain != "All" else None,
            "max_results": max_results,
            "include_explanation": include_explanation
        }
        
        with st.spinner('Processing query...'):
            response = requests.post(f"{url}/query/", json=query_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            return False, f"Query failed: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Query error: {str(e)}"

def get_document_info(document_id, url):
    """Get document information"""
    try:
        response = requests.get(f"{url}/document/{document_id}")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Failed to get document info: {response.status_code}"
    except Exception as e:
        return False, f"Error getting document info: {str(e)}"

def main():
    # Header
    st.markdown('<div class="main-header">🏥 Intelligent Query-Retrieval System</div>', unsafe_allow_html=True)
    st.markdown("*LLM-powered document processing and query system for insurance, legal, HR, and compliance domains*")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Server selection
        server_option = st.radio(
            "Select Server:",
            ["🌐 Live Server (Render)", "🏠 Local Server"],
            index=0
        )
        
        current_url = BASE_URL if server_option == "🌐 Live Server (Render)" else LOCAL_URL
        st.session_state.current_url = current_url
        
        st.markdown(f"**Current URL:** `{current_url}`")
        
        # Server status check
        st.header("🔍 Server Status")
        if st.button("Check Server Health"):
            is_healthy, health_info = test_health(current_url)
            if is_healthy:
                st.success("✅ Server is healthy!")
                st.json(health_info)
            else:
                st.error(f"❌ Server issue: {health_info}")
        
        # Quick server check on load
        is_available = check_server_availability(current_url)
        if is_available:
            st.success("🟢 Server Online")
        else:
            st.error("🔴 Server Offline")
            st.warning("Please check your server connection")

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Document", "🔍 Query Documents", "📄 Document Info", "🔗 API Endpoints"])

    # Tab 1: Upload Document
    with tab1:
        st.markdown('<div class="section-header">📤 Upload Document</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a document to upload",
                type=['pdf', 'docx', 'eml', 'msg'],
                help="Supported formats: PDF, DOCX, EML, MSG"
            )
            
            domain = st.selectbox(
                "Select Domain:",
                ["insurance", "legal", "hr", "compliance"],
                help="Choose the domain that best fits your document"
            )
        
        with col2:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("**📋 Upload Guidelines:**")
            st.markdown("• Max file size: 50MB")
            st.markdown("• Supported: PDF, DOCX, EML, MSG")
            st.markdown("• Processing time: 2-10 minutes")
            st.markdown("• Files are processed with AI")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            st.info(f"📄 Selected file: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
            
            if st.button("🚀 Upload and Process Document", type="primary"):
                success, result = upload_document(uploaded_file, domain, current_url)
                
                if success:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ Document uploaded successfully!")
                    st.markdown(f"**Document ID:** `{result['document_id']}`")
                    st.markdown(f"**Filename:** {result['filename']}")
                    st.markdown(f"**Domain:** {result.get('domain', 'N/A')}")
                    st.markdown(f"**File Size:** {result.get('file_size', 0):,} bytes")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store in session state
                    st.session_state.uploaded_documents.append({
                        'id': result['document_id'],
                        'filename': result['filename'],
                        'domain': domain,
                        'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    st.balloons()
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"❌ {result}")
                    st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Query Documents
    with tab2:
        st.markdown('<div class="section-header">🔍 Query Documents</div>', unsafe_allow_html=True)
        
        # Query input section
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query_text = st.text_area(
                "Enter your query:",
                placeholder="e.g., Does this policy cover knee surgery, and what are the conditions?",
                height=100,
                help="Ask questions about your uploaded documents"
            )
        
        with col2:
            domain_filter = st.selectbox(
                "Filter by Domain:",
                ["All", "insurance", "legal", "hr", "compliance"],
                help="Filter results by document domain"
            )
            
            max_results = st.slider(
                "Max Results:",
                min_value=1,
                max_value=10,
                value=5,
                help="Number of document chunks to retrieve"
            )
            
            include_explanation = st.checkbox(
                "Include AI Explanation",
                value=True,
                help="Get detailed AI analysis and reasoning"
            )
        
        # Sample queries
        st.markdown("**💡 Sample Queries:**")
        sample_queries = [
            "Does this policy cover knee surgery, and what are the conditions?",
            "What are the waiting periods for pre-existing conditions?", 
            "What is the annual limit for surgical procedures?",
            "Are experimental procedures covered?",
            "What documents are required for claim processing?"
        ]
        
        cols = st.columns(len(sample_queries))
        for i, sample in enumerate(sample_queries):
            with cols[i % len(cols)]:
                if st.button(f"📝 {sample[:30]}...", key=f"sample_{i}"):
                    st.session_state.sample_query = sample

        # Use sample query if selected
        if 'sample_query' in st.session_state:
            query_text = st.session_state.sample_query
            del st.session_state.sample_query
            st.rerun()
        
        # Query button
        # Query button
        if st.button("🔍 Query Documents", type="primary", disabled=not query_text.strip()):
            if query_text.strip():
                success, result = query_document(
                    query_text.strip(), 
                    domain_filter, 
                    max_results, 
                    include_explanation, 
                    current_url
                )
                
                if success:
                    # Store in chat history
                    query_index = len(st.session_state.chat_history)
                    st.session_state.chat_history.append({
                        'query': query_text,
                        'result': result,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'index': query_index  # Add index for unique keys
                    })
                    
                    # Display results with unique index
                    display_query_result(result, query_index)
                else:
                    st.error(f"❌ {result}")

        
        # Chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown('<div class="section-header">💬 Query History</div>', unsafe_allow_html=True)
            
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
                with st.expander(f"🕒 {chat['timestamp']} - {chat['query'][:50]}..."):
                    display_query_result(chat['result'])

    # Tab 3: Document Info
    with tab3:
        st.markdown('<div class="section-header">📄 Document Information</div>', unsafe_allow_html=True)
        
        # Document ID input
        document_id = st.text_input(
            "Enter Document ID:",
            placeholder="e.g., 80b72a10f36aa9bfe667722a19adb029",
            help="Get information about a specific document"
        )
        
        if st.button("🔍 Get Document Info", type="primary", disabled=not document_id.strip()):
            if document_id.strip():
                success, result = get_document_info(document_id.strip(), current_url)
                
                if success:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ Document information retrieved!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📝 Filename:** {result['filename']}")
                        st.markdown(f"**🏷️ Domain:** {result['domain']}")
                        st.markdown(f"**📊 File Size:** {result.get('file_size', 'Unknown'):,} bytes")
                    
                    with col2:
                        st.markdown(f"**✅ Processed:** {'Yes' if result['processed'] else 'No'}")
                        st.markdown(f"**📅 Upload Time:** {result['upload_timestamp']}")
                        st.markdown(f"**📄 Pages:** {result.get('page_count', 'Unknown')}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ {result}")
        
        # Show uploaded documents from session
        if st.session_state.uploaded_documents:
            st.markdown("---")
            st.markdown("**📚 Recently Uploaded Documents:**")
            
            for doc in st.session_state.uploaded_documents:
                with st.expander(f"📄 {doc['filename']} - {doc['domain']}"):
                    st.markdown(f"**Document ID:** `{doc['id']}`")
                    st.markdown(f"**Domain:** {doc['domain']}")
                    st.markdown(f"**Upload Time:** {doc['upload_time']}")

    # Tab 4: API Endpoints
    with tab4:
        st.markdown('<div class="section-header">🔗 API Endpoints</div>', unsafe_allow_html=True)
        
        st.markdown(f"**Base URL:** `{current_url}`")
        
        # Main endpoints
        st.markdown("### 📋 Main Endpoints")
        endpoints = [
            ("Health Check", "GET", "/health", "Check server status"),
            ("Upload Document", "POST", "/upload-document/", "Upload and process documents"),
            ("Query Documents", "POST", "/query/", "Query processed documents"),
            ("Get Document Info", "GET", "/document/{document_id}", "Get document metadata"),
        ]
        
        for name, method, endpoint, description in endpoints:
            st.markdown(f"**{name}**")
            st.code(f"{method} {current_url}{endpoint}")
            st.markdown(f"*{description}*")
            st.markdown("---")
        
        # Webhook endpoints
        st.markdown("### 🔗 Webhook Endpoints")
        webhook_endpoints = [
            ("Document Processed", "POST", "/webhook/document-processed/"),
            ("Query Executed", "POST", "/webhook/query-executed/"),
            ("External Service", "POST", "/webhook/external/{service_name}"),
            ("Subscribe to Webhooks", "POST", "/webhooks/subscribe/"),
            ("List Available Events", "GET", "/webhooks/events/"),
            ("Test Webhooks", "POST", "/webhooks/test/{event}"),
        ]
        
        for name, method, endpoint in webhook_endpoints:
            st.markdown(f"**{name}**")
            st.code(f"{method} {current_url}{endpoint}")
        
        # API documentation link
        st.markdown("### 📖 Interactive API Documentation")
        st.markdown(f"[**Swagger UI**]({current_url}/docs) - Interactive API documentation")
        st.markdown(f"[**ReDoc**]({current_url}/redoc) - Alternative API documentation")

def display_query_result(result, query_index=None):
    """Display formatted query results with unique keys"""
    
    # Generate unique identifier for this query result
    if query_index is None:
        query_index = len(st.session_state.chat_history)
    
    # Main answer
    st.markdown("### 💡 Answer")
    st.markdown(f"**Query:** {result['query']}")
    st.info(result['answer'])
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        confidence = result['decision_rationale']['confidence_score']
        st.metric("🎯 Confidence", f"{confidence:.2f}", f"{confidence*100:.1f}%")
    with col2:
        chunks_count = len(result['retrieved_chunks'])
        st.metric("📄 Chunks Found", chunks_count)
    with col3:
        processing_time = result['processing_time']
        st.metric("⏱️ Processing Time", f"{processing_time:.2f}s")
    
    # Decision rationale
    if result['decision_rationale']['reasoning']:
        st.markdown("### 🧠 AI Reasoning")
        st.markdown(result['decision_rationale']['reasoning'])
    
    # Supporting evidence
    if result['decision_rationale']['supporting_evidence']:
        st.markdown("### 📋 Supporting Evidence")
        for i, evidence in enumerate(result['decision_rationale']['supporting_evidence'], 1):
            st.markdown(f"{i}. {evidence}")
    
    # Conditions and limitations
    col1, col2 = st.columns(2)
    with col1:
        if result['decision_rationale']['conditions']:
            st.markdown("### ⚠️ Conditions")
            for condition in result['decision_rationale']['conditions']:
                st.warning(condition)
    
    with col2:
        if result['decision_rationale']['limitations']:
            st.markdown("### ⚠️ Limitations")
            for limitation in result['decision_rationale']['limitations']:
                st.warning(limitation)
    
    # Retrieved chunks - WITH UNIQUE KEYS
    if result['retrieved_chunks']:
        st.markdown("### 📄 Source Documents")
        
        for i, chunk in enumerate(result['retrieved_chunks'][:3], 1):
            with st.expander(f"Source {i} - Relevance: {chunk['relevance_score']:.3f}"):
                st.markdown(f"**Filename:** {chunk['metadata'].get('filename', 'Unknown')}")
                st.markdown(f"**Relevance Score:** {chunk['relevance_score']:.3f}")
                st.markdown("**Content:**")
                st.text_area(
                    "Content",
                    chunk['content'], 
                    height=150,
                    key=f"chunk_content_{query_index}_{i}",  # ✅ Now unique per query
                    label_visibility="collapsed"
                )

if __name__ == "__main__":
    main()
