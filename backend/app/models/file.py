"""
File models for upload and management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileResponse(BaseModel):
    """File response model"""
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    file_type: str  # 'document', 'video', 'audio', 'image'
    folder_path: str = "/"
    drive_file_id: Optional[str] = None
    processed: bool = False
    transcription_path: Optional[str] = None
    created_at: datetime


class FolderCreate(BaseModel):
    """Folder creation model"""
    name: str
    parent_path: str = "/"


class FileUploadResponse(BaseModel):
    """File upload response"""
    file: FileResponse
    upload_url: str
    processing_status: str = "pending"


