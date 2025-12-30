"""
AI chat routes with WebSocket streaming support
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import uuid

from app.dependencies import get_current_user, get_current_user_ws, get_db
from app.core.ai_client import get_ai_client
from app.core.vector_store import get_vector_store
from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.chat_service import create_chat_session, save_chat_message, get_chat_history


router = APIRouter()


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    user = Depends(get_current_user_ws),
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
            
            search_where = None
            if file_ids:
                try:
                    # Filter by the local database file IDs (integers) or Drive IDs (strings)
                    # We create an $or condition if multiple IDs of different types are present
                    int_ids = [int(fid) for fid in file_ids if str(fid).isdigit()]
                    str_ids = [str(fid) for fid in file_ids if not str(fid).isdigit()]
                    
                    filters = []
                    if int_ids:
                        if len(int_ids) == 1:
                            filters.append({"file_id": int_ids[0]})
                        else:
                            filters.append({"file_id": {"$in": int_ids}})
                    
                    if str_ids:
                        if len(str_ids) == 1:
                            filters.append({"drive_file_id": str_ids[0]})
                        else:
                            filters.append({"drive_file_id": {"$in": str_ids}})
                    
                    if len(filters) == 1:
                        search_where = filters[0]
                    elif len(filters) > 1:
                        search_where = {"$or": filters}
                        
                except Exception as e:
                    print(f"Error building search filter: {str(e)}")

            search_results = await vector_store.search_documents(
                message, 
                n_results=5, 
                where=search_where
            )

            # Build context from search results
            context = ""
            sources = []

            if search_results.get("documents"):
                for i, doc in enumerate(search_results["documents"][0]):
                    metadata = search_results["metadatas"][0][i] if (search_results.get("metadatas") and search_results["metadatas"][0]) else {}
                    filename = metadata.get("filename") or metadata.get("name") or f"Document {i+1}"
                    context += f"\nSource: {filename}\nContent Snippet: {doc[:1000]}\n---\n"
                    sources.append(metadata)

            # Build AI prompt
            system_prompt = f"""You are SmartDrive AI, an expert document assistant.
Your goal is to answer questions using ONLY the provided document context.

RULES:
1. If the answer is in the context, provide a detailed response and CITE the source filenames.
2. If the answer is NOT in the context, say "I'm sorry, I couldn't find information about that in the selected documents."
3. Do NOT use your general knowledge to answer if the context is missing.
4. If multiple documents are provided, synthesize the information correctly.

CONTEXT FROM DOCUMENTS:
{context}
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

            # Send start signal
            await websocket.send_json({
                "type": "start",
                "session_id": session_id
            })

            # Get AI response with streaming
            ai_client = get_ai_client()
            full_response = ""

            async for chunk in ai_client.chat_completion(messages, stream=True):
                full_response += chunk
                await websocket.send_json({
                    "type": "stream",
                    "content": chunk,
                    "session_id": session_id
                })

            # Save AI response
            await save_chat_message(session_id, "assistant", full_response, user.id if user else None, db, sources)

            # Send sources
            for source in sources:
                await websocket.send_json({
                    "type": "source",
                    "source": source,
                    "session_id": session_id
                })

            # Send completion signal
            await websocket.send_json({
                "type": "end",
                "session_id": session_id
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
    
    search_where = None
    if request.file_ids:
        try:
            int_ids = [int(fid) for fid in request.file_ids if str(fid).isdigit()]
            str_ids = [str(fid) for fid in request.file_ids if not str(fid).isdigit()]
            
            filters = []
            if int_ids:
                if len(int_ids) == 1:
                    filters.append({"file_id": int_ids[0]})
                else:
                    filters.append({"file_id": {"$in": int_ids}})
            
            if str_ids:
                if len(str_ids) == 1:
                    filters.append({"drive_file_id": str_ids[0]})
                else:
                    filters.append({"drive_file_id": {"$in": str_ids}})
            
            if len(filters) == 1:
                search_where = filters[0]
            elif len(filters) > 1:
                search_where = {"$or": filters}
        except:
            pass

    search_results = await vector_store.search_documents(request.message, n_results=5, where=search_where)

    # Build context
    context = ""
    sources = []

    if search_results.get("documents"):
        for i, doc in enumerate(search_results["documents"][0]):
            metadata = search_results["metadatas"][0][i] if (search_results.get("metadatas") and search_results["metadatas"][0]) else {}
            filename = metadata.get("filename") or metadata.get("name") or f"Document {i+1}"
            context += f"\nSource: {filename}\nContent Snippet: {doc[:1000]}\n---\n"
            sources.append(metadata)

    # Get AI response
    ai_client = get_ai_client()

    system_prompt = f"""You are SmartDrive AI, an expert document assistant.
Your goal is to answer questions using ONLY the provided document context.

RULES:
1. If the answer is in the context, provide a detailed response and CITE the source filenames.
2. If the answer is NOT in the context, say "I'm sorry, I couldn't find information about that in the selected documents."
3. Do NOT use your general knowledge to answer if the context is missing.

CONTEXT FROM DOCUMENTS:
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


