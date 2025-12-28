"""
Chat service for AI conversation management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import uuid
import json

from app.models.chat import ChatMessage


async def create_chat_session(
    user_id: Optional[int],
    title: Optional[str],
    db: AsyncSession
) -> str:
    """Create a new chat session"""

    session_id = str(uuid.uuid4())

    await db.execute(
        text("""
            INSERT INTO chat_sessions (session_id, user_id, title)
            VALUES (:session_id, :user_id, :title)
        """),
        {"session_id": session_id, "user_id": user_id, "title": title}
    )

    await db.commit()
    return session_id


async def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    user_id: Optional[int],
    db: AsyncSession,
    sources: Optional[List[Dict[str, Any]]] = None
):
    """Save a chat message"""

    await db.execute(
        text("""
            INSERT INTO chat_messages (session_id, role, content, sources)
            VALUES (:session_id, :role, :content, :sources)
        """),
        {
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources": json.dumps(sources) if sources else None
        }
    )

    await db.commit()


async def get_chat_history(
    session_id: str,
    user_id: Optional[int],
    db: AsyncSession
) -> List[ChatMessage]:
    """Get chat history for a session"""

    result = await db.execute(
        text("""
            SELECT role, content, sources, created_at
            FROM chat_messages
            WHERE session_id = :session_id
            ORDER BY created_at ASC
        """),
        {"session_id": session_id}
    )

    messages = result.fetchall()
    chat_messages = []

    for msg in messages:
        sources = None
        if msg.sources:
            try:
                sources = json.loads(msg.sources)
            except:
                sources = None

        chat_messages.append(ChatMessage(
            role=msg.role,
            content=msg.content,
            sources=sources,
            created_at=msg.created_at
        ))

    return chat_messages


async def get_user_sessions(
    user_id: Optional[int],
    db: AsyncSession,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get chat sessions for a user"""

    result = await db.execute(
        text("""
            SELECT session_id, title, created_at, updated_at
            FROM chat_sessions
            WHERE user_id = :user_id OR user_id IS NULL
            ORDER BY updated_at DESC
            LIMIT :limit
        """),
        {"user_id": user_id, "limit": limit}
    )

    sessions = result.fetchall()
    return [{
        "session_id": s.session_id,
        "title": s.title,
        "created_at": s.created_at,
        "updated_at": s.updated_at
    } for s in sessions]
