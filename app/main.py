# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import logging
from typing import Optional
from models import QueryRequest, QueryResponse, Domain, DocumentMetadata
from services.query_service import QueryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Intelligent Query-Retrieval System",
    description="LLM-powered document processing and query system for insurance, legal, HR, and compliance domains",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
query_service = QueryService()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Intelligent Query-Retrieval System")

@app.post("/upload-document/")
async def upload_document(
    file: UploadFile = File(...),
    domain: Domain = Form(...)
):
    """Upload and process a document"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.eml', '.msg'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document
            document_id = await query_service.process_document(
                file_path=tmp_file_path,
                filename=file.filename,
                domain=domain
            )
            
            return {
                "message": "Document uploaded and processed successfully",
                "document_id": document_id,
                "filename": file.filename,
                "domain": domain
            }
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents and get intelligent responses"""
    try:
        response = await query_service.query_documents(request)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{document_id}", response_model=DocumentMetadata)
async def get_document_info(document_id: str):
    """Get document metadata"""
    try:
        metadata = await query_service.get_document_info(document_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all associated data"""
    try:
        await query_service.delete_document(document_id)
        return {"message": "Document deleted successfully", "document_id": document_id}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Intelligent Query-Retrieval System"}

# Example usage endpoint
@app.post("/example-query/")
async def example_query():
    """Demonstrate the system with a sample query"""
    sample_request = QueryRequest(
        query="Does this policy cover knee surgery, and what are the conditions?",
        domain=Domain.INSURANCE,
        max_results=5,
        include_explanation=True
    )
    
    try:
        response = await query_service.query_documents(sample_request)
        return response
    except Exception as e:
        logger.error(f"Error in example query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
