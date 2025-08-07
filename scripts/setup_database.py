#!/usr/bin/env python3
"""
Database setup script for Intelligent Query System
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.mongodb_service import MongoDBService
from app.services.vector_db_service import VectorDBService

async def setup_databases():
    """Setup MongoDB and Pinecone databases"""
    print("Setting up databases...")
    
    # Initialize services
    mongodb_service = MongoDBService()
    vector_db_service = VectorDBService()
    
    print("✓ Databases initialized successfully")

if __name__ == "__main__":
    asyncio.run(setup_databases())
