# Architecture Overview

Complete guide to Smart-Drive's architecture, data flow, and design patterns.

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart-Drive Platform                      │
│                                                             │
│  ┌─────────────────┐    WebSocket     ┌─────────────────┐   │
│  │   Vue 3 UI      │◄────────────────►│  FastAPI Backend │   │
│  │  (Frontend)     │    HTTP/REST     │   (Backend)      │   │
│  └─────────────────┘                  └─────────────────┘   │
│           │                                   │              │
│           │                                   │              │
│           ▼                                   ▼              │
│  ┌─────────────────┐                  ┌─────────────────┐   │
│  │ Local Storage   │                  │ Google Drive API │   │
│  │ (IndexedDB)     │                  │ Integration      │   │
│  └─────────────────┘                  └─────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  AI Processing Layer                     │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │ Document    │  │   Video     │  │   Vector    │     │ │
│  │  │ Processing  │  │ Processing  │  │   Search    │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
│           │                                   │              │
│           ▼                                   ▼              │
│  ┌─────────────────┐                  ┌─────────────────┐   │
│  │   SQLite DB     │◄────────────────►│   ChromaDB      │   │
│  │ (Metadata)      │   Embeddings     │ (Vectors)       │   │
│  └─────────────────┘   & Search       └─────────────────┘   │
│           │                                   │              │
│           ▼                                   ▼              │
│  ┌─────────────────┐                  ┌─────────────────┐   │
│  │ File System     │                  │   External APIs  │   │
│  │ (Local Files)   │                  │ (Groq, Whisper)  │   │
│  └─────────────────┘                  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

### Complete Directory Tree

```
smart-drive/
├── backend/                          # FastAPI backend application
│   ├── app/
│   │   ├── core/                     # Core functionality
│   │   │   ├── ai_client.py          # Groq API integration
│   │   │   ├── auth.py               # JWT authentication
│   │   │   ├── document_processor.py # Document text extraction
│   │   │   ├── drive_client.py       # Google Drive API client
│   │   │   ├── image_processor.py    # Image analysis
│   │   │   └── video_processor.py    # Video transcription
│   │   ├── models/                   # Pydantic data models
│   │   │   ├── chat.py               # Chat message models
│   │   │   ├── file.py               # File metadata models
│   │   │   ├── google_token.py       # OAuth token models
│   │   │   └── user.py               # User models
│   │   ├── routers/                  # API route handlers
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── chat.py               # Chat WebSocket endpoints
│   │   │   ├── drive.py              # Google Drive endpoints
│   │   │   └── files.py              # File management endpoints
│   │   ├── services/                 # Business logic services
│   │   │   ├── chat_service.py       # Chat conversation logic
│   │   │   ├── file_service.py       # File operations
│   │   │   ├── google_drive_service.py # Drive sync logic
│   │   │   └── user_service.py       # User management
│   │   ├── utils/                    # Utility functions
│   │   │   ├── file_utils.py         # File handling utilities
│   │   │   └── text_utils.py         # Text processing utilities
│   │   ├── config.py                 # Application configuration
│   │   ├── database.py               # Database connection
│   │   ├── dependencies.py           # FastAPI dependencies
│   │   └── main.py                   # Application entry point
│   ├── chroma_db/                    # Vector database storage
│   ├── uploads/                      # Local file storage
│   ├── tests/                        # Backend test suite
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Backend container config
├── frontend/                         # Vue.js frontend application
│   ├── src/
│   │   ├── components/               # Reusable Vue components
│   │   │   ├── chat/                 # Chat-related components
│   │   │   │   ├── AIChatPanel.vue   # Main chat interface
│   │   │   │   ├── ChatInput.vue     # Message input component
│   │   │   │   ├── ChatMessage.vue   # Individual message display
│   │   │   │   └── TypingIndicator.vue # AI typing animation
│   │   │   ├── common/               # Shared UI components
│   │   │   │   ├── BaseButton.vue    # Standardized buttons
│   │   │   │   ├── BaseInput.vue     # Form inputs
│   │   │   │   ├── BaseModal.vue     # Modal dialogs
│   │   │   │   └── LoadingSpinner.vue # Loading indicators
│   │   │   └── files/                # File management components
│   │   │       ├── FileCard.vue      # File display card
│   │   │       ├── FileExplorer.vue  # File browser
│   │   │       └── UploadModal.vue   # File upload interface
│   │   ├── composables/              # Vue composition functions
│   │   │   ├── useChat.js            # Chat functionality
│   │   │   └── useFiles.js           # File operations
│   │   ├── router/                   # Vue Router configuration
│   │   │   └── index.js              # Route definitions
│   │   ├── services/                 # API service layer
│   │   │   ├── api/                  # API client functions
│   │   │   │   ├── authenticationService.js
│   │   │   │   ├── chatService.js
│   │   │   │   ├── driveService.js
│   │   │   └── api.js                # Axios configuration
│   │   ├── stores/                   # Pinia state management
│   │   │   ├── auth.js               # Authentication state
│   │   │   ├── chat.js               # Chat conversation state
│   │   │   ├── files.js              # File management state
│   │   │   └── ui.js                 # UI state
│   │   ├── views/                    # Page-level components
│   │   │   ├── AIChat.vue            # Chat page
│   │   │   ├── Dashboard.vue         # Main dashboard
│   │   │   ├── FileExplorer.vue      # File browser page
│   │   │   ├── Login.vue             # Authentication page
│   │   │   └── Settings.vue          # User settings
│   │   ├── App.vue                   # Root Vue component
│   │   └── main.js                   # Vue application entry
│   ├── public/                       # Static assets
│   ├── package.json                  # Node dependencies
│   └── Dockerfile                    # Frontend container config
├── docker/                           # Docker configuration
│   ├── docker-compose.yml            # Development services
│   ├── docker-compose.prod.yml       # Production services
│   └── nginx.conf                    # Web server config
├── scripts/                          # Development scripts
├── docs/                             # Documentation
└── Makefile                          # Build automation
```

