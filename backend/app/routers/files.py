"""
File management routes for upload, download, and organization
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import shutil
import uuid

from app.dependencies import get_db, get_optional_user
from app.config import settings
from app.services.file_service import (
    save_file_metadata,
    get_user_files,
    delete_file_record,
    create_folder,
    move_file
)
from app.models.file import FileResponse, FolderCreate


router = APIRouter()


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder_path: str = "/",
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to the system"""

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed"
        )

    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )

    # Generate unique filename
    unique_id = str(uuid.uuid4())
    safe_filename = f"{unique_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Determine file type
    file_type = "document"  # default
    if file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
        file_type = "video"
    elif file_ext in [".mp3", ".wav", ".flac"]:
        file_type = "audio"
    elif file_ext in [".jpg", ".jpeg", ".png", ".gif"]:
        file_type = "image"

    # Save metadata to database
    file_record = await save_file_metadata(
        filename=safe_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(file_content),
        mime_type=file.content_type,
        file_type=file_type,
        user_id=user.id if user else None,
        folder_path=folder_path,
        db=db
    )

    return FileResponse(
        id=file_record.id,
        filename=file_record.filename,
        original_filename=file_record.original_filename,
        file_path=file_record.file_path,
        file_size=file_record.file_size,
        mime_type=file_record.mime_type,
        file_type=file_record.file_type,
        folder_path=file_record.folder_path,
        processed=file_record.processed,
        created_at=file_record.created_at
    )


@router.get("/", response_model=List[FileResponse])
async def list_files(
    folder_path: str = "/",
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """List files in a folder"""
    files = await get_user_files(user.id if user else None, folder_path, db)
    return files


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    success = await delete_file_record(file_id, user.id if user else None, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied"
        )
    return {"message": "File deleted successfully"}


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a file"""
    # Get file record
    file_record = await get_file_by_id(file_id, user.id if user else None, db)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Return file
    return FileResponse(
        media_type=file_record.mime_type,
        filename=file_record.original_filename,
        path=file_record.file_path
    )


@router.post("/folders")
async def create_folder_endpoint(
    folder: FolderCreate,
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder"""
    success = await create_folder(
        folder.name,
        folder.parent_path,
        user.id if user else None,
        db
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create folder"
        )
    return {"message": "Folder created successfully"}


@router.put("/{file_id}/move")
async def move_file_endpoint(
    file_id: int,
    new_path: str,
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Move a file to a different folder"""
    success = await move_file(file_id, new_path, user.id if user else None, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to move file"
        )
    return {"message": "File moved successfully"}


