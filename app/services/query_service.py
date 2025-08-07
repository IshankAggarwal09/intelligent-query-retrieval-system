# query_service.py
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from models import QueryRequest, QueryResponse, DocumentMetadata, DocumentChunk, Domain, DecisionRationale
from .document_processor import DocumentProcessor
from .embedding_service import EmbeddingService
from .vector_db_service import VectorDBService
from .mongodb_service import MongoDBService
from .llm_service import LLMService

class QueryService:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDBService()
        self.mongodb = MongoDBService()
        self.llm_service = LLMService()
        self.logger = logging.getLogger(__name__)
    
    async def process_document(self, 
                             file_path: str, 
                             filename: str, 
                             domain: Domain) -> str:
        """Process and store a document"""
        start_time = time.time()
        
        try:
            # Generate document ID
            document_id = hashlib.md5(f"{filename}_{time.time()}".encode()).hexdigest()
            
            # Determine file type
            file_extension = filename.lower().split('.')[-1]
            document_type = file_extension
            
            # Extract text based on file type
            if file_extension == 'pdf':
                extraction_result = await self.document_processor.process_pdf(file_path)
            elif file_extension == 'docx':
                extraction_result = await self.document_processor.process_docx(file_path)
            elif file_extension in ['eml', 'msg']:
                extraction_result = await self.document_processor.process_email(file_path)
                document_type = 'email'
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Create document metadata
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                document_type=document_type,
                domain=domain,
                upload_timestamp=datetime.utcnow(),
                file_size=0,  # You would get this from the actual file
                page_count=extraction_result.get("page_count"),
                processed=False
            )
            
            # Store metadata
            await self.mongodb.store_document_metadata(metadata)
            
            # Create chunks
            chunks = await self.document_processor.create_chunks(
                extraction_result["text"], 
                document_id, 
                extraction_result["metadata"]
            )
            
            # Create embeddings
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.create_embeddings(chunk_texts)
            
            # Store in vector database
            await self.vector_db.upsert_embeddings(chunks, embeddings)
            
            # Store chunks in MongoDB
            await self.mongodb.store_document_chunks(chunks)
            
            # Update processing status
            await self.mongodb.update_document_processed_status(document_id, True)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Document processed successfully in {processing_time:.2f}s: {document_id}")
            
            return document_id
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            # Clean up on error
            try:
                await self.mongodb.delete_document(document_id)
                await self.vector_db.delete_document_embeddings(document_id)
            except:
                pass
            raise
    
    async def query_documents(self, request: QueryRequest) -> QueryResponse:
        """Process a query and return results with decision rationale"""
        start_time = time.time()
        
        try:
            # Create query embedding
            query_embedding = await self.embedding_service.create_query_embedding(request.query)
            
            # Prepare filters for vector search
            filter_dict = {}
            if request.domain:
                filter_dict["domain"] = request.domain.value
            if request.document_ids:
                filter_dict["document_id"] = {"$in": request.document_ids}
            
            # Perform similarity search
            retrieved_chunks = await self.vector_db.similarity_search(
                query_embedding=query_embedding,
                top_k=request.max_results,
                filter_dict=filter_dict if filter_dict else None
            )
            
            # Analyze with LLM if explanation is requested
            if request.include_explanation and retrieved_chunks:
                llm_analysis = await self.llm_service.analyze_query_and_context(
                    query=request.query,
                    retrieved_chunks=retrieved_chunks,
                    domain=request.domain.value if request.domain else None
                )
                
                answer = llm_analysis["answer"]
                decision_rationale = llm_analysis["decision_rationale"]
            else:
                answer = "Query processed. Retrieved relevant document chunks."
                decision_rationale = DecisionRationale(
                    reasoning="Basic retrieval without LLM analysis",
                    confidence_score=0.0,
                    supporting_evidence=[],
                    conditions=[],
                    limitations=[]
                )
            
            processing_time = time.time() - start_time
            
            # Create response
            response = QueryResponse(
                query=request.query,
                answer=answer,
                decision_rationale=decision_rationale,
                retrieved_chunks=retrieved_chunks,
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
            
            # Log query for analytics
            await self.mongodb.log_query({
                "query": request.query,
                "domain": request.domain.value if request.domain else None,
                "num_results": len(retrieved_chunks),
                "processing_time": processing_time
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise
    
    async def get_document_info(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata"""
        return await self.mongodb.get_document_metadata(document_id)
    
    async def delete_document(self, document_id: str):
        """Delete document and all associated data"""
        try:
            await self.mongodb.delete_document(document_id)
            await self.vector_db.delete_document_embeddings(document_id)
            self.logger.info(f"Document deleted: {document_id}")
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            raise
