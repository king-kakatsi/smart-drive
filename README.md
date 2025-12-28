# Smart-Drive

AI-powered document and video analysis platform with Google Drive integration. Ask questions about your files and get intelligent answers using Groq AI.

## Features

- **Google Drive Integration**: Connect and sync your Google Drive files
- **AI-Powered Q&A**: Ask questions about documents and videos
- **Video Transcription**: Automatic speech-to-text using Whisper
- **File Management**: Upload, organize, and manage files
- **Real-time Chat**: WebSocket-powered AI conversations
- **Multi-format Support**: PDF, DOCX, videos, images, and more

## Architecture

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

## Tech Stack

- **Frontend**: Vue 3 + Vite + TailwindCSS
- **Backend**: FastAPI + WebSockets
- **AI**: Groq API + ChromaDB + Whisper
- **Database**: SQLite + ChromaDB
- **Auth**: JWT + Google OAuth2
- **Deployment**: Docker + Nginx

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Google Drive API credentials
- Groq API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-drive
   ```

2. **Install dependencies**
   ```bash
   # Backend (Python)
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Frontend (Node.js)
   cd ../frontend
   npm install
   ```

3. **Configure environment**
   ```bash
   # Copy and edit environment file
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys (Google Drive, Groq)
   ```

4. **Start development servers**
   ```bash
   # From project root
   ./scripts/dev.sh

   # Or manually:
   # Terminal 1 - Backend
   cd backend && source venv/bin/activate && python run.py

   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Setup (Alternative)

```bash
# Build and run with Docker
docker-compose -f docker/docker-compose.yml up --build
```

## Configuration

### Environment Variables

```bash
# Google Drive OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AI API Keys
GROQ_API_KEY=your-groq-api-key

# Application
DEBUG=true
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./smart_drive.db
```

### Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins
6. Copy client ID and secret to `.env`

## Project Structure

```
smart-drive/
|-- backend/                          # FastAPI backend
|   |-- app/
|   |   |-- routers/                  # API routes
|   |   |-- services/                 # Business logic
|   |   |-- core/                     # Core utilities
|   |   |-- models/                   # Pydantic models
|   |   `-- utils/                    # Helper functions
|   |-- external/                     # Cloned repositories
|   |-- requirements.txt
|   `-- Dockerfile
|-- frontend/                         # Vue.js frontend
|   |-- src/
|   |   |-- components/               # Vue components
|   |   |-- views/                    # Page components
|   |   |-- stores/                   # Pinia stores
|   |   |-- composables/              # Vue composables
|   |   `-- utils/                    # Utilities
|   |-- package.json
|   `-- Dockerfile
|-- docker/                           # Docker configuration
|   |-- docker-compose.yml
|   |-- nginx.conf
|   `-- .env
|-- scripts/                          # Setup scripts
`-- docs/                             # Documentation
```

## Usage

### File Upload
1. Navigate to Files section
2. Drag & drop files or click to browse
3. Files are automatically processed and indexed

### AI Chat
1. Go to AI Chat section
2. Ask questions about your uploaded files
3. Get intelligent answers based on content
4. For videos: Ask timestamp-specific questions like "What happens at 1:30?"

### Google Drive Integration
1. Go to Settings
2. Click "Connect Google Drive"
3. Authorize the application
4. Your Drive files will be synced and searchable

## AI Features

- **Document Analysis**: Extract and understand text from PDFs, DOCX, TXT
- **Video Transcription**: Convert speech to text with timestamps
- **Semantic Search**: Find relevant content using vector similarity
- **Contextual Responses**: AI answers based only on your files
- **Multi-file Queries**: Analyze multiple files simultaneously

## Security

- JWT-based authentication
- Secure file upload validation
- API rate limiting
- HTTPS encryption in production
- Secure token storage

## Deployment

### Development
```bash
docker-compose -f docker/docker-compose.yml up --build
```

### Production
```bash
# Use production docker-compose
docker-compose -f docker/docker-compose.prod.yml up -d
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for Whisper and Chroma examples
- Google for Drive API samples
- LangChain community for tutorials
- Vue.js ecosystem for UI components
