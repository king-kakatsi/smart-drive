"""
Image processing utilities for visual description extraction
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.vector_store import get_vector_store
from app.core.ai_client import get_ai_client
from app.config import settings


class ImageProcessor:
    """Image processing and indexing using Vision LLMs"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.ai_client = get_ai_client()

    async def process_image(self, file_path: str, file_id: int, metadata: Dict[str, Any]):
        """Process an image, describe it, and add to vector store"""

        # Generate description using Vision LLM
        print(f"DEBUG: Generating visual description for {file_path}")
        description = await self.ai_client.describe_image(file_path)

        if not description:
            print(f"DEBUG: No description generated for {file_path}")
            return False

        # Add image description to vector store as a single chunk
        documents = [description]
        metadatas = [{
            **metadata,
            "chunk_id": 0,
            "total_chunks": 1,
            "file_id": file_id
        }]
        ids = [f"{file_id}_image_desc"]

        # Add to vector store
        await self.vector_store.add_documents(documents, metadatas, ids)

        # Update database status
        try:
            from app.database import async_session
            from sqlalchemy import text
            
            async with async_session() as session:
                await session.execute(
                    text("UPDATE files SET processed = 1 WHERE id = :file_id"),
                    {"file_id": file_id}
                )
                await session.commit()
                print(f"DEBUG: Image {file_id} marked as processed")
        except Exception as e:
            print(f"Error updating file status for {file_id}: {str(e)}")

        return True


# Global image processor instance
image_processor = ImageProcessor()


def get_image_processor():
    """Get the global image processor instance"""
    return image_processor
