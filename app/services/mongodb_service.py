# mongodb_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from config import settings
from models import DocumentMetadata, DocumentChunk

class MongoDBService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DATABASE]
        self.documents_collection = self.db.documents
        self.chunks_collection = self.db.chunks
        self.queries_collection = self.db.queries
        self.logger = logging.getLogger(__name__)
    
    async def store_document_metadata(self, metadata: DocumentMetadata) -> str:
        """Store document metadata"""
        try:
            document_dict = metadata.dict()
            result = await self.documents_collection.insert_one(document_dict)
            self.logger.info(f"Stored document metadata: {metadata.document_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error storing document metadata: {str(e)}")
            raise
    
    async def store_document_chunks(self, chunks: List[DocumentChunk]):
        """Store document chunks"""
        try:
            chunks_dict = [chunk.dict() for chunk in chunks]
            await self.chunks_collection.insert_many(chunks_dict)
            self.logger.info(f"Stored {len(chunks)} chunks")
        except Exception as e:
            self.logger.error(f"Error storing document chunks: {str(e)}")
            raise
    
    async def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieve document metadata"""
        try:
            doc = await self.documents_collection.find_one({"document_id": document_id})
            if doc:
                doc.pop("_id", None)
                return DocumentMetadata(**doc)
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving document metadata: {str(e)}")
            raise
    
    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Retrieve all chunks for a document"""
        try:
            cursor = self.chunks_collection.find({"document_id": document_id})
            chunks = []
            async for doc in cursor:
                doc.pop("_id", None)
                chunks.append(DocumentChunk(**doc))
            return chunks
        except Exception as e:
            self.logger.error(f"Error retrieving document chunks: {str(e)}")
            raise
    
    async def update_document_processed_status(self, document_id: str, processed: bool):
        """Update document processing status"""
        try:
            await self.documents_collection.update_one(
                {"document_id": document_id},
                {"$set": {"processed": processed}}
            )
        except Exception as e:
            self.logger.error(f"Error updating document status: {str(e)}")
            raise
    
    async def log_query(self, query_data: Dict[str, Any]):
        """Log query for analytics"""
        try:
            query_data["timestamp"] = datetime.utcnow()
            await self.queries_collection.insert_one(query_data)
        except Exception as e:
            self.logger.error(f"Error logging query: {str(e)}")
            # Don't raise - logging shouldn't break the main flow
    
    async def delete_document(self, document_id: str):
        """Delete document and all associated chunks"""
        try:
            await self.documents_collection.delete_one({"document_id": document_id})
            await self.chunks_collection.delete_many({"document_id": document_id})
            self.logger.info(f"Deleted document and chunks: {document_id}")
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            raise
