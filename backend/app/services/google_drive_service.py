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
        
        # Download file using Drive API
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


# Global service instance
google_drive_service = GoogleDriveService()
