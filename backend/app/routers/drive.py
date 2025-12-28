"""
Google Drive integration routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from app.dependencies import get_current_user, get_db
from app.services.google_drive_service import google_drive_service


router = APIRouter()


@router.get("/files")
async def list_drive_files(
    folder_id: str = "root",
    page_token: Optional[str] = None,
    page_size: int = 100,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List files from connected Google Drive"""
    try:
        files_data = await google_drive_service.list_files_from_drive(
            database=db,
            user_id=user.id,
            folder_id=folder_id,
            page_token=page_token,
            page_size=page_size
        )
        return files_data
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Drive files: {str(error)}"
        )


@router.get("/files/{file_id}")
async def get_drive_file_metadata(
    file_id: str,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metadata for specific Drive file"""
    try:
        metadata = await google_drive_service.get_file_metadata_from_drive(
            database=db,
            user_id=user.id,
            file_id=file_id
        )
        return metadata
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file metadata: {str(error)}"
        )


@router.get("/files/{file_id}/download")
async def download_drive_file(
    file_id: str,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download file content from Drive"""
    from fastapi.responses import Response
    
    try:
        file_content = await google_drive_service.download_file_content_from_drive(
            database=db,
            user_id=user.id,
            file_id=file_id
        )
        
        # Get file metadata for proper content type
        metadata = await google_drive_service.get_file_metadata_from_drive(
            database=db,
            user_id=user.id,
            file_id=file_id
        )
        
        return Response(
            content=file_content,
            media_type=metadata.get("mimeType", "application/octet-stream"),
            headers={"Content-Disposition": f'attachment; filename="{metadata.get("name", "file")}"'}
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(error)}"
        )


@router.get("/search")
async def search_drive_files(
    query: str,
    page_size: int = 50,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search files in Google Drive"""
    try:
        files = await google_drive_service.search_files_in_drive(
            database=db,
            user_id=user.id,
            search_query=query,
            page_size=page_size
        )
        return {"files": files, "query": query}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search files: {str(error)}"
        )


@router.post("/sync")
async def sync_drive_files(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync files from Google Drive to local storage"""
    try:
        # List all files from Drive
        files_data = await google_drive_service.list_files_from_drive(
            database=db,
            user_id=user.id,
            folder_id="root",
            page_size=100
        )
        
        files = files_data.get("files", [])
        synced_count = 0
        
        # TODO: Implement actual sync logic
        # For now, just return the count of files found
        synced_count = len(files)
        
        return {
            "message": f"Found {synced_count} files in Drive",
            "synced_count": synced_count,
            "files_preview": files[:5]  # Return first 5 files as preview
        }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drive sync failed: {str(error)}"
        )


@router.get("/connect")
async def connect_drive():
    """Get Google Drive connection URL"""
    from app.core.drive_client import get_google_auth_url
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url, "message": "Redirect user to this URL to connect Google Drive"}


