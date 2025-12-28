"""
Authentication routes including Google OAuth2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.dependencies import get_db, get_current_user
from app.core.auth import create_access_token, verify_token
from app.core.drive_client import get_google_auth_url, exchange_code_for_tokens
from app.models.user import UserCreate, UserResponse
from app.services.user_service import create_or_update_user


router = APIRouter()


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth2 login"""
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth2 callback"""
    try:
        # Exchange code for tokens
        tokens = exchange_code_for_tokens(code)

        # Get user info from Google
        user_info = await get_google_user_info(tokens["access_token"])

        # Create or update user
        user_data = UserCreate(
            email=user_info["email"],
            full_name=user_info["name"],
            google_id=user_info["id"],
            avatar_url=user_info.get("picture")
        )

        user = await create_or_update_user(user_data, db)

        # Create JWT token
        access_token = create_access_token({"sub": str(user.id)})

        # Redirect to frontend with token
        frontend_url = "http://localhost:5173/auth/callback"
        return RedirectResponse(
            url=f"{frontend_url}?token={access_token}&user_id={user.id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """Refresh access token"""
    access_token = create_access_token({"sub": str(current_user.id)})
    return {"access_token": access_token}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        google_id=current_user.google_id,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"message": "Successfully logged out"}


