"""
User service for authentication and user management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.models.user import UserCreate, UserResponse, UserInDB


async def create_or_update_user(user_data: UserCreate, db: AsyncSession) -> UserInDB:
    """Create a new user or update existing one"""

    # Check if user exists
    result = await db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": user_data.email}
    )
    existing_user = result.fetchone()

    if existing_user:
        # Update existing user
        await db.execute(
            text("""
                UPDATE users
                SET full_name = :full_name,
                    google_id = :google_id,
                    avatar_url = :avatar_url,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = :email
            """),
            {
                "full_name": user_data.full_name,
                "google_id": user_data.google_id,
                "avatar_url": user_data.avatar_url,
                "email": user_data.email
            }
        )

        # Get updated user
        result = await db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": user_data.email}
        )
        user = result.fetchone()

    else:
        # Create new user
        await db.execute(
            text("""
                INSERT INTO users (email, full_name, google_id, avatar_url)
                VALUES (:email, :full_name, :google_id, :avatar_url)
            """),
            {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "google_id": user_data.google_id,
                "avatar_url": user_data.avatar_url
            }
        )

        # Get created user
        result = await db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": user_data.email}
        )
        user = result.fetchone()

    await db.commit()
    return UserInDB(**dict(user))


async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[UserInDB]:
    """Get user by ID"""
    result = await db.execute(
        text("SELECT * FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    user = result.fetchone()
    return UserInDB(**dict(user)) if user else None


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[UserInDB]:
    """Get user by email"""
    result = await db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    )
    user = result.fetchone()
    return UserInDB(**dict(user)) if user else None


