# API Reference

Complete API documentation for Smart-Drive backend services, including REST endpoints and WebSocket protocols.

## Overview

Smart-Drive provides both REST API endpoints and WebSocket connections for real-time communication. The API is built with FastAPI and includes automatic OpenAPI documentation.

### Base URL
```
Production: https://api.smart-drive.com
Development: http://localhost:8000
```

### Authentication
All API requests require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Response Format
All responses follow a consistent JSON format:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "errors": null
}
```

### Error Responses
```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "errors": {
    "field": ["Error details"]
  }
}
```

## Authentication Endpoints

### POST /auth/login

Authenticate user and return JWT tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Invalid credentials
- `422`: Validation error

### POST /auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAi...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### POST /auth/logout

Invalidate the current session.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### GET /auth/me

Get current user information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "username": "string",
    "email": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T00:00:00Z",
    "is_active": true
  }
}
```

## File Management Endpoints

### POST /files/upload

Upload a file for processing and AI analysis.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (file): The file to upload
- `description` (optional string): File description

**Supported File Types:**
- Documents: PDF, DOCX, TXT
- Videos: MP4, AVI, WEBM, MOV
- Images: JPG, JPEG, PNG, GIF
- Audio: MP3, WAV

**File Size Limit:** 10MB

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "filename": "document.pdf",
    "original_name": "my-document.pdf",
    "file_path": "/uploads/uuid/document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "upload_date": "2024-01-01T00:00:00Z",
    "processing_status": "pending",
    "user_id": "string",
    "metadata": {
      "page_count": 10,
      "word_count": 2500,
      "language": "en"
    }
  }
}
```

**Status Codes:**
- `201`: File uploaded successfully
- `400`: Invalid file or validation error
- `413`: File too large
- `415`: Unsupported file type

### GET /files

List user's files with pagination and filtering.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `per_page` (integer, default: 20, max: 100): Items per page
- `search` (string): Search in filename
- `file_type` (string): Filter by MIME type
- `processing_status` (string): Filter by status (pending, processing, completed, failed)
- `sort_by` (string, default: upload_date): Sort field (upload_date, filename, file_size)
- `sort_order` (string, default: desc): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "string",
        "filename": "document.pdf",
        "file_size": 1024000,
        "upload_date": "2024-01-01T00:00:00Z",
        "processing_status": "completed",
        "mime_type": "application/pdf",
        "metadata": {
          "page_count": 10,
          "word_count": 2500
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### GET /files/{file_id}

Get detailed information about a specific file.

**Path Parameters:**
- `file_id` (string): File ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "filename": "document.pdf",
    "original_name": "my-document.pdf",
    "file_path": "/uploads/uuid/document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "upload_date": "2024-01-01T00:00:00Z",
    "processing_status": "completed",
    "processing_started_at": "2024-01-01T00:00:00Z",
    "processing_completed_at": "2024-01-01T00:05:00Z",
    "user_id": "string",
    "metadata": {
      "page_count": 10,
      "word_count": 2500,
      "language": "en",
      "encoding": "utf-8"
    },
    "ai_metadata": {
      "chunks_count": 25,
      "embeddings_generated": true,
      "searchable": true
    }
  }
}
```

### GET /files/{file_id}/download

Download the original file.

**Path Parameters:**
- `file_id` (string): File ID

**Response:** Binary file content with appropriate Content-Type header.

**Status Codes:**
- `200`: File download
- `404`: File not found
- `403`: Access denied

### GET /files/{file_id}/preview

Get file preview information (for images, documents, etc.).

**Path Parameters:**
- `file_id` (string): File ID

**Response:**
```json
{
  "success": true,
  "data": {
    "preview_available": true,
    "preview_type": "image",
    "preview_url": "/files/uuid/preview.jpg",
    "thumbnail_url": "/files/uuid/thumbnail.jpg",
    "dimensions": {
      "width": 800,
      "height": 600
    },
    "page_count": 1
  }
}
```

### DELETE /files/{file_id}

Delete a file and all associated data.

**Path Parameters:**
- `file_id` (string): File ID

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

**Status Codes:**
- `200`: File deleted
- `404`: File not found
- `403`: Access denied

### POST /files/{file_id}/reprocess

Reprocess a file (useful if processing failed or you want to update AI embeddings).

**Path Parameters:**
- `file_id` (string): File ID

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "string",
    "processing_status": "pending",
    "message": "File queued for reprocessing"
  }
}
```

## Google Drive Integration Endpoints

### POST /drive/connect

Initiate Google Drive connection.

**Response:**
```json
{
  "success": true,
  "data": {
    "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
    "state": "random_state_string"
  }
}
```

### GET /drive/callback

OAuth2 callback endpoint (handled automatically by frontend).

### GET /drive/status

Check Google Drive connection status.

**Response:**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "email": "user@gmail.com",
    "last_sync": "2024-01-01T00:00:00Z",
    "files_count": 150
  }
}
```

