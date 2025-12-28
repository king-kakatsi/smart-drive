"""
ChromaDB vector store integration for document embeddings
Adapted from OpenAI Chroma examples
"""
import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any

from app.config import settings


class VectorStore:
    """ChromaDB vector store wrapper"""

    def __init__(self):
        self.client = None
        self.collection = None

    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        # Create persist directory if it doesn't exist
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

        # Initialize client with persistence
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="smart_drive_docs",
            metadata={"description": "Smart-Drive document embeddings"}
        )

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents to vector store"""
        if not self.collection:
            await self.initialize()

        # Generate embeddings (will use OpenAI by default in Chroma)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    async def search_documents(
        self,
        query: str,
        n_results: int = 5,
        where: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search for similar documents"""
        if not self.collection:
            await self.initialize()

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        return results

    async def delete_documents(self, ids: List[str]):
        """Delete documents from vector store"""
        if self.collection:
            self.collection.delete(ids=ids)

    async def update_document(
        self,
        document_id: str,
        document: str,
        metadata: Dict[str, Any]
    ):
        """Update a document in the vector store"""
        if self.collection:
            self.collection.update(
                ids=[document_id],
                documents=[document],
                metadatas=[metadata]
            )


# Global vector store instance
vector_store = VectorStore()


async def init_vector_store():
    """Initialize the global vector store"""
    await vector_store.initialize()


def get_vector_store():
    """Get the global vector store instance"""
    return vector_store


