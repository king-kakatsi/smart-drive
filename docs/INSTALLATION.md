# Installation Guide

Complete guide for setting up Smart-Drive on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python** 3.12 or higher ([Download](https://python.org/))
- **Node.js** 20.x or higher ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **Docker** & Docker Compose (recommended, [Download](https://docker.com/))

### Optional but Recommended

- **Visual Studio Code** with Python and Vue.js extensions
- **Git Bash** or similar terminal on Windows
- **Postman** or similar API testing tool

### Verify Prerequisites

```bash
# Check Python version
python --version  # Should be 3.12 or higher

# Check Node.js version
node --version   # Should be 20.x or higher

# Check npm version
npm --version    # Should be 9.x or higher

# Check Git
git --version    # Any recent version

# Check Docker (optional)
docker --version
docker-compose --version
```

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd smart-drive

# Verify the structure
ls -la
```

## Step 2: Backend Setup

### Python Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, chromadb, whisper; print('Backend dependencies installed successfully')"
```

### Backend Dependencies Explained

The `requirements.txt` includes:
- **FastAPI**: Web framework for the API
- **Uvicorn**: ASGI server for FastAPI
- **ChromaDB**: Vector database for embeddings
- **Whisper**: OpenAI's speech-to-text model
- **Groq**: AI API client
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **Python-multipart**: File upload handling

## Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Verify installation
npm list vue
npm list tailwindcss

# Check Vue CLI version
npx vue --version
```

### Frontend Dependencies Explained

The `package.json` includes:
- **Vue 3**: Progressive JavaScript framework
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Pinia**: State management for Vue
- **Vue Router**: Official router for Vue.js
- **Axios**: HTTP client for API calls

## Step 4: Environment Configuration

### Create Environment Files

```bash
# Backend environment file
cd ../backend
cp .env.example .env

# Frontend environment file (if needed)
cd ../frontend
cp .env.example .env  # If exists
```

### Essential Environment Variables

Edit `backend/.env`:

```bash
# Application Settings
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./smart_drive.db

# AI API Keys (Required)
GROQ_API_KEY=your-groq-api-key-here

# Google Drive Integration (Required for Drive features)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional Settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_FILE_SIZE=10000000  # 10MB in bytes
CHROMA_DB_PATH=./chroma_db
UPLOAD_DIR=./uploads
```

## Step 5: Get API Credentials

### Groq API Setup

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to `GROQ_API_KEY` in your `.env` file

### Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized origins: `http://localhost:5173` (frontend) and `http://localhost:8000` (backend)
   - Add authorized redirect URIs: `http://localhost:8000/auth/google/callback`
5. Copy Client ID and Client Secret to your `.env` file

## Step 6: Database Initialization

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Initialize database (if needed)
python -c "from app.database import init_db; init_db()"
```

## Step 7: Start Development Servers

### Option A: Using Make Commands (Recommended)

```bash
# From project root
cd ..

# Setup all dependencies
make setup

# Start development servers
make dev
```

### Option B: Manual Startup

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Option C: Docker Setup (Easiest)

```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up --build

# Or use the development compose file
docker-compose -f docker/docker-compose.dev.yml up --build
```

## Step 8: Verify Installation

### Check Backend

1. Open browser to `http://localhost:8000`
2. Should see FastAPI documentation page
3. Check `http://localhost:8000/docs` for interactive API docs
4. Check `http://localhost:8000/health` for health status

### Check Frontend

1. Open browser to `http://localhost:5173`
2. Should see Smart-Drive login page
3. Try basic navigation

### Test AI Features

1. Create an account or login
2. Upload a small text file
3. Try asking a question about the file
4. Check if AI responds (may take time for first request due to model loading)

## Troubleshooting

### Common Backend Issues

#### Python Virtual Environment Issues

**Error: `python` command not found**
```bash
# Use python3 instead
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

**Error: Permission denied on activation**
```bash
# Fix permissions
chmod +x venv/bin/activate
source venv/bin/activate
```

#### Dependency Installation Issues

**Error: Failed building wheel for some-package**
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Try installing with --no-cache-dir
pip install --no-cache-dir -r requirements.txt
```

**Error: Microsoft Visual C++ 14.0 required (Windows)**
- Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Or use `pip install --only-binary=all -r requirements.txt`

#### ChromaDB Issues

**Error: ChromaDB connection failed**
```bash
# Clear ChromaDB data
rm -rf backend/chroma_db

# Restart the backend
```

#### Whisper Model Issues

**Error: Model download failed**
```bash
# Pre-download models
python -c "import whisper; whisper.load_model('base')"
```

### Common Frontend Issues

#### Node.js Issues

**Error: npm install failed**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: Port 5173 already in use**
```bash
# Kill process using port 5173
npx kill-port 5173

# Or use different port
npm run dev -- --port 5174
```

#### Vue/Vite Issues

**Error: Vite dev server not starting**
```bash
# Clear Vite cache
rm -rf node_modules/.vite

# Restart dev server
npm run dev
```

### Common Docker Issues

#### Docker Build Issues

**Error: Build failed**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

**Error: Port already allocated**
```bash
# Stop conflicting containers
docker-compose down

# Or change ports in docker-compose.yml
```

#### Docker Compose Issues

**Error: Services not communicating**
```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

### API and Integration Issues

#### Google Drive API Issues

**Error: Invalid client**
- Double-check your Google Cloud Console credentials
- Ensure OAuth consent screen is configured
- Verify authorized origins and redirect URIs

**Error: Access denied**
- Check Google Drive API scopes
- Ensure user has granted necessary permissions

#### Groq API Issues

**Error: Invalid API key**
- Verify your Groq API key
- Check API key format (should start with 'gsk_')

**Error: Rate limit exceeded**
- Wait a few minutes before retrying
- Consider upgrading your Groq plan for higher limits

### Database Issues

#### SQLite Issues

**Error: Database locked**
```bash
# Close all connections to the database
# Restart the backend service
```

#### ChromaDB Issues

**Error: Collection not found**
```bash
# Reset ChromaDB
rm -rf backend/chroma_db
# Restart backend to recreate collections
```

### Network Issues

#### CORS Issues

**Error: CORS policy blocked**
- Check `ALLOWED_ORIGINS` in backend `.env`
- Ensure frontend URL is included
- Restart backend after changing CORS settings

#### WebSocket Issues

**Error: WebSocket connection failed**
- Check if backend WebSocket endpoint is running
- Verify firewall settings
- Check browser console for connection errors

## Development Tools Setup

### VS Code Extensions (Recommended)

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "Vue.volar",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint"
  ]
}
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Performance Optimization

### Backend Performance

```bash
# Use gunicorn for production
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Performance

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Verification Checklist

After installation, verify everything works:

- [ ] Backend starts without errors
- [ ] Frontend compiles successfully
- [ ] Database connections work
- [ ] API endpoints respond
- [ ] File upload works
- [ ] AI chat responds
- [ ] Google Drive integration works (optional)
- [ ] WebSocket connections work
- [ ] No console errors in browser

## Next Steps

After successful installation:

1. Read [QUICKSTART.md](./QUICKSTART.md) for a 5-minute getting started guide
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the codebase
3. Check [CONFIGURATION.md](./CONFIGURATION.md) for advanced settings
4. See [DEVELOPMENT.md](./DEVELOPMENT.md) for development workflow

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Search existing GitHub issues
3. Review Docker/container logs: `docker-compose logs`
4. Check backend logs in terminal
5. Verify environment variables are correct
6. Test API endpoints with curl/Postman
7. Contact the development team

## Additional Resources

- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Node.js Installation Guide](https://nodejs.org/en/download/)
- [Docker Getting Started](https://docs.docker.com/get-started/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Guide](https://vuejs.org/guide/introduction.html)
- [ChromaDB Documentation](https://docs.trychroma.com/)
