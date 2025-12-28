"""
File handling utilities
"""
import os
import mimetypes
from pathlib import Path
from typing import Optional

from app.config import settings


def get_file_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def ensure_upload_dir() -> str:
    """Ensure upload directory exists"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    return settings.UPLOAD_DIR


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename"""
    import uuid
    name = Path(original_filename).stem
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4()}_{name}{ext}"


def get_file_type_from_path(file_path: str) -> str:
    """Determine file type from file path"""
    ext = Path(file_path).suffix.lower()

    # Document types
    if ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
        return 'document'

    # Video types
    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
        return 'video'

    # Audio types
    elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
        return 'audio'

    # Image types
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        return 'image'

    # Default
    else:
        return 'other'


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS


def get_file_info(file_path: str) -> dict:
    """Get comprehensive file information"""
    path = Path(file_path)

    return {
        "filename": path.name,
        "path": str(path),
        "size": get_file_size(file_path),
        "mime_type": get_file_mime_type(file_path),
        "extension": path.suffix,
        "type": get_file_type_from_path(file_path),
        "exists": path.exists()
    }


def cleanup_temp_files(temp_dir: str = None, older_than_hours: int = 24):
    """Clean up temporary files older than specified hours"""
    import time

    if not temp_dir:
        temp_dir = settings.UPLOAD_DIR

    if not os.path.exists(temp_dir):
        return

    current_time = time.time()
    cutoff_time = current_time - (older_than_hours * 3600)

    for filename in os.listdir(temp_dir):
        filepath = os.path.join(temp_dir, filename)

        # Skip if it's a directory
        if os.path.isdir(filepath):
            continue

        # Check file modification time
        if os.path.getmtime(filepath) < cutoff_time:
            try:
                os.remove(filepath)
                print(f"Cleaned up old file: {filename}")
            except OSError:
                pass  # Ignore errors during cleanup


