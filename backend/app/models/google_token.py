"""
Google OAuth token storage model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GoogleTokenCreate(BaseModel):
    """Model for creating a new Google token record"""
    user_id: int
    access_token: str
    refresh_token: Optional[str] = None
    token_uri: str = "https://oauth2.googleapis.com/token"
    expires_at: datetime


class GoogleTokenUpdate(BaseModel):
    """Model for updating an existing Google token"""
    access_token: str
    expires_at: datetime


class GoogleTokenResponse(BaseModel):
    """Model for Google token response"""
    id: int
    user_id: int
    access_token: str
    refresh_token: Optional[str]
    token_uri: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class GoogleTokenInDB(BaseModel):
    """Internal model for database operations"""
    id: int
    user_id: int
    access_token: str
    refresh_token: Optional[str]
    token_uri: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
