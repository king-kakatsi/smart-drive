# File Upload Flow

This document describes the complete file upload flow in SmartDrive, including local storage and Google Drive integration with automatic fallback mechanisms.

## Upload Architecture

The upload system supports two storage backends with automatic fallback:

- **Primary**: Google Drive (cloud storage)
- **Fallback**: Local filesystem storage
- **Processing**: Asynchronous AI indexing for documents, videos, and images

## Frontend Upload Flow

### Vue.js Components

#### `UploadModal.vue` - Main Upload Interface

**Component Features:**
- Drag & drop file selection
- Multiple file upload with progress tracking
- File validation (type, size)
- Google Drive priority with local fallback
- Real-time upload status and error handling

**File Validation:**
```javascript
const allowedTypes = [
    'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'video/mp4', 'audio/mp3', 'audio/mpeg',
    'image/jpeg', 'image/png', 'image/gif'
]
```

### Pinia Store Management

#### `stores/files.js` - File State Management

**State Properties:**
- `localFiles`: Files stored locally
- `driveFiles`: Files from Google Drive
- `folderContents`: Current folder view
- `isUploading`: Upload progress state
- `folderIdMap`: Path-to-Drive-ID mappings

**Key Actions:**
- `uploadFile()`: Single file upload
- `fetchFolderContents()`: Refresh folder view
- `fetchStorageMetrics()`: Update storage quota

## Upload Flow Diagrams

### Phase 1: File Selection & Validation (Frontend)

```
User selects/drops files (UploadModal.vue)
    ↓
Validate file types and sizes
    ↓
Display files in upload queue
    ↓
User clicks "Submit" → uploadAllFiles()
    ↓
Sequential upload of each file
```

### Phase 2: Upload Processing with Fallback

```
For each file in queue:
    ↓
Try Google Drive upload first
    ↓
services/api/driveService.js::uploadFileToDrive()
    ↓
POST /api/v1/drive/upload with FormData
    ↓
routers/drive.py::upload_file_to_drive()
    │
    ├─ SUCCESS: File uploaded to Google Drive
    │   ↓
    │   Store metadata in local DB
    │   ↓
    │   Trigger AI processing
    │   ↓
    │   Update frontend state
    │
    └─ FAILED: Google Drive unavailable
        ↓
        Try local storage fallback
        ↓
        services/api/fileService.js::uploadFile()
        ↓
        POST /api/v1/files/upload with FormData
        ↓
        routers/files.py::upload_file()
            ↓
            Store file on local filesystem
            ↓
            Store metadata in local DB
            ↓
            Trigger AI processing
            ↓
            Update frontend state
```

### Phase 3: AI Processing Pipeline

```
File uploaded successfully
    ↓
Background processing based on file type
    ↓
core/{document|video|image}_processor.py
    │
    ├─ Document files (.pdf, .docx, .txt)
    │   ↓
    │   Extract text content
    │   ↓
    │   Chunk text into segments
    │   ↓
    │   Generate embeddings
    │   ↓
    │   Store in ChromaDB vector store
    │
    ├─ Video files (.mp4, .avi, .mov)
    │   ↓
    │   Extract audio track
    │   ↓
    │   Transcribe using Whisper
    │   ↓
    │   Generate embeddings
    │   ↓
    │   Store in vector database
    │
    └─ Image files (.jpg, .png, .gif)
        ↓
        Generate description using Groq Vision
        ↓
        Generate embeddings
        ↓
        Store in vector database

Update database: processed = 1
```

### Phase 4: State Synchronization

```
Upload completes successfully
    ↓
stores/files.js::fetchFolderContents()
    ↓
Parallel API calls:
    │
    ├─ services/api/fileService.js::listAllFiles()
    │   ↓
    │   GET /api/v1/files?folder_path=...
    │   ↓
    │   Update localFiles state
    │
    └─ services/api/driveService.js::listDriveFiles()
        ↓
        GET /api/v1/drive/files?page_size=...
        ↓
        Update driveFiles state

Merge and deduplicate files in store
    ↓
Update UI with new file list
```

## Backend API Routes

### Local File Upload

#### `routers/files.py::upload_file()`

**Endpoint:** `POST /api/v1/files/upload`

**Process:**
1. **Validation**: File type and size checks
2. **Storage**: Generate unique filename, save to disk
3. **Database**: Store file metadata
4. **Processing**: Trigger background AI processing
5. **Response**: Return file information

