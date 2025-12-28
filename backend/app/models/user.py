"""
User models for authentication and user management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    full_name: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: EmailStr
    full_name: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(BaseModel):
    """Internal user model for database operations"""
    id: int
    email: str
    full_name: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


