"""
FastAPI dependency injection functions
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Query, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db_session
from app.core.auth import verify_token


# Security scheme for JWT
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async for session in get_db_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Current user dependency with JWT validation (supports Header and Query token)"""
    actual_token = None
    if credentials:
        actual_token = credentials.credentials
    elif token:
        actual_token = token

    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await verify_token(actual_token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Optional user dependency (supports Header and Query token)"""
    actual_token = None
    if credentials:
        actual_token = credentials.credentials
    elif token:
        actual_token = token

    if not actual_token:
        return None

    user = await verify_token(actual_token, db)
    return user


async def get_current_user_ws(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket user dependency that supports token in query params.
    Does not use HTTPBearer to avoid TypeError: HTTPBearer() missing 1 required positional argument: 'request'
    """
    actual_token = token
    
    # Fallback to Authorization header in websocket handshake if provided
    if not actual_token:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            actual_token = auth_header.split(" ")[1]
        
    if not actual_token:
        # For WebSockets, we might want to close with a code instead of raising HTTPException,
        # but raising it works as well (FastAPI handles it by closing).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user = await verify_token(actual_token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user


