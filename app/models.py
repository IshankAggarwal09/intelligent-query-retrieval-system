# models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    EMAIL = "email"

class Domain(str, Enum):
    INSURANCE = "insurance"
    LEGAL = "legal"
    HR = "hr"
    COMPLIANCE = "compliance"

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    document_type: DocumentType
    domain: Domain
    upload_timestamp: datetime
    file_size: int
    page_count: Optional[int] = None
    processed: bool = False

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any]
    embedding_id: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    domain: Optional[Domain] = None
    document_ids: Optional[List[str]] = None
    max_results: int = Field(default=5, ge=1, le=20)
    include_explanation: bool = True

class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    relevance_score: float
    metadata: Dict[str, Any]

class DecisionRationale(BaseModel):
    reasoning: str
    confidence_score: float
    supporting_evidence: List[str]
    conditions: List[str]
    limitations: List[str]

class QueryResponse(BaseModel):
    query: str
    answer: str
    decision_rationale: DecisionRationale
    retrieved_chunks: List[RetrievalResult]
    processing_time: float
    timestamp: datetime