## Component Architecture

### Vue.js Component Hierarchy

```
App.vue (Root)
├── AppHeader.vue
├── AppSidebar.vue
├── RouterView
│   ├── Login.vue
│   ├── Dashboard.vue
│   │   ├── FileExplorer.vue
│   │   │   ├── FileCard.vue (multiple)
│   │   │   └── UploadModal.vue
│   │   └── RecentFiles.vue
│   ├── AIChat.vue
│   │   ├── AIChatPanel.vue
│   │   │   ├── ChatMessage.vue (multiple)
│   │   │   ├── ChatInput.vue
│   │   │   └── TypingIndicator.vue
│   └── Settings.vue
└── ToastNotification.vue (global)
```

### FastAPI Application Structure

```
main.py (Entry Point)
├── Routers
│   ├── auth.py (/auth/*)
│   ├── files.py (/files/*)
│   ├── drive.py (/drive/*)
│   └── chat.py (/ws/chat)
├── Services Layer
│   ├── UserService (authentication, user management)
│   ├── FileService (file operations, metadata)
│   ├── GoogleDriveService (Drive sync, OAuth)
│   └── ChatService (AI conversations, RAG)
├── Core Layer
│   ├── AIClient (Groq API integration)
│   ├── DocumentProcessor (text extraction)
│   ├── VideoProcessor (Whisper transcription)
│   ├── DriveClient (Google Drive API)
│   └── Auth (JWT handling)
└── Database Layer
    ├── SQLite (metadata, users, files)
    └── ChromaDB (vector embeddings)
```

## Data Flow Architecture

### File Upload and Processing Flow

```
1. User Upload
       ↓
2. Frontend Validation
       ↓
3. API Upload Endpoint (/files/upload)
       ↓
4. File Storage (local filesystem)
       ↓
5. Metadata Database (SQLite)
       ↓
6. Document Processing
   ├── Text Extraction (PDF/DOCX/TXT)
   │       ↓
   │   Text Chunking (overlap strategy)
   │       ↓
   │   Embedding Generation
   │       ↓
   │   ChromaDB Storage
   │
   └── Video Processing (MP4/AVI/WEBM)
           ↓
       Whisper Transcription
           ↓
       Timestamp Preservation
           ↓
       Text Chunking
           ↓
       Embedding Generation
           ↓
       ChromaDB Storage
```

### AI Chat Conversation Flow

