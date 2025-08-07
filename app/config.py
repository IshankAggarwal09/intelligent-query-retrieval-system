# config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str
    PINECONE_API_KEY: str
    MONGODB_URI: str
    
    # Pinecone Configuration
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "document-embeddings"
    PINECONE_DIMENSION: int = 768
    
    # MongoDB Configuration
    MONGODB_DATABASE: str = "intelligent_query_system"
    
    # Model Configuration
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "models/gemini-2.5-flash"
    
    # Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_TOKENS: int = 8192
    
    class Config:
        env_file = r"C:\Users\aggar\OneDrive\Desktop\intelligent-query-system\.env"

settings = Settings()
