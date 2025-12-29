"""
Google Drive integration routes
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from app.dependencies import get_current_user, get_db
from app.services.google_drive_service import google_drive_service
from app.services.google_token_service import get_valid_access_token_for_user
from app.services.file_service import save_file_metadata
from app.core.document_processor import get_document_processor
from app.core.video_processor import get_video_processor
from app.config import settings


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


@router.post("/upload")
async def upload_file_to_drive(
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload file to user's Google Drive"""
    from fastapi.responses import JSONResponse
    from googleapiclient.http import MediaIoBaseUpload
    import io

    try:
        print(f"DEBUG: Received Drive upload request for file: {file.filename}")
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.mp4', '.avi', '.mov', '.mp3', '.jpg', '.jpeg', '.png', '.gif']
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed"
            )

        # Validate file size (100MB limit)
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )

        # Get Drive service
        access_token = await get_valid_access_token_for_user(db, user.id)
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google Drive access not configured"
            )

        # Prepare file metadata
        file_metadata = {
            'name': file.filename,
            'mimeType': file.content_type or 'application/octet-stream'
        }

        if folder_id:
            file_metadata['parents'] = [folder_id]

        print(f"DEBUG: Using access token (first 10 chars): {access_token[:10]}...")
        print(f"DEBUG: File metadata: {file_metadata}")
        
        # Determine file type
        file_type = "document"  # default
        if file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
            file_type = "video"
        elif file_ext in [".mp3", ".wav", ".flac"]:
            file_type = "audio"
        elif file_ext in [".jpg", ".jpeg", ".png", ".gif"]:
            file_type = "image"

        # Upload to Drive using the service
        drive_file = await google_drive_service.upload_file_to_drive(
            database=db,
            user_id=user.id,
            file_metadata=file_metadata,
            file_content=file_content,
            mime_type=file.content_type
        )

        # Save metadata and file copy for indexing
        drive_cache_dir = os.path.join(settings.UPLOAD_DIR, "drive")
        os.makedirs(drive_cache_dir, exist_ok=True)
        
        local_path = os.path.join(drive_cache_dir, f"{drive_file['id']}_{file.filename}")
        with open(local_path, "wb") as f:
            f.write(file_content)

        file_record = await save_file_metadata(
            filename=f"{drive_file['id']}_{file.filename}",
            original_filename=file.filename,
            file_path=local_path,
            file_size=len(file_content),
            mime_type=file.content_type,
            file_type=file_type,
            user_id=user.id,
            folder_path="/", # Default for drive files for now
            db=db,
            drive_file_id=drive_file['id']
        )

        # Trigger indexing
        index_metadata = {
            "filename": file.filename,
            "mime_type": file.content_type,
            "file_type": file_type,
            "user_id": user.id,
            "drive_file_id": drive_file['id']
        }

        if file_type == "document":
            doc_processor = get_document_processor()
            background_tasks.add_task(doc_processor.process_file, local_path, file_record.id, index_metadata)
        elif file_type == "video":
            vid_processor = get_video_processor()
            background_tasks.add_task(vid_processor.process_video, local_path, file_record.id, index_metadata)

        return JSONResponse({
            "id": drive_file['id'],
            "local_id": file_record.id,
            "name": drive_file['name'],
            "mimeType": drive_file['mimeType'],
            "size": drive_file.get('size', len(file_content)),
            "webViewLink": drive_file.get('webViewLink'),
            "createdTime": drive_file.get('createdTime', 'N/A')
        })

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(error)}"
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
        # Get file metadata first to determine download approach
        metadata = await google_drive_service.get_file_metadata_from_drive(
            database=db,
            user_id=user.id,
            file_id=file_id
        )

        original_mime_type = metadata.get("mimeType", "")
        original_filename = metadata.get("name", "file")

        # Determine if this is a Google native file that will be exported
        export_mime_types = {
            "application/vnd.google-apps.document": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
            "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
            "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
            "application/vnd.google-apps.drawing": ("application/pdf", ".pdf"),
        }

        # Download the file (will auto-export Google native files)
        file_content = await google_drive_service.download_file_content_from_drive(
            database=db,
            user_id=user.id,
            file_id=file_id
        )

        # Determine final mime type and filename
        if original_mime_type in export_mime_types:
            # This was exported - use export mime type and add extension
            final_mime_type, extension = export_mime_types[original_mime_type]
            # Add extension if not already present
            if not original_filename.lower().endswith(extension.lower()):
                final_filename = original_filename + extension
            else:
                final_filename = original_filename
        else:
            # Regular file - use original metadata
            final_mime_type = original_mime_type
            final_filename = original_filename

        return Response(
            content=file_content,
            media_type=final_mime_type or "application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{final_filename}"'}
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


@router.delete("/files/{file_id}")
async def delete_drive_file(
    file_id: str,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete (trash) a file from Google Drive"""
    try:
        print(f"Deleting Drive file {file_id} for user {user.id}")
        result = await google_drive_service.delete_file_from_drive(
            database=db,
            user_id=user.id,
            file_id=file_id
        )
        print(f"Successfully deleted Drive file {file_id}")
        return {"message": "File moved to trash successfully", "deleted": result}
    except Exception as error:
        print(f"Error deleting Drive file {file_id}: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(error)}"
        )


@router.get("/metrics")
async def get_storage_metrics(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's storage and file metrics"""
    try:
        quota = await google_drive_service.get_storage_quota(db, user.id)

        # We can also fetch the file count here if we want,
        # but for now just returning the quota
        return {
            "quota": quota.get("storageQuota", {}),
            "user": quota.get("user", {})
        }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(error)}"
        )


