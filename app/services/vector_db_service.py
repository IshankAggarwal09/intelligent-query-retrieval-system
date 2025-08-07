# services/vector_db_service.py
from pinecone import Pinecone, ServerlessSpec  # Updated import
from typing import List, Dict, Any, Tuple
import logging
from ..config import settings
from ..models import DocumentChunk, RetrievalResult

class VectorDBService:
    def __init__(self):
        # New initialization method
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.PINECONE_DIMENSION
        self.logger = logging.getLogger(__name__)
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            # Check if index exists using new method
            if self.index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'  # Change to your preferred region
                    )
                )
                self.logger.info(f"Created Pinecone index: {self.index_name}")
        except Exception as e:
            self.logger.error(f"Error ensuring index exists: {str(e)}")
            raise
    
    async def upsert_embeddings(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """Store embeddings in Pinecone"""
        try:
            vectors = []
            for chunk, embedding in zip(chunks, embeddings):
                vector_data = {
                    "id": chunk.chunk_id,
                    "values": embedding,
                    "metadata": {
                        "document_id": chunk.document_id,
                        "content": chunk.content[:1000],  # Truncate for metadata
                        "chunk_index": chunk.chunk_index,
                        **chunk.metadata
                    }
                }
                vectors.append(vector_data)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            self.logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            self.logger.error(f"Error upserting embeddings: {str(e)}")
            raise
    
    async def similarity_search(self, 
                              query_embedding: List[float], 
                              top_k: int = 5, 
                              filter_dict: Dict[str, Any] = None) -> List[RetrievalResult]:
        """Perform similarity search in Pinecone"""
        try:
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            results = []
            for match in query_response.matches:
                result = RetrievalResult(
                    chunk_id=match.id,
                    document_id=match.metadata.get("document_id"),
                    content=match.metadata.get("content"),
                    relevance_score=float(match.score),
                    metadata=match.metadata
                )
                results.append(result)
            
            return results
        except Exception as e:
            self.logger.error(f"Error performing similarity search: {str(e)}")
            raise
    
    async def delete_document_embeddings(self, document_id: str):
        """Delete all embeddings for a specific document"""
        try:
            self.index.delete(filter={"document_id": document_id})
            self.logger.info(f"Deleted embeddings for document: {document_id}")
        except Exception as e:
            self.logger.error(f"Error deleting document embeddings: {str(e)}")
            raise