### POST /drive/sync

Manually trigger Google Drive synchronization.

**Response:**
```json
{
  "success": true,
  "data": {
    "sync_id": "string",
    "status": "running",
    "message": "Drive synchronization started"
  }
}
```

### GET /drive/files

List Google Drive files (integrated with local files).

**Query Parameters:** Same as `/files` endpoint

**Response:** Same format as `/files` endpoint, with additional `source: "drive"` field.

### DELETE /drive/disconnect

Disconnect Google Drive integration.

**Response:**
```json
{
  "success": true,
  "message": "Google Drive disconnected successfully"
}
```

## AI Chat Endpoints

### WebSocket /ws/chat

Real-time AI chat with streaming responses.

**Authentication:** JWT token required in query parameter or header

**Connection URL:**
```
ws://localhost:8000/ws/chat?token=<jwt_token>
```

**Message Format (Send):**
```json
{
  "type": "chat_message",
  "message": "What are the main topics in this document?",
  "file_ids": ["file_id_1", "file_id_2"],
  "conversation_id": "optional_conversation_id",
  "context": {
    "timestamp": "2024-01-01T00:00:00Z",
    "session_id": "session_123"
  }
}
```

**Message Format (Receive):**
```json
{
  "type": "chat_response",
  "content": "The main topics in the document include...",
  "source": {
    "file_id": "file_id_1",
    "filename": "document.pdf",
    "page": 5,
    "timestamp": "00:30"  // for videos
  },
  "done": false,
  "metadata": {
    "model": "llama3-70b-8192",
    "tokens_used": 150,
    "processing_time": 2.5
  }
}
```

**Error Message:**
```json
{
  "type": "error",
  "error": "Authentication failed",
  "code": "AUTH_FAILED",
  "details": {
    "reason": "Invalid token"
  }
}
```

### GET /chat/conversations

List user's chat conversations.

**Query Parameters:**
- `page` (integer, default: 1)
- `per_page` (integer, default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "string",
        "title": "Discussion about quarterly reports",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:05:00Z",
        "message_count": 12,
        "file_ids": ["file1", "file2"],
        "last_message": "That makes sense, thank you!"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

### GET /chat/conversations/{conversation_id}

Get detailed conversation with all messages.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "Discussion about quarterly reports",
    "created_at": "2024-01-01T00:00:00Z",
    "messages": [
      {
        "id": "string",
        "role": "user",
        "content": "What are the sales figures?",
        "timestamp": "2024-01-01T00:00:00Z",
        "file_references": ["file1"]
      },
      {
        "id": "string",
        "role": "assistant",
        "content": "According to the quarterly report...",
        "timestamp": "2024-01-01T00:00:05Z",
        "sources": [
          {
            "file_id": "file1",
            "filename": "quarterly_report.pdf",
            "page": 15,
            "text_snippet": "Sales figures for Q1..."
          }
        ]
      }
    ]
  }
}
```

### DELETE /chat/conversations/{conversation_id}

Delete a conversation and all its messages.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Response:**
```json
{
  "success": true,
  "message": "Conversation deleted successfully"
}
```

### POST /chat/conversations/{conversation_id}/title

Update conversation title.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Request Body:**
```json
{
  "title": "Updated conversation title"
}
```

## Search Endpoints

### GET /search

Search across all user files using AI-powered semantic search.

**Query Parameters:**
- `q` (string, required): Search query
- `file_ids` (array): Limit search to specific files
- `file_type` (string): Filter by file type
- `limit` (integer, default: 20): Max results
- `include_content` (boolean, default: false): Include full content snippets

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "machine learning algorithms",
    "results": [
      {
        "file_id": "string",
        "filename": "ml_paper.pdf",
        "score": 0.95,
        "snippets": [
          {
            "text": "Machine learning algorithms can be categorized...",
            "page": 25,
            "position": 1250
          }
        ],
        "metadata": {
          "file_type": "application/pdf",
          "upload_date": "2024-01-01T00:00:00Z"
        }
      }
    ],
    "total_results": 15,
    "search_time": 0.8
  }
}
```

### GET /search/suggestions

Get search query suggestions based on user content.

**Query Parameters:**
- `prefix` (string): Partial query for autocomplete
- `limit` (integer, default: 10): Max suggestions

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      "machine learning algorithms",
      "neural network architecture",
      "deep learning applications",
      "computer vision techniques"
    ]
  }
}
```

## Analytics Endpoints

### GET /analytics/overview

Get user analytics and usage statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "files": {
      "total_count": 150,
      "total_size": 1073741824,  // bytes
      "by_type": {
        "application/pdf": 45,
        "video/mp4": 23,
        "text/plain": 82
      }
    },
    "ai_usage": {
      "total_queries": 1250,
      "total_tokens": 50000,
      "average_response_time": 2.3,
      "top_topics": ["research papers", "video content", "documentation"]
    },
    "storage": {
      "used": 1073741824,
      "limit": 5368709120,  // 5GB
      "percentage": 20
    },
    "activity": {
      "last_7_days": {
        "uploads": 12,
        "queries": 89,
        "downloads": 5
      }
    }
  }
}
```

