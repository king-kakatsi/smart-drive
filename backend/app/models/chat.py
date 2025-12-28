"""
Chat models for AI conversation
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Individual chat message"""
    id: Optional[int] = None
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[List[Dict[str, Any]]] = None  # Source references
    created_at: Optional[datetime] = None


class ChatSession(BaseModel):
    """Chat session model"""
    id: Optional[int] = None
    session_id: str
    user_id: Optional[int] = None
    title: Optional[str] = None
    messages: List[ChatMessage] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None
    file_ids: Optional[List[int]] = None  # Files to analyze in this chat


class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str
    message: ChatMessage
    sources: Optional[List[Dict[str, Any]]] = None


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str
    done: bool = False
    sources: Optional[List[Dict[str, Any]]] = None


