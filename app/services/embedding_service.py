# embedding_service.py
import google.generativeai as genai
from typing import List, Dict, Any
import numpy as np
import logging
from ..config import settings

class EmbeddingService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.logger = logging.getLogger(__name__)
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts using Gemini"""
        try:
            embeddings = []
            
            for text in texts:
                # Clean and truncate text if necessary
                cleaned_text = self._clean_text(text)
                
                result = genai.embed_content(
                    model=self.model,
                    content=cleaned_text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            
            return embeddings
        except Exception as e:
            self.logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    async def create_query_embedding(self, query: str) -> List[float]:
        """Create embedding for a query"""
        try:
            cleaned_query = self._clean_text(query)
            
            result = genai.embed_content(
                model=self.model,
                content=cleaned_query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            self.logger.error(f"Error creating query embedding: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (Gemini has token limits)
        max_chars = 30000  # Conservative limit
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
