"""
Google Drive API client for authentication and file operations
Adapted from Google Drive Python samples
"""
import aiohttp
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from app.config import settings


class GoogleDriveClient:
    """Google Drive API client"""

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def get_auth_url(self, state: str = None) -> str:
        """Generate Google OAuth2 authorization URL"""

        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }

        if state:
            params["state"] = state

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""

        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Token exchange failed: {response.status} - {error_text}")

                return await response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""

        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(userinfo_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get user info: {response.status} - {error_text}")

                return await response.json()

    async def list_drive_files(
        self,
        access_token: str,
        folder_id: str = "root",
        page_token: str = None
    ) -> Dict[str, Any]:
        """List files in Google Drive"""

        files_url = "https://www.googleapis.com/drive/v3/files"
        headers = {"Authorization": f"Bearer {access_token}"}

        params = {
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, thumbnailLink)",
            "pageSize": 100
        }

        if page_token:
            params["pageToken"] = page_token

        async with aiohttp.ClientSession() as session:
            async with session.get(files_url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to list files: {response.status} - {error_text}")

                return await response.json()

    async def download_file(self, access_token: str, file_id: str) -> bytes:
        """Download a file from Google Drive"""

        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(download_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to download file: {response.status} - {error_text}")

                return await response.read()


# Global Drive client instance
drive_client = GoogleDriveClient()


def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    return drive_client.get_auth_url()


async def exchange_code_for_tokens(code: str):
    """Exchange OAuth code for tokens"""
    return await drive_client.exchange_code_for_tokens(code)


async def get_google_user_info(access_token: str):
    """Get Google user information"""
    return await drive_client.get_user_info(access_token)