**Validation Rules:**
```python
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.md', '.mp4', '.avi', '.mov', '.mp3', '.jpg', '.jpeg', '.png', '.gif']
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

### Google Drive Upload

#### `routers/drive.py::upload_file_to_drive()`

**Endpoint:** `POST /api/v1/drive/upload`

**Process:**
1. **Authentication**: Get valid Google access token
2. **Validation**: File type and size checks
3. **Upload**: Use Google Drive API to upload file
4. **Metadata**: Store file info in local database
5. **Processing**: Trigger background AI processing
6. **Response**: Return file information with Drive ID

**Google Drive Integration:**
```python
# File metadata for Drive API
file_metadata = {
    'name': file.filename,
    'mimeType': file.content_type,
    'parents': [folder_id] if folder_id else None
}
```

## File Processing Pipeline

### Document Processing (`core/document_processor.py`)

**Supported Formats:**
- PDF files (PyPDF2 extraction)
- Word documents (.docx via python-docx)
- Text files (.txt direct reading)

**Process:**
1. Extract text content from file
2. Split into chunks (1000 chars with 200 char overlap)
3. Generate embeddings via ChromaDB
4. Store in vector database with metadata

### Video Processing (`core/video_processor.py`)

**Supported Formats:**
- MP4, AVI, MOV, MKV, WebM

**Process:**
1. Extract audio track using FFmpeg
2. Transcribe audio using Whisper AI
3. Generate embeddings from transcription
4. Store in vector database

### Image Processing (`core/image_processor.py`)

**Supported Formats:**
- JPEG, PNG, GIF, WebP

**Process:**
1. Send image to Groq Vision API for description
2. Generate embeddings from description
3. Store in vector database

## Error Handling & Fallback

### Primary Strategy: Google Drive First
```javascript
// UploadModal.vue - Fallback logic
try {
    // Try Google Drive first
    await driveService.uploadFileToDrive(file, folderId, folderPath)
} catch (driveError) {
    console.warn('Google Drive failed, falling back to local storage')
    // Fallback to local storage
    await fileService.uploadFile(file, folderPath)
}
```

### Error Scenarios:
1. **Google Drive unavailable**: Automatic fallback to local storage
2. **Local storage fails**: Upload marked as error
3. **File too large**: 413 error returned
4. **Invalid file type**: 400 error with validation message
5. **Processing fails**: File uploaded but marked as unprocessed

## State Management

### File Deduplication Logic

**Merge Strategy:**
```javascript
// stores/files.js - joinAndDeduplicate()
const fileMap = new Map()

// 1. Add local files first
localFiles.forEach(local => {
    const key = local.drive_file_id || `local_${local.id}`
    fileMap.set(key, { ...local, isLocal: true })
})

// 2. Merge Drive files (Drive data takes priority)
driveFiles.forEach(drive => {
    const key = drive.id
    if (fileMap.has(key)) {
        // Merge local intelligence with Drive richness
        fileMap.set(key, {
            ...fileMap.get(key),
            ...drive,
            isSynced: true
        })
    } else {
        fileMap.set(key, { ...drive, isDriveOnly: true })
    }
})
```

### Storage Metrics

**Quota Tracking:**
- Fetch from Google Drive API (`/api/v1/drive/metrics`)
- Default fallback: 15GB limit
- Real-time updates after uploads/deletions

## Performance Optimizations

1. **Sequential Uploads**: Prevent server overload
2. **Background Processing**: AI indexing doesn't block uploads
3. **Lazy Loading**: File lists loaded on demand
4. **Caching**: File metadata cached in localStorage
5. **Optimistic UI**: Immediate UI updates before API confirmation

## Security Considerations

1. **File Validation**: Strict type and size checking
2. **Path Sanitization**: Prevent directory traversal attacks
3. **Access Control**: User-scoped file operations
4. **Token Security**: Google tokens stored server-side only
5. **Error Handling**: No sensitive information in error messages

## API Endpoints Summary

| Endpoint | Method | Purpose | Storage |
|----------|--------|---------|---------|
| `/api/v1/files/upload` | POST | Upload to local storage | Local filesystem |
| `/api/v1/drive/upload` | POST | Upload to Google Drive | Google Drive |
| `/api/v1/files` | GET | List local files | Database query |
| `/api/v1/drive/files` | GET | List Drive files | Google Drive API |
| `/api/v1/files/{id}/download` | GET | Download local file | Local filesystem |
| `/api/v1/drive/files/{id}/download` | GET | Download Drive file | Google Drive API |

This upload system provides robust file handling with cloud storage priority, automatic fallback, and comprehensive AI processing for content indexing and search capabilities.
