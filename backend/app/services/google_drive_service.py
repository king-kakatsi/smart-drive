"""
Google Drive API integration service
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.drive_client import GoogleDriveClient
from app.services.google_token_service import get_valid_access_token_for_user


class GoogleDriveService:
    """Service for Google Drive API operations"""
    
    def __init__(self):
        self.drive_client = GoogleDriveClient()
    
    async def list_files_from_drive(
        self,
        database: AsyncSession,
        user_id: int,
        folder_id: str = "root",
        page_token: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        List files from user's Google Drive
        
        Args:
            database: Database session
            user_id: User ID
            folder_id: Drive folder ID (default: root)
            page_token: Pagination token
            page_size: Number of files per page
        
        Returns:
            Dict containing files list and next page token
        """
        # Get valid access token (will refresh if needed)
        access_token = await get_valid_access_token_for_user(database, user_id)
        
        if not access_token:
            raise Exception("No valid Google Drive token found for user")
        
        # List files using Drive API
        return await self.drive_client.list_drive_files(
            access_token=access_token,
            folder_id=folder_id,
            page_token=page_token
        )
    
    async def get_file_metadata_from_drive(
        self,
        database: AsyncSession,
        user_id: int,
        file_id: str
    ) -> Dict[str, Any]:
        """
        Get metadata for specific Drive file
        
        Args:
            database: Database session
            user_id: User ID
            file_id: Google Drive file ID
        
        Returns:
            Dict containing file metadata
        """
        access_token = await get_valid_access_token_for_user(database, user_id)
        
        if not access_token:
            raise Exception("No valid Google Drive token found for user")
        
        # Get file metadata from Drive API
        files_url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
        params = {
            "fields": "id, name, mimeType, size, modifiedTime, webViewLink, thumbnailLink, parents"
        }
        
        import aiohttp
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(files_url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get file metadata: {response.status} - {error_text}")
                
                return await response.json()
    
    async def download_file_content_from_drive(
        self,
        database: AsyncSession,
        user_id: int,
        file_id: str
    ) -> bytes:
        """
        Download file content from Drive

        Args:
            database: Database session
            user_id: User ID
            file_id: Google Drive file ID

        Returns:
            bytes: File content
        """
        access_token = await get_valid_access_token_for_user(database, user_id)

        if not access_token:
            raise Exception("No valid Google Drive token found for user")

        # Get file metadata to check if it's a Google native file
        metadata = await self.get_file_metadata_from_drive(database, user_id, file_id)
        mime_type = metadata.get("mimeType", "")

        # Check if this is a Google native file that needs export
        if mime_type.startswith("application/vnd.google-apps."):
            # Map Google native files to export formats
            export_formats = {
                "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
                "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
                "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # PPTX
                "application/vnd.google-apps.drawing": "application/pdf",  # PDF
            }

            export_mime_type = export_formats.get(mime_type)
            if export_mime_type:
                # Export the Google native file
                return await self.drive_client.export_file(access_token, file_id, export_mime_type)
            else:
                raise Exception(f"Cannot export Google file type: {mime_type}")

        # Regular file - download directly
        return await self.drive_client.download_file(access_token, file_id)
    
    async def search_files_in_drive(
        self,
        database: AsyncSession,
        user_id: int,
        search_query: str,
        page_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search files in Google Drive
        
        Args:
            database: Database session
            user_id: User ID
            search_query: Search query string
            page_size: Number of results
        
        Returns:
            List of file metadata dictionaries
        """
        access_token = await get_valid_access_token_for_user(database, user_id)
        
        if not access_token:
            raise Exception("No valid Google Drive token found for user")
        
        # Search files using Drive API
        files_url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"name contains '{search_query}' and trashed = false",
            "fields": "files(id, name, mimeType, size, modifiedTime, webViewLink)",
            "pageSize": page_size
        }
        
        import aiohttp
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(files_url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to search files: {response.status} - {error_text}")
                
                data = await response.json()
                return data.get("files", [])

    async def get_storage_quota(
        self,
        database: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get user's Google Drive storage quota
        
        Args:
            database: Database session
            user_id: User ID
        
        Returns:
            Dict containing storage info
        """
        access_token = await get_valid_access_token_for_user(database, user_id)
        
        if not access_token:
            raise Exception("No valid Google Drive token found for user")
            
        return await self.drive_client.get_storage_quota(access_token)

    async def delete_file_from_drive(
        self,
        database: AsyncSession,
        user_id: int,
        file_id: str
    ) -> bool:
        """
        Delete (trash) a file from Google Drive

        Args:
            database: Database session
            user_id: User ID
            file_id: Google Drive file ID

        Returns:
            bool: True if successfully deleted
        """
        print(f"Getting access token for user {user_id}")
        access_token = await get_valid_access_token_for_user(database, user_id)

        if not access_token:
            raise Exception("No valid Google Drive token found for user")

        print(f"Calling drive client to delete file {file_id}")
        # Delete file using Drive API (moves to trash)
        return await self.drive_client.delete_file(access_token, file_id)


# Global service instance
google_drive_service = GoogleDriveService()
