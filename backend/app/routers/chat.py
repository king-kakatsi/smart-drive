"""
AI chat routes with WebSocket streaming support
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import uuid

from app.dependencies import get_current_user, get_db
from app.core.ai_client import get_ai_client
from app.core.vector_store import get_vector_store
from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.chat_service import create_chat_session, save_chat_message, get_chat_history


router = APIRouter()


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time AI chat"""

    await websocket.accept()

    try:
        # Create or get chat session
        session_id = None

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            chat_request = json.loads(data)

            message = chat_request.get("message", "")
            session_id = chat_request.get("session_id", str(uuid.uuid4()))
            file_ids = chat_request.get("file_ids", [])

            if not message:
                await websocket.send_json({"error": "Message is required"})
                continue

            # Create session if new
            if not session_id or len(session_id) < 10:  # Simple check for new session
                session_id = str(uuid.uuid4())

            # Save user message
            await save_chat_message(session_id, "user", message, user.id if user else None, db)

            # Search for relevant documents
            vector_store = get_vector_store()
            search_results = await vector_store.search_documents(message, n_results=3)

            # Build context from search results
            context = ""
            sources = []

            if search_results.get("documents"):
                for i, doc in enumerate(search_results["documents"][0]):
                    context += f"\nDocument {i+1}: {doc[:1000]}..."  # Limit context length
                    if search_results.get("metadatas") and search_results["metadatas"][0]:
                        sources.append(search_results["metadatas"][0][i])

            # Build AI prompt
            system_prompt = f"""You are SmartDrive AI.
You ONLY respond using indexed content from documents.
If answer not in content, reply "Content not found."
Include source filename + position when possible.

Context from documents:
{context}
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

            # Get AI response with streaming
            ai_client = get_ai_client()
            full_response = ""

            async for chunk in ai_client.chat_completion(messages, stream=True):
                full_response += chunk
                await websocket.send_json({
                    "content": chunk,
                    "done": False,
                    "session_id": session_id
                })

            # Save AI response
            await save_chat_message(session_id, "assistant", full_response, user.id if user else None, db, sources)

            # Send completion signal
            await websocket.send_json({
                "content": "",
                "done": True,
                "session_id": session_id,
                "sources": sources
            })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user.id if user else 'anonymous'}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": f"Internal error: {str(e)}"})


@router.post("/", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """REST endpoint for chat (non-streaming)"""

    # Create session if needed
    session_id = request.session_id or str(uuid.uuid4())

    # Save user message
    await save_chat_message(session_id, "user", request.message, user.id, db)

    # Search for relevant documents
    vector_store = get_vector_store()
    search_results = await vector_store.search_documents(request.message, n_results=3)

    # Build context
    context = ""
    sources = []

    if search_results.get("documents"):
        for i, doc in enumerate(search_results["documents"][0]):
            context += f"\nDocument {i+1}: {doc[:1000]}..."
            if search_results.get("metadatas") and search_results["metadatas"][0]:
                sources.append(search_results["metadatas"][0][i])

    # Get AI response
    ai_client = get_ai_client()

    system_prompt = f"""You are SmartDrive AI.
You ONLY respond using indexed content from documents.
If answer not in content, reply "Content not found."
Include source filename + position when possible.

Context from documents:
{context}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message}
    ]

    response_text = ""
    async for chunk in ai_client.chat_completion(messages, stream=False):
        response_text += chunk

    # Save AI response
    await save_chat_message(session_id, "assistant", response_text, user.id, db, sources)

    return ChatResponse(
        session_id=session_id,
        message=ChatMessage(
            role="assistant",
            content=response_text
        ),
        sources=sources
    )


@router.get("/history/{session_id}")
async def get_chat_history_endpoint(
    session_id: str,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a session"""
    history = await get_chat_history(session_id, user.id, db)
    return {"session_id": session_id, "messages": history}


