# AI Chat Flow

This document describes the complete AI chat system in SmartDrive, including real-time WebSocket communication, document-aware responses, and vector search integration.

## Chat Architecture

The chat system combines multiple technologies:

- **Real-time Communication**: WebSocket for streaming AI responses
- **Document Intelligence**: Vector search for context-aware answers
- **State Management**: Pinia stores for reactive UI updates
- **AI Integration**: Groq API with streaming capabilities
- **Session Management**: Persistent chat history and file context

## Frontend Chat Components

### Vue.js Chat Interface

#### `AIChatPanel.vue` - Main Chat Container

**Component Responsibilities:**
- WebSocket lifecycle management (connect/disconnect)
- Message display and real-time updates
- File context integration
- Auto-scroll for new messages

**Key Features:**
```javascript
// WebSocket connection on mount
onMounted(() => {
    chatStore.initializeWebSocket()
})

// File context integration
watch(() => props.selectedFile, (newFile) => {
    if (newFile) {
        chatStore.setContextFiles([newFile.id])
    }
})
```

### Pinia State Management

#### `stores/chat.js` - Chat State Store

**State Properties:**
- `messages`: Array of chat messages with roles and content
- `sessionId`: Current chat session identifier
- `isTyping`: AI response status
- `selectedFileIds`: Files providing context for chat
- `currentContext`: Active file context

**WebSocket Message Handling:**
```javascript
handleWebSocketMessage(data) {
    switch(data.type) {
        case 'start': this.isTyping = true; break;
        case 'stream': // Append streaming content
        case 'source': // Add source citations
        case 'end': this.isTyping = false; break;
    }
}
```

### API Communication Layer

#### `services/api/chatService.js` - Chat API Service

**WebSocket Management:**
```javascript
connectWebSocket(onMessage, onError) {
    const token = localStorage.getItem('access_token')
    const wsUrl = `${environment.apiWebSocketUrl}/api/v1/chat/ws/chat?token=${token}`
    this.websocket = new WebSocket(wsUrl)
    // ... event handlers
}

sendMessage(message, sessionId, fileIds) {
    const payload = { message, session_id: sessionId, file_ids: fileIds }
    this.websocket.send(JSON.stringify(payload))
}
```

**REST API Fallback:**
- `sendChatMessage()`: Non-streaming REST endpoint
- `getChatHistory()`: Retrieve chat session history

## Chat Flow Diagrams

### Phase 1: Chat Initialization

```
User opens AI Chat (AIChatPanel.vue)
    ↓
onMounted() → useChatStore().initializeWebSocket()
    ↓
chatService.connectWebSocket(onMessage, onError)
    ↓
WebSocket connection: ws://api/chat/ws/chat?token={JWT}
    ↓
Backend authenticates via JWT token
    ↓
WebSocket connection established
    ↓
Ready for chat messages
```

### Phase 2: Message Processing (WebSocket Flow)

```
User types message → chatStore.sendMessage(content)
    ↓
Add user message to local state
    ↓
chatService.sendMessage(content, sessionId, fileIds)
    ↓
WebSocket send: {message, session_id, file_ids}
    ↓
routers/chat.py::chat_websocket()
    │
    ├─ Authenticate user via JWT
    │
    ├─ Save user message to database
    │   ↓
    │   services/chat_service.py::save_chat_message()
    │
    ├─ Build document search context
    │   ↓
    │   core/vector_store.py::search_documents()
    │       └─ ChromaDB semantic search with filters
    │
    ├─ Construct AI prompt with document context
    │
    ├─ Start streaming AI response
    │   ↓
    │   core/ai_client.py::chat_completion(stream=True)
    │       └─ POST https://api.groq.com/openai/v1/chat/completions
    │
    ├─ Stream response chunks via WebSocket
    │   ↓
    │   Send: {type: 'start'}, {type: 'stream', content: '...'}
    │   ↓
    │   Send: {type: 'source', source: metadata}
    │   ↓
    │   Send: {type: 'end', session_id: '...'}
    │
    └─ Save AI response to database
        ↓
        services/chat_service.py::save_chat_message()
```

### Phase 3: Document Context Building

```
Receive file_ids in WebSocket message
    ↓
Build search filters for vector database
    ↓
core/vector_store.py::search_documents()
    │
    ├─ Filter by file_id (local files) or drive_file_id (Google Drive)
    │   ↓
    │   Example: {"$or": [{"file_id": 123}, {"drive_file_id": "abc..."}]}
    │
    └─ Semantic search in ChromaDB
        ↓
        Return top 5 relevant document chunks
            ↓
            Build context string:
            "Source: filename.pdf
             Content Snippet: [text excerpt]...
             ---"
```

### Phase 4: AI Response Generation

```
Build system prompt with document context
    ↓
System Prompt Structure:
"You are SmartDrive AI, an expert document assistant.
RULES:
1. Answer using ONLY provided document context
2. Cite source filenames
3. Don't use general knowledge

CONTEXT FROM DOCUMENTS:
[Source: doc1.pdf]
[text excerpt 1]
---
[Source: doc2.pdf]
[text excerpt 2]"

    ↓
core/ai_client.py::GroqClient.chat_completion()
    ↓
POST to Groq API with streaming enabled
    ↓
Receive streaming response chunks
    ↓
Forward each chunk via WebSocket
    ↓
Frontend appends chunks to message in real-time
```

### Phase 5: Response Finalization

