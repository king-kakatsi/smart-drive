"""
Document processing utilities for text extraction and chunking
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.vector_store import get_vector_store
from app.config import settings


class DocumentProcessor:
    """Document processing and indexing"""

    def __init__(self):
        self.vector_store = get_vector_store()

    async def process_file(self, file_path: str, file_id: int, metadata: Dict[str, Any]):
        """Process a file and add to vector store"""

        # Extract text based on file type
        text_content = await self._extract_text(file_path)

        if not text_content:
            return False

        # Chunk the text
        chunks = self._chunk_text(text_content)

        # Prepare documents for vector store
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                **metadata,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "file_id": file_id
            })
            ids.append(f"{file_id}_chunk_{i}")

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
        except Exception as e:
            print(f"Error updating file status for {file_id}: {str(e)}")

        return True

    async def _extract_text(self, file_path: str) -> Optional[str]:
        """Extract text from different file types"""

        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext == '.pdf':
                return await self._extract_pdf_text(file_path)
            elif file_ext in ['.docx', '.doc']:
                return await self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                return await self._extract_txt_text(file_path)
            else:
                # For unsupported formats, return filename only
                return f"File: {Path(file_path).name}"
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None

    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            text = ""

            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()
        except ImportError:
            return f"PDF extraction not available: {Path(file_path).name}"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            from docx import Document

            doc = Document(file_path)
            text = ""

            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()
        except ImportError:
            return f"DOCX extraction not available: {Path(file_path).name}"
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            return f"Error reading TXT: {str(e)}"

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chunk text into smaller pieces with overlap"""

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Find a good breaking point (sentence end)
            if end < len(text):
                # Look for sentence endings within the last 100 chars
                search_end = min(end + 100, len(text))
                last_period = text.rfind('.', end, search_end)
                last_newline = text.rfind('\n', end, search_end)

                break_point = max(last_period, last_newline)
                if break_point > end - 100:  # If we found a good break point
                    end = break_point + 1

            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

            # Move start position with overlap
            start = end - overlap

            # Ensure we don't get stuck
            if start >= len(text):
                break
            elif start <= 0:
                start = end

        return chunks if chunks else [text]


# Global document processor instance
document_processor = DocumentProcessor()


def get_document_processor():
    """Get the global document processor instance"""
    return document_processor


