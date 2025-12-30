"""
Service for managing Google OAuth tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import aiohttp

from app.models.google_token import GoogleTokenCreate, GoogleTokenInDB, GoogleTokenUpdate
from app.config import settings


async def store_google_tokens_for_user(
    database: AsyncSession,
    user_id: int,
    access_token: str,
    refresh_token: Optional[str],
    expires_in: int
) -> GoogleTokenInDB:
    """
    Store or update Google tokens for user
    
    Args:
        database: Database session
        user_id: User ID
        access_token: Google access token
        refresh_token: Google refresh token (optional)
        expires_in: Token expiration time in seconds
    
    Returns:
        GoogleTokenInDB: Stored token record
    """
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    # Check if token already exists for user
    result = await database.execute(
        text("SELECT * FROM google_tokens WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    existing_token = result.fetchone()
    
    if existing_token:
        # Update existing token
        await database.execute(
            text("""
                UPDATE google_tokens
                SET access_token = :access_token,
                    refresh_token = COALESCE(:refresh_token, refresh_token),
                    expires_at = :expires_at,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id
            """),
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "user_id": user_id
            }
        )
    else:
        # Create new token record
        await database.execute(
            text("""
                INSERT INTO google_tokens (user_id, access_token, refresh_token, expires_at)
                VALUES (:user_id, :access_token, :refresh_token, :expires_at)
            """),
            {
                "user_id": user_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at
            }
        )
    
    await database.commit()
    
    # Retrieve and return the stored token
    result = await database.execute(
        text("SELECT * FROM google_tokens WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    token = result.fetchone()
    return GoogleTokenInDB(**token._asdict())


async def get_valid_access_token_for_user(
    database: AsyncSession,
    user_id: int
) -> Optional[str]:
    """
    Get valid access token for user, refreshing if expired
    
    Args:
        database: Database session
        user_id: User ID
    
    Returns:
        str: Valid access token or None if not found
    """
    result = await database.execute(
        text("SELECT * FROM google_tokens WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    token_record = result.fetchone()
    
    if not token_record:
        return None
    
    token = GoogleTokenInDB(**token_record._asdict())
    
    # Check if token is expired (with 5 minute buffer)
    if datetime.utcnow() >= token.expires_at - timedelta(minutes=5):
        # Token is expired or about to expire, refresh it
        if token.refresh_token:
            new_access_token = await refresh_expired_google_token(database, user_id)
            return new_access_token
        else:
            # No refresh token available
            return None
    
    return token.access_token


async def refresh_expired_google_token(
    database: AsyncSession,
    user_id: int
) -> Optional[str]:
    """
    Refresh expired Google access token using refresh token
    
    Args:
        database: Database session
        user_id: User ID
    
    Returns:
        str: New access token or None if refresh failed
    """
    result = await database.execute(
        text("SELECT * FROM google_tokens WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    token_record = result.fetchone()
    
    if not token_record or not token_record.refresh_token:
        return None
    
    token = GoogleTokenInDB(**token_record._asdict())
    
    # Refresh the token using Google OAuth2 API
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": token.refresh_token,
        "grant_type": "refresh_token"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Token refresh failed: {response.status} - {error_text}")
                    return None
                
                token_data = await response.json()
                
                # Update token in database
                new_access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                
                await store_google_tokens_for_user(
                    database,
                    user_id,
                    new_access_token,
                    token.refresh_token,  # Keep existing refresh token
                    expires_in
                )
                
                return new_access_token
    
    except Exception as error:
        print(f"Error refreshing token: {str(error)}")
        return None


async def get_google_token_for_user(
    database: AsyncSession,
    user_id: int
) -> Optional[GoogleTokenInDB]:
    """
    Get Google token record for user
    
    Args:
        database: Database session
        user_id: User ID
    
    Returns:
        GoogleTokenInDB: Token record or None if not found
    """
    result = await database.execute(
        text("SELECT * FROM google_tokens WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    token_record = result.fetchone()
    
    if not token_record:
        return None
    
    return GoogleTokenInDB(**token_record._asdict())


async def delete_google_token_for_user(
    database: AsyncSession,
    user_id: int
) -> bool:
    """
    Delete Google token for user
    
    Args:
        database: Database session
        user_id: User ID
    
    Returns:
        bool: True if deleted, False otherwise
    """
    result = await database.execute(
        text("DELETE FROM google_tokens WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    await database.commit()
    return result.rowcount > 0
