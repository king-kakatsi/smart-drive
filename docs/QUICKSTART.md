# Quick Start Guide

Get Smart-Drive running in 5 minutes with Docker. This guide assumes you have Docker and Docker Compose installed.

## Prerequisites

- Docker & Docker Compose
- Git
- 5 minutes of your time

## Step 1: Clone and Navigate

```bash
git clone <repository-url>
cd smart-drive
```

## Step 2: Quick Setup

```bash
# One command setup (downloads everything)
make setup-quick

# Or manually:
curl -o .env https://raw.githubusercontent.com/your-repo/smart-drive/main/.env.example
```

## Step 3: Configure API Keys

Edit the `.env` file in the backend directory:

```bash
# Required: Get from https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here

# Optional: Get from Google Cloud Console
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Step 4: Launch Everything

```bash
# Start all services
make dev-quick

# Or with Docker:
docker-compose -f docker/docker-compose.yml up --build
```

## Step 5: Open Your Browser

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## That's It! You're Done.

## First Steps in Smart-Drive

### 1. Create an Account
- Click "Sign Up" on the login page
- Enter your details

### 2. Upload Your First File
- Go to "Files" section
- Drag & drop a PDF, DOCX, or TXT file
- Wait for processing (may take 1-2 minutes)

### 3. Ask Your First Question
- Navigate to "AI Chat"
- Type: "What are the main topics in this document?"
- Watch the AI analyze your file and respond

### 4. Try Video Analysis (Optional)
- Upload an MP4 video file
- Ask timestamp-specific questions like "What happens at 1:30?"

## Quick Commands Reference

```bash
# Start everything
make dev-quick

# Stop everything
make stop

# View logs
make logs

# Reset everything (fresh start)
make clean && make dev-quick

# Update code and restart
git pull && make restart
```

## Troubleshooting Quick Fixes

### Services Not Starting?
```bash
# Check if ports are free
docker-compose ps

# Kill conflicting processes
make stop

# Restart
make dev-quick
```

### AI Not Responding?
- Check your Groq API key is correct
- Wait 2-3 minutes for first request (model loading)
- Check logs: `make logs-backend`

### Files Not Uploading?
- Check file size (max 10MB default)
- Supported formats: PDF, DOCX, TXT, MP4, JPG, PNG
- Check logs: `make logs-backend`

## Next Steps

Now that you're running:

1. **Upload More Files**: Try different file types
2. **Connect Google Drive**: Sync your Drive files
3. **Explore Features**: Test video analysis, multi-file queries
4. **Customize Settings**: Adjust AI parameters in settings

## Detailed Setup

If the quick start doesn't work, see [INSTALLATION.md](./INSTALLATION.md) for detailed setup instructions.

## Need Help?

- Check the logs: `docker-compose logs`
- Common issues are covered in [INSTALLATION.md](./INSTALLATION.md#troubleshooting)
- API documentation: http://localhost:8000/docs

Happy exploring with Smart-Drive!
