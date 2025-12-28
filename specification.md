# Smart-Drive Project Specification

## Project Goal
Build a web app that integrates Google Drive + local uploads + AI Q&A on documents & videos using Groq API - delivered in 24h with zero expenditure.

## Tech Stack (Final Choices)
- **Frontend**: Vue 3 + Vite + TailwindCSS
- **Backend**: FastAPI
- **Auth**: JWT + Google OAuth2 (drive.readonly + drive.file)
- **LLM**: Groq API (OpenAI-compatible)
- **Vector DB**: ChromaDB (local)
- **Metadata DB**: SQLite
- **File Storage**: Local filesystem
- **Speech-to-Text**: Whisper local
- **Realtime**: FastAPI WebSocket streaming

## Architecture Overview
```
User <-> Vue3 UI
| WebSocket
FastAPI Backend
|
Google Drive API
SQLite Metadata DB
Chroma Vector DB
Whisper (video -> text)
Groq LLM API
Local FS
```

## Core Pipelines

### Document Workflow
Upload/Drive -> Extract text -> Chunk -> Create Embeddings -> Store in Chroma

### Video Workflow
Upload/Drive Video -> Whisper -> Timestamped text -> Chunk -> Embeddings -> Chroma

### Chat
Frontend (WebSocket) -> Backend -> Groq Stream -> Frontend UI

## Required Repositories (to clone)

### Backend Base
- RAG + Chroma examples: https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/chroma/Using_Chroma_for_embeddings_search.ipynb
- LangChain tutorials: https://github.com/gkamradt/langchain-tutorials

### Google Drive Sync
- Official Python examples (Drive API): https://github.com/gsuitedevs/python-samples/tree/main/drive

### Video Transcription
- Whisper from OpenAI: https://github.com/openai/whisper

## Vue UI Components (validated)

### Drag & Drop (file reorder / folder move)
- **vue-draggable-next** (Vue3 compatible DnD): https://github.com/anish2690/vue-draggable-next

### File Explorer UI
- **VueFinder**: Vue file manager UI (file tree, preview): https://github.com/n1crack/vuefinder

### File Upload UI (option)
- **vue-file-agent** (drag & drop upload component): https://github.com/safrazik/vue-file-agent

## API Design (REST + WS)

### Auth
- **POST /auth/login**
- **POST /auth/refresh**
- Google OAuth callback

### Files
- **GET /files** -> list (local + Drive)
- **POST /files/upload**
- **POST /files/move**
- **DELETE /files/:id**
- **GET /files/:id/preview**

### Drive Sync
- **POST /drive/connect**
- **GET /drive/sync**

### Chat AI
- **WebSocket /ws/chat** -> Streams Groq tokens

## AI Logic (Groq + RAG)

### Prompt Template
You are SmartDrive AI.
You ONLY respond using indexed content from ChromaDB.
If answer not in content, reply "Content not found."
Include source filename + position.

### Retrieval
- Chunk with overlap
- Vector embedding per chunk
- Store in ChromaDB with metadata (source, type, timestamp/page)
- Use sparse + dense retrieval

## File Support
- Docs: PDF, DOCX, TXT, XLSX, PPTX
- Images: JPG, PNG, GIF
- Audio: MP3, WAV
- Video: MP4, MOV, AVI, WEBM

## Testing
- Unit: FastAPI logic, chunking, embedding service
- Integration: Drive API workflows
- E2E: Upload -> Q&A -> Video -> timestamp query

## Deployment (Dev/Prod)
- Docker (FastAPI + Chroma + Vue)
- .env config
- HTTPS
- Token safety

## Timeline
- **Duration**: 24 hours
- **Delivery**: Complete working application
- **Budget**: Zero expenditure

## Core Features

### 1. Google Drive Integration
- **Authentication**: Google OAuth2 with drive.readonly + drive.file scopes
- **File Synchronization**: Real-time sync of Google Drive files
- **Unified View**: Display both local and Drive files in single interface

### 2. File Management System
- **File Explorer**: VueFinder-based file browser with drag & drop
- **Upload System**: vue-file-agent for drag & drop uploads
- **Operations**: Create/move/delete/rename folders and files
- **Preview**: File preview functionality for supported formats

### 3. AI Assistant (Core Feature)
- **Document Analysis**: RAG-based Q&A on uploaded documents
- **Video Analysis**: Whisper transcription + timestamped Q&A
- **Chat Interface**: WebSocket streaming chat with Groq API
- **Content-Based**: Responses only from indexed content
- **Multi-file Support**: Analyze multiple files simultaneously

## Technical Implementation

### Vector Database (ChromaDB)
- Local vector storage for document/video embeddings
- Metadata storage (filename, type, timestamps, pages)
- Semantic search with sparse + dense retrieval

### Document Processing
- Text extraction from PDF, DOCX, TXT
- Chunking with overlap for optimal retrieval
- Embedding generation and storage

### Video Processing
- Whisper local transcription
- Timestamp preservation
- Text chunking and embedding
- Timestamp-based question answering

### Real-time Chat
- WebSocket connection for streaming responses
- Groq API integration
- Context-aware conversations
- Source citation in responses

## Security & Performance
- JWT authentication
- Secure token storage
- File upload validation
- Rate limiting
- Fast AI responses (<5s)
- Local processing (zero cost)

## Development Setup
- Clone required repositories
- Docker containerization
- Local ChromaDB and SQLite
- Vue 3 + Vite development server
- FastAPI backend with auto-reload

## Success Criteria
- Google Drive sync works
- Local upload works
- AI Q&A (Docs + Video) works
- Streaming chat response (<5s)
- Full UI (Explorer + Chat)

## Important Notes
- Groq API is the free LLM provider
- All repositories have real GitHub links
- Vue components are Vue 3 compatible
- No React, no paid services
- Local processing ensures zero cost
- Emphasis on reusing existing functional code for 24h delivery