```
1. User Question
       ↓
2. Frontend WebSocket (/ws/chat)
       ↓
3. Message Validation
       ↓
4. Context Retrieval
   ├── File Selection (user specified or auto)
   │       ↓
   │   Vector Similarity Search (ChromaDB)
   │       ↓
   │   Relevant Chunks Selection
   │
   └── Conversation History
           ↓
       Recent Messages Retrieval
           ↓
       Context Window Management
       ↓
5. Prompt Construction
   ├── System Instructions
   │   └── Content-based responses only
   ├── Retrieved Context
   │   └── Source citations required
   └── User Question
       ↓
6. Groq API Call (streaming)
       ↓
7. Response Processing
   ├── Content Filtering
   │   └── Remove hallucinations
   ├── Source Attribution
   │   └── File references
   └── Citation Generation
       ↓
8. WebSocket Streaming Response
       ↓
9. Frontend Display
```

### Google Drive Synchronization Flow

```
1. User Authorization Request
       ↓
2. OAuth 2.0 Flow
   ├── Google Consent Screen
   │       ↓
   │   Authorization Code
   │       ↓
   │   Token Exchange
   │       ↓
   │   JWT Generation
   │
   └── Token Storage
           ↓
       Secure Database Storage
           ↓
3. Drive File Discovery
       ↓
4. Metadata Comparison
   ├── Local Cache Check
   │       ↓
   │   Change Detection
   │       ↓
   │   Delta Updates Only
   │
   └── New File Processing
           ↓
       Download & Process
           ↓
       Embedding Generation
           ↓
       Database Storage
```

## State Management Architecture

### Frontend State Management (Pinia)

#### Auth Store
```javascript
// stores/auth.js
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false,
    loading: true
  }),

  actions: {
    async login(credentials) {
      // JWT authentication
      const response = await authService.login(credentials);
      this.token = response.token;
      this.user = response.user;
      this.isAuthenticated = true;
    },

    async logout() {
      // Clear authentication state
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
    }
  }
});
```

#### Chat Store
```javascript
// stores/chat.js
export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    currentConversation: null,
    isTyping: false,
    selectedFiles: []
  }),

  actions: {
    async sendMessage(message) {
      // WebSocket communication
      this.isTyping = true;

      const wsMessage = {
        message,
        file_ids: this.selectedFiles,
        conversation_id: this.currentConversation
      };

      websocket.send(JSON.stringify(wsMessage));
    },

    addMessage(message) {
      this.messages.push(message);
    }
  }
});
```

### Backend State Management

#### Database Models (SQLAlchemy)

```python
# models/file.py
class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"))

    # Processing status
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)

    # AI processing metadata
    text_content = Column(Text)  # Extracted text
    page_count = Column(Integer)  # For PDFs
    word_count = Column(Integer)
    language = Column(String)

    # Relationships
    user = relationship("User", back_populates="files")
    chat_messages = relationship("ChatMessage", back_populates="file")
```

#### Vector Database Management (ChromaDB)

```python
# core/vector_store.py
class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

    def create_collection(self, file_id: str) -> chromadb.Collection:
        """Create a new collection for a file's embeddings."""
        return self.client.create_collection(
            name=f"file_{file_id}",
            metadata={"file_id": file_id}
        )

    def add_embeddings(self, collection_name: str, embeddings: List[List[float]],
                      documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add embeddings to a collection."""
        collection = self.client.get_collection(name=collection_name)

        ids = [f"chunk_{i}" for i in range(len(embeddings))]

        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_similar(self, collection_name: str, query_embedding: List[float],
                      n_results: int = 5) -> Dict[str, Any]:
        """Search for similar embeddings."""
        collection = self.client.get_collection(name=collection_name)

        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
```

## AI Processing Pipeline

### Document Processing Architecture

```
Raw Document (PDF/DOCX/TXT)
       ↓
Text Extraction Layer
├── PDFMiner (PDFs)
├── python-docx (DOCX)
└── Direct Read (TXT)
       ↓
Text Cleaning & Normalization
├── Remove special characters
├── Normalize whitespace
├── Language detection
└── Encoding standardization
       ↓
Intelligent Chunking Strategy
├── Overlap-based chunking (configurable)
├── Semantic boundary detection
├── Maximum chunk size enforcement
└── Metadata preservation (page numbers, sections)
       ↓
Embedding Generation
├── Sentence Transformers model
├── Batch processing for efficiency
├── Embedding dimensionality reduction
└── Quality validation
       ↓
Vector Database Storage
├── ChromaDB collection creation
├── Metadata attachment
├── Index optimization
└── Search index building
```

