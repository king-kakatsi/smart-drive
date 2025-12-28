"""
File service for upload, management, and organization
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Dict, Any
import os

from app.config import settings
from app.models.file import FileResponse


async def save_file_metadata(
    filename: str,
    original_filename: str,
    file_path: str,
    file_size: int,
    mime_type: str,
    file_type: str,
    user_id: Optional[int],
    folder_path: str,
    db: AsyncSession
) -> FileResponse:
    """Save file metadata to database"""

    result = await db.execute(
        text("""
            INSERT INTO files (filename, original_filename, file_path, file_size, mime_type, file_type, user_id, folder_path)
            VALUES (:filename, :original_filename, :file_path, :file_size, :mime_type, :file_type, :user_id, :folder_path)
        """),
        {
            "filename": filename,
            "original_filename": original_filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_type": file_type,
            "user_id": user_id,
            "folder_path": folder_path
        }
    )

    await db.commit()

    # Get the inserted file
    file_id = result.lastrowid
    return await get_file_by_id(file_id, user_id, db)


async def get_user_files(
    user_id: Optional[int],
    folder_path: str,
    db: AsyncSession
) -> List[FileResponse]:
    """Get files for a user in a specific folder"""

    result = await db.execute(
        text("""
            SELECT * FROM files
            WHERE (user_id = :user_id OR user_id IS NULL)
            AND folder_path = :folder_path
            ORDER BY created_at DESC
        """),
        {"user_id": user_id, "folder_path": folder_path}
    )

    files = result.fetchall()
    return [FileResponse(**dict(file)) for file in files]


async def get_file_by_id(
    file_id: int,
    user_id: Optional[int],
    db: AsyncSession
) -> Optional[FileResponse]:
    """Get a specific file by ID"""

    result = await db.execute(
        text("""
            SELECT * FROM files
            WHERE id = :file_id AND (user_id = :user_id OR user_id IS NULL)
        """),
        {"file_id": file_id, "user_id": user_id}
    )

    file = result.fetchone()
    return FileResponse(**dict(file)) if file else None


async def delete_file_record(
    file_id: int,
    user_id: Optional[int],
    db: AsyncSession
) -> bool:
    """Delete a file record and physical file"""

    # Get file info first
    file_record = await get_file_by_id(file_id, user_id, db)
    if not file_record:
        return False

    # Delete physical file
    try:
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)

        # Delete transcription file if exists
        if file_record.transcription_path and os.path.exists(file_record.transcription_path):
            os.remove(file_record.transcription_path)
    except Exception:
        # Log error but continue with database deletion
        pass

    # Delete from database
    await db.execute(
        text("""
            DELETE FROM files
            WHERE id = :file_id AND (user_id = :user_id OR user_id IS NULL)
        """),
        {"file_id": file_id, "user_id": user_id}
    )

    await db.commit()
    return True


async def create_folder(
    name: str,
    parent_path: str,
    user_id: Optional[int],
    db: AsyncSession
) -> bool:
    """Create a new folder (just a placeholder file record)"""

    # Create a folder record (using a special file_type)
    try:
        await db.execute(
            text("""
                INSERT INTO files (filename, original_filename, file_path, file_type, user_id, folder_path)
                VALUES (:filename, :original_filename, :file_path, 'folder', :user_id, :folder_path)
            """),
            {
                "filename": name,
                "original_filename": name,
                "file_path": f"{parent_path.rstrip('/')}/{name}",
                "user_id": user_id,
                "folder_path": parent_path
            }
        )
        await db.commit()
        return True
    except Exception:
        return False


async def move_file(
    file_id: int,
    new_path: str,
    user_id: Optional[int],
    db: AsyncSession
) -> bool:
    """Move a file to a different folder"""

    try:
        await db.execute(
            text("""
                UPDATE files
                SET folder_path = :new_path
                WHERE id = :file_id AND (user_id = :user_id OR user_id IS NULL)
            """),
            {"file_id": file_id, "new_path": new_path, "user_id": user_id}
        )
        await db.commit()
        return True
    except Exception:
        return False


async def get_files_by_type(
    file_type: str,
    user_id: Optional[int],
    db: AsyncSession
) -> List[FileResponse]:
    """Get files by type (document, video, etc.)"""

    result = await db.execute(
        text("""
            SELECT * FROM files
            WHERE file_type = :file_type AND (user_id = :user_id OR user_id IS NULL)
            ORDER BY created_at DESC
        """),
        {"file_type": file_type, "user_id": user_id}
    )

    files = result.fetchall()
    return [FileResponse(**dict(file)) for file in files]


