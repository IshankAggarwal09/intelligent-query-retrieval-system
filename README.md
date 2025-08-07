# Intelligent Query-Retrieval System

LLM-powered document processing and query system for insurance, legal, HR, and compliance domains.

## Features
- Document processing (PDF, DOCX, Email)
- Semantic search with Pinecone
- LLM analysis with Gemini 2.5 Flash
- Explainable AI decisions
- Domain-specific expertise

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env`
4. Run: `uvicorn app.main:app --reload`

## API Endpoints
- POST `/upload-document/` - Upload documents
- POST `/query/` - Query documents
- GET `/document/{id}` - Get document info
- DELETE `/document/{id}` - Delete document

## Environment Variables
See `.env.example` for required configuration.