### Video Processing Architecture

```
Raw Video (MP4/AVI/WEBM)
       ↓
Audio Extraction (FFmpeg)
├── Format conversion to WAV
├── Audio normalization
├── Quality optimization
└── Temporary file management
       ↓
Whisper Transcription
├── Model selection (base/small/medium)
├── Language detection/auto
├── Timestamp preservation
├── Confidence scoring
└── Batch processing
       ↓
Transcript Post-processing
├── Speaker diarization (optional)
├── Punctuation restoration
├── Capitalization normalization
└── Noise filtering
       ↓
Time-stamped Chunking
├── Timestamp-aware segmentation
├── Overlap consideration
├── Context preservation
└── Metadata enrichment
       ↓
Embedding Generation
└── Same as document pipeline
       ↓
Temporal Vector Storage
├── Time-range metadata
├── Timestamp indexing
└── Sequential retrieval optimization
```

## API Design Patterns

### RESTful Endpoints

```python
# routers/files.py
@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a file."""
    # 1. Validate file
    if not validate_file_type(file.filename):
        raise HTTPException(400, "Unsupported file type")

    # 2. Save to filesystem
    file_path = await save_file(file, current_user.id)

    # 3. Create database record
    db_file = File(
        filename=file.filename,
        file_path=file_path,
        user_id=current_user.id
    )
    db.add(db_file)
    db.commit()

    # 4. Start background processing
    background_tasks.add_task(process_file, db_file.id)

    return FileResponse.from_orm(db_file)
```

### WebSocket Communication

```python
# routers/chat.py
@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, token: str = Query(...)):
    """Real-time AI chat with streaming responses."""
    await websocket.accept()

    # 1. Authenticate user
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        await websocket.close(code=4001)
        return

    # 2. Initialize chat service
    chat_service = ChatService(user_id)

    try:
        while True:
            # 3. Receive message
            data = await websocket.receive_json()

            # 4. Process message
            async for response_chunk in chat_service.process_message(data):
                # 5. Stream response
                await websocket.send_json({
                    "type": "chunk",
                    "content": response_chunk.content,
                    "source": response_chunk.source,
                    "done": response_chunk.done
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
```

## Security Architecture

### Authentication Flow

```
Client Request
       ↓
Authorization Header (Bearer Token)
       ↓
JWT Token Validation
├── Signature verification
├── Expiration check
├── Issuer validation
└── User context extraction
       ↓
Database User Lookup
       ↓
Permission Validation
       ↓
Request Processing
```

### File Upload Security

```
File Upload Request
       ↓
Content-Type Validation
├── Allowed MIME types
├── File extension check
└── Magic number verification
       ↓
Size Validation
├── Maximum file size
├── User quota check
└── Storage space validation
       ↓
Malware Scanning (Future)
       ↓
Secure Storage
├── Random filename generation
├── Path traversal prevention
└── Permission restrictions
```

## Performance Optimization

### Database Optimization

#### Connection Pooling

```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Connection pool size
    max_overflow=20,       # Max overflow connections
    pool_timeout=30,       # Connection timeout
    pool_recycle=3600,     # Recycle connections hourly
    echo=False
)
```

#### Query Optimization

```python
# services/file_service.py
def get_user_files_optimized(user_id: str, limit: int = 50, offset: int = 0):
    """Optimized query with eager loading."""
    return db.query(File)\
        .options(joinedload(File.user))\
        .filter(File.user_id == user_id)\
        .order_by(File.upload_date.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
```

### Caching Strategy

#### Redis for Session Data (Future)

```python
# Caching layer for frequently accessed data
cache = Redis(host='localhost', port=6379, db=0)

def get_cached_file_metadata(file_id: str):
    """Cache file metadata to reduce database queries."""
    cache_key = f"file_metadata:{file_id}"

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - fetch from database
    metadata = db.query(File).filter(File.id == file_id).first()
    if metadata:
        cache.setex(cache_key, 3600, json.dumps(metadata.__dict__))
        return metadata.__dict__

    return None
```

### Vector Search Optimization

#### Approximate Nearest Neighbor (ANN) Search