### GET /analytics/files

Get detailed file analytics.

**Query Parameters:**
- `period` (string, default: 30d): Time period (7d, 30d, 90d, 1y)
- `group_by` (string, default: day): Grouping (day, week, month)

**Response:**
```json
{
  "success": true,
  "data": {
    "upload_trends": [
      {"date": "2024-01-01", "count": 5},
      {"date": "2024-01-02", "count": 8}
    ],
    "file_types": [
      {"type": "application/pdf", "count": 45, "size": 524288000},
      {"type": "video/mp4", "count": 23, "size": 2147483648}
    ],
    "processing_stats": {
      "success_rate": 0.98,
      "average_processing_time": 45.2,
      "failure_reasons": {
        "unsupported_format": 2,
        "file_corrupted": 1
      }
    }
  }
}
```

## System Endpoints

### GET /health

Health check endpoint for load balancers and monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "chromadb": "healthy",
    "redis": "healthy",
    "groq_api": "healthy"
  },
  "uptime": 3600
}
```

### GET /metrics

Prometheus metrics endpoint.

**Response:** Prometheus format metrics

### GET /version

Get API version information.

**Response:**
```json
{
  "version": "1.0.0",
  "build_date": "2024-01-01T00:00:00Z",
  "git_commit": "abc123def456",
  "environment": "production"
}
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **General endpoints**: 100 requests per minute
- **File uploads**: 10 uploads per minute
- **AI chat**: 50 messages per minute
- **Search**: 30 searches per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Error Codes

### Authentication Errors
- `AUTH001`: Invalid credentials
- `AUTH002`: Token expired
- `AUTH003`: Invalid token
- `AUTH004`: Insufficient permissions

### File Operation Errors
- `FILE001`: File not found
- `FILE002`: Unsupported file type
- `FILE003`: File too large
- `FILE004`: File processing failed
- `FILE005`: Storage quota exceeded

### AI Service Errors
- `AI001`: AI service unavailable
- `AI002`: Invalid request format
- `AI003`: Content not found
- `AI004`: Rate limit exceeded

### System Errors
- `SYS001`: Database connection failed
- `SYS002`: External service error
- `SYS003`: Internal server error

## SDKs and Libraries

### JavaScript/TypeScript Client

```javascript
import { SmartDriveAPI } from 'smart-drive-js';

const client = new SmartDriveAPI({
  baseURL: 'https://api.smart-drive.com',
  token: 'your-jwt-token'
});

// Upload a file
const file = await client.files.upload(fileInput.files[0]);

// Start a chat
const ws = client.chat.connect();
ws.send({
  message: "What are the main topics?",
  file_ids: [file.id]
});

// Search files
const results = await client.search.query("machine learning");
```

### Python Client

```python
from smart_drive import SmartDriveClient

client = SmartDriveClient(
    base_url="https://api.smart-drive.com",
    token="your-jwt-token"
)

# Upload file
with open("document.pdf", "rb") as f:
    file = client.files.upload(f)

# Chat with AI
response = client.chat.ask(
    message="Summarize this document",
    file_ids=[file.id]
)

# Search
results = client.search.query("specific topic")
```

## Webhooks (Future)

Smart-Drive will support webhooks for real-time notifications:

```json
{
  "event": "file.processed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "file_id": "string",
    "status": "completed",
    "processing_time": 45.2
  }
}
```

Supported events:
- `file.uploaded`: File uploaded
- `file.processed`: File processing completed
- `file.failed`: File processing failed
- `chat.message`: New chat message
- `drive.synced`: Google Drive sync completed

## API Changelog

### Version 1.0.0
- Initial release
- Basic file upload and AI chat functionality
- Google Drive integration
- REST API and WebSocket support

### Planned Features
- **v1.1.0**: Advanced search filters, bulk operations
- **v1.2.0**: Team collaboration features
- **v1.3.0**: Advanced AI models, custom prompts
- **v2.0.0**: Real-time collaboration, advanced analytics

## Support

For API support and questions:

- **Documentation**: https://docs.smart-drive.com
- **API Explorer**: https://api.smart-drive.com/docs
- **GitHub Issues**: For bugs and feature requests
- **Email**: api-support@smart-drive.com

## Rate Limits and Fair Use

- **Free Tier**: 100 AI queries, 10GB storage, 100 file uploads per month
- **Pro Tier**: 1000 AI queries, 100GB storage, unlimited uploads
- **Enterprise**: Custom limits

API calls are subject to fair use policies. Excessive usage may result in temporary throttling or account suspension.