```
AI response complete
    ↓
Save complete response to database with sources
    ↓
services/chat_service.py::save_chat_message()
    │
    ├─ Store message content
    │
    ├─ Store source citations as JSON
    │   ↓
    │   [{"filename": "doc.pdf", "file_id": 123, "chunk_id": 0}, ...]
    │
    └─ Update session timestamp
        ↓
        Database: chat_messages table
```

## Backend API Routes

### WebSocket Endpoint

#### `routers/chat.py::chat_websocket()`

**Endpoint:** `WS /api/v1/chat/ws/chat`

**WebSocket Message Protocol:**
```json
// Client → Server
{
    "message": "What is the revenue for Q4?",
    "session_id": "uuid-string",
    "file_ids": ["123", "drive_file_id_456"]
}

// Server → Client (Streaming)
{ "type": "start", "session_id": "uuid-string" }
{ "type": "stream", "content": "Based on" }
{ "type": "stream", "content": " the documents" }
{ "type": "source", "source": {"filename": "report.pdf", "file_id": 123} }
{ "type": "end", "session_id": "uuid-string" }
```

**Authentication:** JWT token in WebSocket URL query parameter

### REST API Endpoints

#### `routers/chat.py::chat_message()`

**Endpoint:** `POST /api/v1/chat`

**Purpose:** Non-streaming chat for API integrations

**Response:**
```json
{
    "session_id": "uuid-string",
    "message": {
        "role": "assistant",
        "content": "Complete AI response...",
        "sources": [...]
    }
}
```

#### `routers/chat.py::get_chat_history_endpoint()`

**Endpoint:** `GET /api/v1/chat/history/{session_id}`

**Purpose:** Retrieve chat session history

**Response:**
```json
{
    "session_id": "uuid-string",
    "messages": [
        {
            "role": "user",
            "content": "Hello",
            "sources": null,
            "created_at": "2024-01-01T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "Hi there!",
            "sources": [...],
            "created_at": "2024-01-01T10:00:01Z"
        }
    ]
}
```

## Core Components

### AI Integration (`core/ai_client.py`)

**GroqClient Class:**
- `chat_completion()`: Streaming and non-streaming AI responses
- OpenAI-compatible API interface
- Automatic token management and error handling

**Streaming Implementation:**
```python
async def chat_completion(self, messages, stream=False):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if stream:
                # Parse Server-Sent Events
                while True:
                    line = await response.content.readline()
                    if not line: break
                    
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data = line_str[6:].strip()
                        if data == '[DONE]': break
                        
                        chunk = json.loads(data)
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
```

### Vector Search (`core/vector_store.py`)

**ChromaDB Integration:**
- `search_documents()`: Semantic search with metadata filtering
- Persistent vector storage with embeddings
- File-based filtering for context-aware responses

**Search Filtering:**
```python
# Filter by specific files
where = {"$or": [
    {"file_id": 123},           # Local file ID
    {"drive_file_id": "abc..."} # Google Drive file ID
]}

results = await vector_store.search_documents(query, n_results=5, where=where)
```

### Chat Persistence (`services/chat_service.py`)

**Database Operations:**
- `save_chat_message()`: Store messages with sources
- `get_chat_history()`: Retrieve session messages
- `create_chat_session()`: Initialize new sessions

**Data Structure:**
```sql
-- Chat sessions
CREATE TABLE chat_sessions (
    session_id VARCHAR PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Chat messages
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR,
    role VARCHAR, -- 'user' or 'assistant'
    content TEXT,
    sources JSON, -- Source citations
    created_at TIMESTAMP
);
```

## Frontend State Management

### Reactive Message Updates

**Real-time Streaming:**
```javascript
// In stores/chat.js
handleWebSocketMessage(data) {
    if (data.type === 'stream') {
        // Append to existing assistant message
        const lastMessage = this.messages[this.messages.length - 1]
        lastMessage.content += data.content
        // Vue reactivity triggers UI update
    }
}
```

### File Context Integration

**Dynamic Context Switching:**
```javascript
// File selection updates chat context
setContextFiles(fileIds) {
    this.selectedFileIds = fileIds
    // Next message will search these files
}

// File-specific chat initialization
startChatWithFile(file) {
    this.clearHistory()
    this.setContextFiles([file.id])
    this.currentContext = file
}
```

## Error Handling & Recovery

### WebSocket Connection Issues

**Automatic Reconnection:**
```javascript
// In chat store
sendMessage(content) {
    if (!this.isConnected) {
        this.initializeWebSocket()
    }
    // ... send message
}
```

### AI Response Errors

**Graceful Degradation:**
```javascript
// Backend error handling
try {
    async for chunk in ai_client.chat_completion(messages, stream=True):
        await websocket.send_json({"type": "stream", "content": chunk})
} except Exception as e:
    await websocket.send_json({"type": "error", "message": str(e)})
```

### Token Expiration

**Authentication Errors:**
- JWT expired → Frontend logout
- WebSocket auth failure → Connection rejected
- Invalid session → Error message

## Performance Optimizations

1. **WebSocket Efficiency**: Single persistent connection for streaming
2. **Lazy Loading**: Chat history loaded on demand
3. **Context Caching**: File metadata cached in memory
4. **Streaming UI**: Progressive rendering of AI responses
5. **Database Indexing**: Optimized queries for chat history

## Security Considerations

1. **Authentication**: JWT validation on WebSocket connection
2. **Authorization**: User-scoped chat sessions and file access
3. **Input Validation**: Message content sanitization
4. **Rate Limiting**: AI API call throttling
5. **Session Management**: Automatic cleanup of old sessions

This chat system provides intelligent, document-aware AI conversations with real-time streaming responses and comprehensive session management.