```python
# Optimized similarity search
def search_similar_optimized(query_embedding, collection_name, n_results=10):
    """Use ANN search for better performance on large datasets."""
    collection = chroma_client.get_collection(collection_name)

    # Use cosine similarity with optimized parameters
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
        # ChromaDB automatically uses ANN for performance
    )

    return results
```

## Scalability Considerations

### Horizontal Scaling

#### Stateless Backend Design
- All user sessions stored in database
- File processing as background tasks
- Stateless WebSocket connections
- External service dependencies (ChromaDB, Groq)

#### Database Sharding Strategy
```
User-based sharding:
├── Shard 1: Users A-M
├── Shard 2: Users N-Z
└── Global tables: System config, API keys

File-based sharding:
├── Shard 1: Documents
├── Shard 2: Videos
├── Shard 3: Images
└── Shard 4: Audio files
```

### Vertical Scaling

#### Resource Optimization
- Memory-efficient text processing
- Streaming for large file uploads
- Background job queues for processing
- Connection pooling for databases

#### CDN Integration (Future)
```
Static Assets → CDN (CloudFlare, AWS CloudFront)
Uploaded Files → CDN with access control
AI-generated content → CDN with caching
```

## Monitoring and Observability

### Application Metrics

```python
# core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

# AI processing metrics
AI_REQUESTS = Counter('ai_requests_total', 'Total AI API requests', ['provider', 'model'])
AI_LATENCY = Histogram('ai_request_duration_seconds', 'AI request latency', ['provider', 'model'])

# File processing metrics
FILES_UPLOADED = Counter('files_uploaded_total', 'Total files uploaded', ['file_type'])
FILES_PROCESSED = Counter('files_processed_total', 'Total files processed', ['status'])

# Database metrics
DB_CONNECTIONS = Gauge('db_connections_active', 'Active database connections')
DB_QUERY_LATENCY = Histogram('db_query_duration_seconds', 'Database query latency', ['query_type'])
```

### Logging Architecture

```python
# Structured logging configuration
import structlog

shared_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

structlog.configure(
    processors=shared_processors + [
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.WriteLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Error Handling and Resilience

### Circuit Breaker Pattern

```python
# core/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    async def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
            else:
                raise CircuitBreakerOpenException()

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = 'closed'

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
```

### Graceful Degradation

```python
# services/chat_service.py
class ChatService:
    async def process_message(self, message_data):
        """Process chat message with fallback strategies."""

        # Primary: Full AI processing with RAG
        try:
            return await self._full_ai_processing(message_data)
        except (AIAPIError, VectorDBError):
            logger.warning("Primary AI processing failed, falling back")

        # Fallback 1: AI without RAG (basic responses)
        try:
            return await self._basic_ai_processing(message_data)
        except AIAPIError:
            logger.error("Basic AI processing failed, using static responses")

        # Fallback 2: Static responses for common queries
        return await self._static_response_processing(message_data)
```

## Design Principles

### SOLID Principles Application

#### Single Responsibility Principle
- Each service handles one domain (auth, files, chat)
- Components have focused, single purposes
- Clear separation between data access, business logic, and presentation

#### Open/Closed Principle
- Extensible file processor architecture
- Plugin-based AI model integration
- Configurable processing pipelines

#### Liskov Substitution Principle
- Consistent interface across file processors
- Interchangeable AI service implementations
- Standardized error handling patterns

#### Interface Segregation Principle
- Focused service interfaces
- Minimal, specific component APIs
- Separated read/write operations

#### Dependency Inversion Principle
- Dependency injection throughout the application
- Abstract interfaces for external services
- Configuration-driven service instantiation

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│         Delivery Layer              │  ← WebSocket, REST API
│   (Routers, Controllers)            │
├─────────────────────────────────────┤
│         Use Case Layer              │  ← Business Logic
│   (Services, Application Rules)     │
├─────────────────────────────────────┤
│         Domain Layer                │  ← Core Business Entities
│   (Models, Domain Logic)            │
├─────────────────────────────────────┤
│         Infrastructure Layer        │  ← External Concerns
│   (Database, External APIs, File IO)│
└─────────────────────────────────────┘
```

This architecture ensures:
- **Testability**: Each layer can be tested independently
- **Maintainability**: Changes in one layer don't affect others
- **Flexibility**: Easy to swap implementations
- **Scalability**: Clear boundaries for horizontal scaling
